# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2024, Shigemi ISHIDA
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the Institute nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

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
