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
import os
import numpy as np

import wave_data
import signal_process
import esignal_process

#======================================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python %s <wavefile> [soundmap_out]\n" % sys.argv[0])
        quit()

    # 引数処理
    wavefile = sys.argv[1]
    # sound mapデータの出力先のデフォルトはwaveファイルの拡張子を".dat"に変更したもの
    outname = os.path.splitext(wavefile)[0] + '_enhanced.dat'
    if len(sys.argv) >= 3:
        outname = sys.argv[2]

    # データ読み込み
    data = wave_data.WaveData(wavefile, False)

    # データ処理
    sig = signal_process.SignalProcess(data.left, data.right, data.sample_rate)
    esig = esignal_process.ESignalProcess(data.left, data.right, data.sample_rate)
    sound_map  = sig()
    esound_map = esig()

    # サウンドマップはindex番号になっているので時間差に変換
    sound_map_time  =  sound_map * 1e3 / data.sample_rate
    esound_map_time = esound_map * 1e3 / data.sample_rate

    # ファイルへの書き出し
    index = np.arange(0, len(sound_map))
    timebox = data.sample_timelen * sig.shift * index
    save_data = np.c_[index, timebox, sound_map, sound_map_time, esound_map, esound_map_time]
    print "Writing output to %s ..." % (outname)
    with open(outname, "w") as f:
        f.write("#index\ttime\tsound_delay\tsound_delay_time\tesound_delay\tesound_delay_time\n")
        np.savetxt(f, save_data,
                   fmt=["%d", "%g", "%d", "%g", "%d", "%g"],
                   delimiter="\t")

    del data
    del sig
    del esig
