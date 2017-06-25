# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import pandas as pd
import numpy as np

import wave_data

#======================================================================
class TrueData():
    def __init__(self, true_file, wav_file, winsize=512, shift=512, pass_dur=2, guard_dur=4):
        # 車両通過情報の真値が格納されているファイル
        self.true_file = true_file
        # 車両音声のwavファイル
        self.wav_file = wav_file
        # FFTパラメータ
        self.winsize = winsize
        self.shift   = shift
        self.folds   = self.winsize / self.shift

        # 音声データを開く
        self.wav = wave_data.WaveData(self.wav_file, False)
        # サンプリングレート
        self.samp_rate = self.wav.sample_rate

        # 各FFT結果の時間幅
        self.fft_timebox = 1.0 * self.shift / self.samp_rate

        # 車両の通過にかかる時間
        self.pass_dur = pass_dur
        # 非車両通過時の音を抽出する際の車両の通過時間からのガード時間
        self.guard_dur = guard_dur

        # 車両通過真値データを開く
        self.load_truth(true_file)
        
        # データは左チャネル
        #   データの長さがシフトサイズの倍数でない場合には最後をカット
        self.data = np.array(self.wav.left)
        if len(self.data) % self.shift != 0:
            self.data = self.data[0:-(len(self.data) % self.shift)]
        # シフトサイズで折り返したテーブルを作成
        self.data = self.data.reshape(-1,self.shift)

        # FFT
        self.fft_all()

        return

    #--------------------------------------------------
    def load_truth(self, t_file):

        # 真値を読み出し
        self.truth = pd.read_csv(t_file,
                                 skiprows=1,
                                 delimiter='\t',
                                 header=None,
                                 names=('time', 'type', 'dir'),
                                 )

        # 時刻順に並べ替え
        self.truth = self.truth.sort_values('time').reset_index(drop=True)

        # 車両通過の開始・終端位置を計算（FFTデータのindex）
        # 検出時刻の前後合計self.pass_dur秒に車両音が含まれているとする
        self.truth['start_end'] = self.truth.time.apply(
            lambda x: self.vehicle_idx(x, self.pass_dur))
        self.truth['start_idx'] = self.truth.start_end.apply(lambda x: x[0])
        self.truth['end_idx']   = self.truth.start_end.apply(lambda x: x[1])
        self.truth = self.truth.drop('start_end', axis=1)
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
    # データを分割し、train_idxで指定された部分のデータに関して
    # 車両通過時・非通過時のFFTデータと通過有無データを取得する
    def get_partial_data(self, train_idx, div):
        # 真値を検定分割数で分割
        blk_size = int(np.round(1.0 * len(self.truth) / div))

        # 対象の真値を切り出し
        #   最後の要素の場合は余っている部分全て
        true_data = None
        if train_idx is None:
          true_data = self.truth
        elif train_idx == div - 1:
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
    def no_vehicle_idx(self, prv, nxt):
        # 間隔が短い場合は破棄
        if nxt.start_idx - prv.end_idx <= int(self.guard_dur/self.fft_timebox) * 2:
            return [0, 0]
        start = prv.end_idx   + int(self.guard_dur/self.fft_timebox)
        end   = nxt.start_idx - int(self.guard_dur/self.fft_timebox)
        return [start, end]

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
