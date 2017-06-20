# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import numpy as np
from sklearn.externals import joblib
from sklearn.decomposition import PCA

#======================================================================
class NoiseReduction():
    def __init__(self, data, winsize=512, shift=512, n_comp=25):
        self.winsize = winsize
        self.shift   = shift
        self.folds   = self.winsize / self.shift
        self.n_comp  = n_comp

        # データの長さがシフトサイズの倍数でない場合には最後をカット
        if len(data) % self.shift != 0:
            self.data = data[0:-(len(data) % self.shift)]
        # シフトサイズで折り返したテーブルを作成
        self.data = self.data.reshape(-1,self.shift)
        return

    #--------------------------------------------------
    def pca_apply(self, data):
        # 単一データの場合は変換して渡す
        if len(data.shape) == 1:
            return self.pca.transform(data.reshape(1,-1))
        # そうでない場合はそのまま渡す
        return self.pca.transform(data)

    #--------------------------------------------------
    def pca_load(self, pca_file):
        self.pca = joblib.load(pca_file)
        self.n_comp = self.pca.n_components_
        return

    #--------------------------------------------------
    def pca_train(self, data, savefile=None):
        self.pca = PCA(n_components=self.n_comp)
        end = self.data.shape[0]-self.folds
        # FFT結果の格納先
        self.fft_data = np.zeros(self.winsize/16*end).reshape(end,self.winsize/16)

        for offset in range(end):
            # データは折り返してあるので、必要行数を取り出してから1行に変換してFFT
            self.fft_data[offset,:] = self.fft(data[offset:offset+self.folds].reshape(1,-1)[0])

        # PCA
        transformed = self.pca.fit_transform(self.fft_data)

        # 出力先が指定されているならばファイルに保存
        if savefile is not None:
            joblib.dump(self.pca, savefile)
        return transformed

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
