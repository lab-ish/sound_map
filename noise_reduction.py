# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import numpy as np
import pandas as pd
from sklearn.externals import joblib
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression as LR

#======================================================================
class NoiseReduction():
    def __init__(self, data, div, samp_rate=48e3, n_comp=None, winsize=512, shift=512):
        self.winsize = winsize
        self.shift   = shift
        self.folds   = self.winsize / self.shift
        self.samp_rate = samp_rate
        self.div     = div              # 交差検定の分割数
        self.n_comp  = n_comp           # PCAの成分数

        # データの長さがシフトサイズの倍数でない場合には最後をカット
        self.data = data
        if len(data) % self.shift != 0:
            self.data = self.data[0:-(len(self.data) % self.shift)]
        # シフトサイズで折り返したテーブルを作成
        self.data = self.data.reshape(-1,self.shift)

        # 各FFT結果の時間幅
        self.fft_timebox = 1.0 * self.shift / self.samp_rate

        self.truth = None
        return

    #--------------------------------------------------
    def fft_all(self):
        end = self.data.shape[0]-self.folds
        # FFT結果の格納先
        self.fft_data = np.zeros(self.winsize/16*end).reshape(end,self.winsize/16)

        for offset in range(end):
            # データは折り返してあるので、必要行数を取り出してから1行に変換してFFT
            self.fft_data[offset,:] = self.fft(self.data[offset:offset+self.folds].reshape(1,-1)[0])

        return

    #--------------------------------------------------
    # Logistic regressionの学習
    #   真値ファイルをあらかじめ読み込んでおくこと
    def lr_train(self, train_idx, savefile=None):
        # 真値ファイルを読み込んでいない場合は学習不能
        if self.truth is None:
            return False
        # cross-validationのindex番号が範囲を超えているときは
        if train_idx >= self.div or train_idx < 0:
            return False

        # 学習データを抽出
        train_data, true_false = self.partial_get_data(train_idx)

        # LR学習
        self.lr = LR(C=1, solver='lbfgs', max_iter=100).fit(train_data, true_false)

        # 出力先が指定されているならばファイルに保存
        if savefile is not None:
            joblib.dump(self.lr, savefile)

        return True

    #--------------------------------------------------
    def partial_get_data(self, train_idx):
        # 真値を検定分割数で分割
        blk_size = int(np.round(1.0 * len(self.truth) / self.div))

        # 学習用データにする真値を切り出し
        #   最後の要素の場合は余っている部分全て
        true_data = None
        if train_idx == self.div - 1:
            true_data = self.truth[blk_size*train_idx:len(self.truth)]
        else:
            true_data = self.truth[blk_size*train_idx:blk_size*(train_idx+1)]

        if len(true_data) == 0:
            return [None, None]
        true_data = true_data.reset_index(drop=True)

        # 偽部分の開始位置と終端位置を計算
        false_data = np.zeros(2*(len(true_data)-1), 'int').reshape(-1,2)
        for cnt in range(len(true_data)-1):
            false_data[cnt,:] = np.array(self.false_idx(true_data.loc[cnt], true_data.loc[cnt+1]))
        false_data = false_data[false_data[:,0] != false_data[:,1],:]

        false_data = pd.DataFrame(false_data,
                                  columns=('start_idx', 'end_idx'),
                                  )

        # 学習データを切り出し
        #   真
        true_fft = self.extract_data(true_data)
        #   偽
        false_fft = self.extract_data(false_data)
        # 真偽データ
        true_false = np.append(np.ones(true_fft.shape[0], 'int8'),
                               np.zeros(false_fft.shape[0], 'int8'))
        return [np.r_[true_fft, false_fft], true_false]

    #--------------------------------------------------
    def extract_data(self, train_df):
        # 与えられたDataFrammeのstart_idx, end_idxで指定されたFFTデータを切り出し
        length = train_df.apply(
            lambda x: x.end_idx - x.start_idx,
            axis=1
            ).sum()
        fft_data = np.zeros(length*self.winsize/16).reshape(-1,self.winsize/16)
        idx = 0
        for cnt in range(len(train_df)):
            fft_data[idx:idx+train_df.loc[cnt].end_idx-train_df.loc[cnt].start_idx] = \
              self.fft_data[train_df.loc[cnt].start_idx:train_df.loc[cnt].end_idx,:]
            idx += train_df.loc[cnt].end_idx-train_df.loc[cnt].start_idx
        return fft_data

    #--------------------------------------------------
    def load_truth(self, truth_file, duration=2):
        # 車両通過情報の真値が格納されているファイル
        self.truth_file = truth_file

        # 真値を読み出し
        self.truth = pd.read_csv(truth_file,
                                 skiprows=1,
                                 delimiter='\t',
                                 header=None,
                                 names=('time', 'type', 'dir'),
                                 )

        # 時刻順に並べ替え
        self.truth = self.truth.sort_values('time').reset_index(drop=True)

        # 検出時刻の前後合計duration秒に車両音が含まれているとする
        self.truth['start_end'] = self.truth.time.apply(
            lambda x: self.true_idx(x, duration))
        self.truth['start_idx'] = self.truth.start_end.apply(lambda x: x[0])
        self.truth['end_idx']   = self.truth.start_end.apply(lambda x: x[1])
        self.truth = self.truth.drop('start_end', axis=1)
        return

    #--------------------------------------------------
    def true_idx(self, time, duration):
        center = time / self.fft_timebox
        dur    = duration/ 2 / self.fft_timebox
        start  = int(center - dur)
        end    = int(center + dur)
        if start < 0:
            start = 0
        return [start, end]

    #--------------------------------------------------
    def false_idx(self, prv, nxt, guard=1):
        # 間隔が短い場合は破棄
        if nxt.start_idx - prv.end_idx <= int(guard/self.fft_timebox) * 2:
            return [0, 0]
        start = prv.end_idx   + int(guard/self.fft_timebox)
        end   = nxt.start_idx - int(guard/self.fft_timebox)
        return [start, end]

    #--------------------------------------------------
    def pca_apply(self, data):
        # 単一データの場合は変換して渡す
        if len(data.shape) == 1:
            return self.pca.transform(data.reshape(1,-1))
        # そうでない場合はそのまま渡す
        return self.pca.transform(data)

    #--------------------------------------------------
    def pca_train(self, savefile=None):
        self.pca = PCA(n_components=self.n_comp)

        # PCA
        transformed = self.pca.fit_transform(self.fft_data)

        # 出力先が指定されているならばファイルに保存
        if savefile is not None:
            joblib.dump(self.pca, savefile)

        return transformed

    #--------------------------------------------------
    def pca_load(self, pca_file):
        self.pca = joblib.load(pca_file)
        self.n_comp = self.pca.n_components_
        return

    #--------------------------------------------------
    def lr_load(self, lr_file):
        self.lr = joblib.load(lr_file)
        return

    #--------------------------------------------------
    def fft(self, data):
        # FFT window
        win = np.hamming(self.winsize)

        # ウィンドウをかける
        win_data = win * data

        # FFT
        #   実信号の複素FFTでは後半の半分は折り返しなので捨てる
        #   （虚部がマイナスなだけで同じもの）
        fft_ret = np.fft.fft(win_data)[0:self.winsize/2]

        # 帯域の1/8のLPFをかけるので、後半を捨てる
        fft_ret = fft_ret[0:self.winsize/16]

        return np.abs(fft_ret)**2

    #--------------------------------------------------
    def __del__(self):
        return
