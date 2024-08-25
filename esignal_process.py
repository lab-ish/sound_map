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

import signal_process

#======================================================================
class ESignalProcess(signal_process.SignalProcess):
    # winsize: FFT windowサイズ
    # shift  : FFT windowをシフトするサイズ
    def __init__(self, data1, data2, samp_rate=48e3, winsize=512, shift=128,
                 mic_sep=0.5, avg_len=8):
        super(ESignalProcess, self).__init__(data1, data2, samp_rate, winsize, shift, mic_sep)

        # Enhanced sound mappingで平均化する長さ
        self.avg_len = avg_len

        # GCC結果の保存先
        self.gcc_results = np.zeros(self.winsize*(self.avg_len+1)).reshape((self.avg_len+1), -1)

        return

    #--------------------------------------------------
    def clear(self):
        # GCC結果の保存先をクリア
        self.gcc_results = np.zeros(self.winsize*(self.avg_len+1)).reshape((self.avg_len+1), -1)
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

        # GCC
        gcc = self.gcc(fft_data1, fft_data2).real
        # GCC結果を後ろに付け、1つ前にシフト
        self.gcc_results[self.avg_len,:] = gcc
        self.gcc_results[0:self.avg_len,:] = self.gcc_results[1:(self.avg_len+1),:]

        # 偶数番目（0, 2, 4, ...）を取り出して合計
        gcc_sum = self.gcc_results[np.arange(self.avg_len/2)*2,:].sum(axis=0)
        # 小さいものは破棄
        gcc_sum[(gcc_sum <= 0.1)] = 0

        # 全部ゼロのときは計算できないので破棄
        if (gcc_sum == 0).all():
            return -100

        # 最大となる位置を返す
        max_value = np.amax(gcc)
        return np.where(gcc == max_value)[0][0]
