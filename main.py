# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM AND A PART OF THIS PROGRAM.
#

import sys

import wave_data
import signal_process

#======================================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python %s <wavefile>\n" % sys.argv[0])
        quit()

    # データ読み込み
    wavefile = sys.argv[1]
    data = wave_data.WaveData(wavefile)

    # データ処理
    sig = signal_process.SignalProcess(data.raw_data[0], data.raw_data[1])

    del data
