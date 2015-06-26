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
class SignalProcess():
    # winsize: FFT windowサイズ
    # shift  : FFT windowをシフトするサイズ
    def __init__(self, data1, data2, winsize=1024, shift=256):
        # シフトサイズの倍数がFFT windowサイズであるかチェック
        if winsize % shift != 0:
            sys.stderr.write("Invalid shift size: window size is a multiple of shift size.\n")
            raise ValueError
        self.winsize = winsize
        self.shift   = shift
        self.folds   = self.winsize / self.shift

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
        return sound_map

    #--------------------------------------------------
    def gcc_phat(self, offset):
        fft_data1 = self.fft(self.data1, offset)
        fft_data2 = self.fft(self.data2, offset)

        # GCC
        gcc = self.gcc(fft_data1, fft_data2)

        # # 帯域を制限するマスクをかける
        # mask = np.zeros(self.winsize, dtype='int8')
        # mask[(512-86):(512+86)] = 1
        # gcc *= mask

        # 絶対値が最大になるところを探す
        #   最大になる点が2点以上ある場合は最初のもの
        gcc = abs(gcc)
        max_idx = np.where(gcc == max(gcc))[0][0]

        return max_idx

    #--------------------------------------------------
    def gcc(self, fdata1, fdata2):
        ret = fdata1 * np.conj(fdata2)
        ret /= abs(ret)
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
