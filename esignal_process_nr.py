# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2017, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import numpy as np

import esignal_process

#======================================================================
class ESignalProcessNr(esignal_process.ESignalProcess):
    def __init__(self, data1, data2, noise_reduce=None, samp_rate=48e3, winsize=512, shift=128,
                 mic_sep=0.5, avg_len=8):
        super(ESignalProcessNr, self).__init__(data1, data2, samp_rate, winsize, shift,
                                               mic_sep, avg_len)

        # ノイズ低減用NoiseReductionオブジェクト
        self.nr = noise_reduce

        return

    #--------------------------------------------------
    def gcc_phat(self, offset):
        fft_data1 = self.fft(self.data1, offset)
        fft_data2 = self.fft(self.data2, offset)

        # 帯域の1/8のLPFをかける
        lowpass = np.append(np.append(np.ones(self.winsize/16),
                                      np.zeros(self.winsize-self.winsize/8)),
                                      np.ones(self.winsize/16))
        fft_data1 = lowpass * fft_data1
        fft_data2 = lowpass * fft_data2

        #------------------------------
        # PCA + Logistic regression
        # テストするデータは1/8帯域の部分だけを投入する
        # PCA
        test_pca = self.nr.pca_apply(np.abs(fft_data1[0:self.winsize/16]))
        # LR
        lr = self.nr.lr.predict(test_pca)

        # LRの結果、車両なしであれば破棄
        if lr == 0:
            return -100

        # GCC
        gcc = self.gcc(fft_data1, fft_data2)
        gcc = abs(gcc)
        max_value = np.amax(gcc)
        if max_value >= 0.06:
            return np.where(gcc == max_value)[0][0]
        else :
        # GCCが閾値以上でない場合は破棄
            return -100
