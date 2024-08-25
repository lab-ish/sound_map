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
import wave
import struct
import numpy as np
from scipy import signal as sp

#======================================================================
class WaveData():
    def __init__(self, datafile, decimate=4):
        # データファイル名を保存
        self.datafile = datafile

        # .wavを開く
        wav = wave.open(self.datafile, "rb")

        #----------
        # sampling rate
        self.sample_rate = wav.getframerate()
        self.sample_timelen = 1.0 / self.sample_rate

        # フレーム数
        nsample = wav.getnframes()

        # サンプルのサイズ
        sample_size = wav.getsampwidth()
        # チャネル数
        ch = wav.getnchannels()

        #----------
        # データ取得
        # データ長が24bitの場合だけは1サンプルずつ読んでpadding
        if sample_size == 3:
            data = ""
            for i in range(nsample):
                sample = wav.readframes(1)
                # 1サンプルはchannel数だけ含んでいるので、それぞれのchannelにpadding
                for c in range(0,ch*3,3):
                    data += "\x00" + sample[c:(c+3)]
        else:
            # 全データ読み出し
            data = wav.readframes(nsample)

        wav.close()

        #----------
        # データは文字列なのでintegerに変換する
        # unpack用文字列
        pack_str = '<{0}{1}'.format(nsample*ch, {1:'b',2:'h',3:'i',4:'i',8:'q'}[sample_size])
        # integerに変換
        self.raw_data = np.array(list(struct.unpack(pack_str, data)))

        # 24bitの場合に下1 byteを0にしたので元に戻す（符号付きで）
        if sample_size == 3:
            self.raw_data = self.raw_data >> 8

        #----------
        # ステレオデータの場合には折り返しておく: [0,:]=left, [1,:]=right
        self.raw_data = self.raw_data.reshape(-1,ch).transpose()

        if decimate:
            self.__downsample(decimate)

        if ch == 2:
            self.left  = self.raw_data[0]
            self.right = self.raw_data[1]
        else:
            self.left  = self.raw_data[0]
            self.right = self.left

        return

    #--------------------------------------------------
    # downsampling
    def __downsample(self, factor=4):
        if factor == 1:
            return
        self.raw_data = sp.decimate(self.raw_data, factor, axis=1)
        self.sample_rate /= factor
        self.sample_timelen *= factor

        return

    #--------------------------------------------------
    def __del__(self):
        return
