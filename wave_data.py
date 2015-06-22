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

#======================================================================
class WaveData():
    def __init__(self, datafile):
        # store data file name
        self.datafile = datafile

        # open .wav
        wav = wave.open(self.datafile, "rb")

        #----------
        # sampling rate
        self.sample_rate = wav.getframerate()
        self.sample_timelen = 1.0 / self.sample_rate

        #----------
        # data
        # retrieve whole data
        data = wav.readframes(wav.getnframes())
        # check sample size
        sys.stderr.write("Sample size: %d bytes\n" % wav.getsampwidth())
        # convert into integer
        self.raw_data = np.fromstring(data, dtype="int32")

        #----------
        # number of channels
        ch = wav.getnchannels()
        # use 2 columns for stereo data: [0,:]=left, [1,:]=right
        self.raw_data = self.raw_data.reshape(-1,ch).transpose()

        wav.close()
        return

    def __del__(self):
        return
