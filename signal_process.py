# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import numpy as np

#======================================================================
class SignalProcess(object):
    # winsize: FFT windowサイズ
    # shift  : FFT windowをシフトするサイズ
    def __init__(self, data1, data2, samp_rate=48e3, winsize=512, shift=128, mic_sep=0.5):
        # シフトサイズの倍数がFFT windowサイズであるかチェック
        if winsize % shift != 0:
            sys.stderr.write("Invalid shift size: window size is not a multiple of shift size.\n")
            raise ValueError
        self.winsize = winsize
        self.shift   = shift
        self.folds   = int(self.winsize / self.shift)
        # 有効なsound mapの範囲（音速340m/sとする）
        self.max_delay = int(np.ceil(mic_sep * samp_rate / 340.0)) + 5

        # データの長さは一致する？
        if len(data1) != len(data2):
            sys.stderr.write("Data length not match.\n")
            raise ValueError

        # データを格納
        #   長さがシフトサイズの倍数でない場合には最後をカット
        if len(data1) % self.shift != 0:
            self.data1 = data1[0:-(len(data1) % self.shift)]
            self.data2 = data2[0:-(len(data2) % self.shift)]
        else:
            self.data1 = data1
            self.data2 = data2

        # シフトサイズで折り返したテーブルを作成
        self.data1 = self.data1.reshape(-1,self.shift)
        self.data2 = self.data2.reshape(-1,self.shift)

        return

    #--------------------------------------------------
    def __call__(self, end=None):
        if end is None:
            end = self.data1.shape[0]-self.folds
        if end > self.data1.shape[0]-self.folds:
            end = self.data1.shape[0]-self.folds

        sound_map = np.array([self.gcc_phat(offset) for offset in range(0,end)])

        # 真ん中より先は折り返してマイナスとする
        #   例: 1024点の場合のindex変換
        #      元: 0 1 2 3 ... 510 511  512  513 ... 1022 1023
        #      ↓
        #      後: 0 1 2 3 ... 510 511 -512 -511 ...   -2   -1
        sound_map[(sound_map >= self.winsize/2)] -= self.winsize

        #マイク幅に鑑みて有効値以外は捨てる
        sound_map[(abs(sound_map) > self.max_delay)] = -100

        return sound_map

    #--------------------------------------------------
    def gcc_phat(self, offset):
        fft_data1 = self.fft(self.data1, offset)
        fft_data2 = self.fft(self.data2, offset)

        # 帯域の1/8のLPFをかける
        lowpass = np.append(np.append(np.ones(int(self.winsize/16)),
                                      np.zeros(self.winsize-int(self.winsize/8))),
                                      np.ones(int(self.winsize/16)))
        fft_data1 = lowpass * fft_data1
        fft_data2 = lowpass * fft_data2

        # GCC
        gcc = self.gcc(fft_data1, fft_data2)
        gcc = abs(gcc)
        max_value = np.amax(gcc)
        if max_value >= 0.06:
            return np.where(gcc == max_value)[0][0]
        else :
        # GCCが閾値以上でない場合は破棄
            return -100

    #--------------------------------------------------
    def gcc(self, fdata1, fdata2):
        ret = fdata1 * np.conj(fdata2)
        # 0で割るとエラーになるので小さい値を足しておく
        ret /= (abs(ret)+1e-6)

        return np.fft.ifft(ret)

    #--------------------------------------------------
    def fft(self, data, offset=0):
        # FFT window
        win = np.hamming(self.winsize)

        # ウィンドウをかける
        #   データは折り返してあるので、必要行数を取り出してから1行に変換する
        win_data = win * (data[offset:offset+self.folds].reshape(1,-1)[0])

        # FFT
        fft_ret = np.fft.fft(win_data)
        return fft_ret

    #--------------------------------------------------
    def __del__(self):
        return
