# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM AND A PART OF THIS PROGRAM.
#

import sys
import wave
import struct
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

        self.__downsample()

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
        self.raw_data = sp.decimate(self.raw_data, factor, axis=1)
        self.sample_rate /= factor
        self.sample_timelen *= factor

        return

    #--------------------------------------------------
    def __del__(self):
        return
