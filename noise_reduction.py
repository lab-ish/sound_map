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

        self._fft_flag = False          # FFTが完了しているかどうか
        return

    #--------------------------------------------------
    def fft_all(self):
        if self._fft_flag:
            return

        end = self.data.shape[0]-self.folds
        # FFT結果の格納先
        self.fft_data = np.zeros(self.winsize/16*end).reshape(end,self.winsize/16)

        for offset in range(end):
            # データは折り返してあるので、必要行数を取り出してから1行に変換してFFT
            self.fft_data[offset,:] = self.fft(self.data[offset:offset+self.folds].reshape(1,-1)[0])

        self._fft_flag = True
        return

    #--------------------------------------------------
    # 全データでcross-validation
    def cross_validation(self):
        self.fft_all()
        results = pd.DataFrame(columns=('tp', 'fn', 'fp', 'tn',
                                        'accuracy', 'precision', 'recall', 'f_measure',
                                        'train_len', 'test_len'))
        for cnt in range(self.div):
            results = results.append(
                pd.Series(self.pca_lr_test(cnt),
                          index=('tp', 'fn', 'fp', 'tn',
                                 'accuracy', 'precision', 'recall', 'f_measure',
                                 'train_len', 'test_len')),
                ignore_index=True)

        return results

    #--------------------------------------------------
    # cross-validationのindex番号を指定して評価
    def pca_lr_test(self, train_idx):
        # 真値ファイルを読み込んでいない場合は評価不能
        if self.truth is None:
            return False
        # cross-validationのindex番号が範囲を超えているときは評価不能
        if train_idx is not None and (train_idx >= self.div or train_idx < 0):
            return False

        idx = range(self.div)

        # 学習用のデータを抽出
        train_data, true_false, train_len = self.partial_get_data(idx.pop(train_idx))
        if not train_len:
            return False

        # PCAの主成分推定
        true_pca = self.pca_train(train_data[(true_false == 1),:])

        # LR学習用に非通過時のデータをPCA
        false_pca = self.pca_apply(train_data[(true_false == 0),:])

        # LR学習
        self.lr_train(np.r_[true_pca, false_pca],
                      true_false)

        # テストデータを連結
        test_data = np.empty([0, self.winsize/16])
        true_val  = np.empty(0, dtype='int8')
        test_len  = 0
        for cnt in idx:
            x = self.partial_get_data(cnt)
            if x[0] is not None:
                test_data = np.r_[test_data, x[0]]
                true_val  = np.append(true_val, x[1])
                test_len += x[2]

        test_pca = self.pca_apply(test_data)

        # Logistic regression
        #   左列: 推定値、右列: 真値
        results = np.c_[self.lr.predict(test_pca), true_val]
        # true positive, false negative, false positive, true negativeの数
        tp = len((results[:,0] & results[:,1] ==  1).nonzero()[0])  # 11
        fn = len((results[:,0] - results[:,1] == -1).nonzero()[0])  # 01
        fp = len((results[:,0] - results[:,1] ==  1).nonzero()[0])  # 10
        tn = len((results[:,0] | results[:,1] ==  0).nonzero()[0])  # 00

        # accuracy, precision, recall, f-measure
        accuracy  = 1.0*(tp+tn)/(tp+fp+fn+tn)
        precision = 1.0*tp/(tp+fp)
        recall    = 1.0*tp/(tp+fn)
        f_measure = 2.0*precision*recall/(precision+recall)

        return [tp, fn, fp, tn,
                accuracy, precision, recall, f_measure,
                train_len, test_len]

    #--------------------------------------------------
    # Logistic regressionの学習
    #   真値ファイルをあらかじめ読み込んでおくこと
    def lr_train(self, train_data, true_false, savefile=None):
        # LR学習
        self.lr = LR(C=1, solver='lbfgs', max_iter=100).fit(train_data, true_false)

        # 出力先が指定されているならばファイルに保存
        if savefile is not None:
            joblib.dump(self.lr, savefile)

        return True

    #--------------------------------------------------
    # データを分割し、train_idxで指定された部分のデータに関して
    # 車両通過時・非通過時のFFTデータと通過有無データを取得する
    def partial_get_data(self, train_idx):
        # 真値を検定分割数で分割
        blk_size = int(np.round(1.0 * len(self.truth) / self.div))

        # 対象の真値を切り出し
        #   最後の要素の場合は余っている部分全て
        true_data = None
        if train_idx is None:
          true_data = self.truth
        elif train_idx == self.div - 1:
            true_data = self.truth[blk_size*train_idx:len(self.truth)]
        else:
            true_data = self.truth[blk_size*train_idx:blk_size*(train_idx+1)]

        if len(true_data) == 0:
            return [None, None]
        true_data = true_data.reset_index(drop=True)

        # 車両非通過時のFFTデータ開始・終端位置を計算
        false_data = np.zeros(2*(len(true_data)-1), 'int').reshape(-1,2)
        for cnt in range(len(true_data)-1):
            false_data[cnt,:] = np.array(self.no_vehicle_idx(true_data.loc[cnt], true_data.loc[cnt+1]))
        false_data = false_data[false_data[:,0] != false_data[:,1],:]
        # データフレームに変換しておく
        false_data = pd.DataFrame(false_data,
                                  columns=('start_idx', 'end_idx'),
                                  )

        # FFTデータを切り出し
        # 通過時
        true_fft = self.ext_fft_data(true_data)
        # 非通過時
        false_fft = self.ext_fft_data(false_data)
        # 通過有無
        true_false = np.append(np.ones(true_fft.shape[0], 'int8'),
                               np.zeros(false_fft.shape[0], 'int8'))
        return [np.r_[true_fft, false_fft],
                true_false,
                true_data.time[len(true_data)-1] - true_data.time[0],
                ]

    #--------------------------------------------------
    def ext_fft_data(self, train_df):
        # 与えられたDataFrameのstart_idx, end_idxで指定された部分の
        # FFTデータを切り出し
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

        # 車両通過の開始・終端位置を計算（FFTデータのindex）
        # 検出時刻の前後合計duration秒に車両音が含まれているとする
        self.truth['start_end'] = self.truth.time.apply(
            lambda x: self.vehicle_idx(x, duration))
        self.truth['start_idx'] = self.truth.start_end.apply(lambda x: x[0])
        self.truth['end_idx']   = self.truth.start_end.apply(lambda x: x[1])
        self.truth = self.truth.drop('start_end', axis=1)
        return

    #--------------------------------------------------
    # 車両通過時のFFTデータの開始終端index（FFTデータの）
    def vehicle_idx(self, time, duration):
        center = time / self.fft_timebox
        dur    = duration/ 2 / self.fft_timebox
        start  = int(center - dur)
        end    = int(center + dur)
        if start < 0:
            start = 0
        return [start, end]

    #--------------------------------------------------
    # 非車両通過時のFFTデータの開始・終端index（FFTデータの）
    def no_vehicle_idx(self, prv, nxt, guard=4):
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
    def pca_train(self, train_data, savefile=None):
        # 学習
        self.pca = PCA(n_components=self.n_comp)
        transformed = self.pca.fit_transform(train_data)

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
