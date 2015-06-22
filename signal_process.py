# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM AND A PART OF THIS PROGRAM.
#

import sys
import numpy as np

#======================================================================
class SignalProcess():
    #--------------------------------------------------
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
        if len(data1) % self.winsize != 0:
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
    def __call__(self):
        return

    #--------------------------------------------------
    def fft(self, data, offset=0):
        # FFT window
        win = np.hamming(self.winsize)
        # ウィンドウをかける
        win_data = win * (data[offset:offset+self.folds].reshape(1,-1)[0])
        # FFT
        fft_ret = np.fft.fft(win_data)
        return fft_ret

    #--------------------------------------------------
    def __del__(self):
        return
