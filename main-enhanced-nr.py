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

import true_data
import noise_reduction
import esignal_process_nr

#======================================================================
def arg_parser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("wavefile", type=str, action="store",
                        help="wave input file",
                        )
    parser.add_argument("-o", "--output", type=str, action="store",
                        dest="outfile",
                        nargs="?",
                        default=None,
                        help="soundmap output file",
                        )
    parser.add_argument("-p", "--pca_file", type=str, action="store",
                        dest="pca_file",
                        nargs="?",
                        default="pca.pkl",
                        help="pca input file",
                        )
    parser.add_argument("-l", "--lr_file", type=str, action="store",
                        dest="lr_file",
                        nargs="?",
                        default="lr.pkl",
                        help="logistic regression input file",
                        )
    return parser

#----------------------------------------------------------------------
if __name__ == '__main__':
    # 引数処理
    args = arg_parser().parse_args()

    # sound mapデータの出力先のデフォルトはwaveファイルの最後を'_enhanced_nr.dat'としたもの
    if args.outfile is None:
        args.outfile = os.path.splitext(args.wavefile)[0] + '_enhanced_nr.dat'

    # データ読み込み
    #   true_dataファイルのデフォルトはwaveファイルベース+'_truth.dat'
    base_name = os.path.splitext(args.wavefile)[0]
    base_dir  = os.path.dirname(base_name)
    true_file = base_name + '_truth.dat'
    data = true_data.TrueData(true_file, args.wavefile)

    # データ処理
    nr = noise_reduction.NoiseReduction(data, 6, 17)
    nr.pca_load(args.pca_file)
    nr.lr_load(args.lr_file)
    esign = esignal_process_nr.ESignalProcessNr(data.wav.left, data.wav.right, nr, data.samp_rate)
    esound_map_nr = esign()

    # サウンドマップはindex番号になっているので時間差に変換
    esound_map_time_nr = esound_map_nr * 1e3 / data.samp_rate

    # ファイルへの書き出し
    index = np.arange(len(esound_map_nr))
    timebox = 1.0 * index * esign.shift / data.samp_rate
    save_data = np.c_[index, timebox,
                      esound_map_nr, esound_map_time_nr]
    print "Writing output to %s" % (args.outfile)
    with open(args.outfile, "w") as f:
        f.write("#index\ttime\tesound_nr_delay\tesound_nr_delay_time\n")
        np.savetxt(f, save_data,
                   fmt=["%d", "%g", "%d", "%g"],
                   delimiter="\t")

    del data
    del esign
    del nr
