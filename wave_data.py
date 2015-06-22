# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM AND A PART OF THIS PROGRAM.
#

import sys
import wave
import numpy as np
from scipy import signal as sp

#======================================================================
class WaveData():
    def __init__(self, datafile):
        # データファイル名を保存
        self.datafile = datafile

        # .wavを開く
        wav = wave.open(self.datafile, "rb")

        #----------
        # sampling rate
        self.sample_rate = wav.getframerate()
        self.sample_timelen = 1.0 / self.sample_rate

        #----------
        # データ
        # 全データ読み出し
        data = wav.readframes(wav.getnframes())
        # # サンプルのサイズを念のため見ておく
        # sys.stderr.write("Sample size: %d bytes\n" % wav.getsampwidth())

        # integerに変換、サイズに注意
        self.raw_data = np.fromstring(data, dtype="int32")

        #----------
        # チャネル数
        ch = wav.getnchannels()
        # ステレオデータの場合には折り返しておく: [0,:]=left, [1,:]=right
        self.raw_data = self.raw_data.reshape(-1,ch).transpose()

        self.__downsample()

        if ch == 2:
            self.left  = self.raw_data[0]
            self.right = self.raw_data[1]
        else:
            self.left  = self.raw_data[0]
            self.right = self.left

        wav.close()
        return

    #--------------------------------------------------
    # downsampling
    def __downsample(self, factor=4):
        self.raw_data = sp.decimate(self.raw_data, factor, axis=1)
        self.sample_rate /= factor
        self.sample_timelen *= factor

        return

    #--------------------------------------------------
    def __del__(self):
        return
