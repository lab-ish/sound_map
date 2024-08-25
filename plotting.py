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
import os.path
import numpy as np
from matplotlib import pyplot as plt

import wave_data
import signal_process

#======================================================================
def gcc_time(sig, offset, samp_rate):
    #------------------------------
    # gcc-phatを手動で呼ぶ
    fft_data1 = sig.fft(sig.data1, offset)
    fft_data2 = sig.fft(sig.data2, offset)
    # 帯域の1/8のLPF
    lowpass = np.append(np.append(np.ones(sig.winsize/16),
                                  np.zeros(sig.winsize-sig.winsize/8)),
                                  np.ones(sig.winsize/16))
    fft_data1 = lowpass * fft_data1
    fft_data2 = lowpass * fft_data2
    gcc = sig.gcc(fft_data1, fft_data2)
    # 後半部分を折り返しておく
    gcc_minus = np.array(gcc[sig.winsize/2:len(gcc)])
    gcc[sig.winsize/2:len(gcc)] = np.array(gcc[0:sig.winsize/2])
    gcc[0:sig.winsize/2] = gcc_minus
    gcc = np.real(gcc)

    # gccの横軸はindex番号になっているので時刻を計算しておく
    timebox = np.arange(-sig.winsize/2, sig.winsize/2) * 1e3 / samp_rate

    return (gcc, timebox)

#--------------------------------------------------
def single_plot(gcc, timebox, xrange=None, yrange=None, newfig=True, label=None):
    # plot
    # プロットの調整
    plt.rcParams['font.family'] = 'Times New Roman' # 全体のフォント
    plt.rcParams['font.size'] = 22                  # フォントサイズ
    plt.rcParams['axes.linewidth'] = 1              # 軸の太さ
    # EPS出力のためのおまじない
    plt.rcParams['ps.useafm'] = True
    plt.rcParams['pdf.use14corefonts'] = True
    plt.rcParams['text.usetex'] = True

    if newfig:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # 図全体の背景を透明に
        fig.patch.set_alpha(0)
        # subplotの背景を透明に
        ax.patch.set_alpha(0)
        fig.subplots_adjust(left=0.15, bottom=0.15)     # 左と下の余白を増やす
        plt.xlabel("Sound delay [ms]")
        plt.ylabel("GCC")

    if xrange is not None:
        plt.xlim(xrange)
    if yrange is not None:
        plt.ylim(yrange)

    if label is not None:
        plt.plot(timebox, gcc,
                marker='',
                linestyle='-',
                label=label,
                )
    else:
        plt.plot(timebox, gcc,
                marker='',
                linestyle='-',
                )
    plt.legend(loc="upper right", fontsize=20)
    return

#----------------------------------------------------------------------
# 引数処理
def arg_parser():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("wavefile", type=str, action="store",
                    help="wavefile",
                    )
    ap.add_argument("-s", "--simul", action="store_true",
                    help="Plot on the same plot",
                    )
    ap.add_argument("-a", "--add", action="store_true",
                    help="Sum up GCC results",
                    )
    ap.add_argument("-y", "--yrange", type=str, action="store",
                    default=None,
                    help="Specify plot yrange such as \"[-0.10,0.20]\"",
                    )
    ap.add_argument("-l", "--labels", type=str, action="store",
                    default=None,
                    help="Specify labels for each line such as \"[10 sec,20 sec]\"",
                    )
    ap.add_argument("offset", type=int, action="store", nargs="*",
                    default=[0],
                    help="Set of offset values for plotting (default: 0)",
                    )
    return ap

#======================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()
    if args.yrange is not None:
        args.yrange = args.yrange.replace(" ", "").replace("[", "").replace("]", "").split(',')
        args.yrange = map(float, args.yrange)
    if args.labels is not None:
        args.labels = args.labels.replace("[", "").replace("]", "").split(',')
    else:
        args.labels = [None] * len(args.offset)

    # データ読み込み
    data = wave_data.WaveData(args.wavefile, False)

    # データ処理
    sig = signal_process.SignalProcess(data.left, data.right)

    # offsetの範囲をチェック
    if (args.offset[0] > sig.data1.shape[0] - sig.folds):
        sys.stderr.write("Error: offset over range.\n")
        quit()

    if args.simul:
        gcc, timebox = gcc_time(sig, args.offset[0], data.sample_rate)
        single_plot(gcc, timebox, [-1.5, 1.5], args.yrange, True, args.labels[0])
        for cnt in range(1,len(args.offset)):
            offset = args.offset[cnt]
            gcc, timebox = gcc_time(sig, offset, data.sample_rate)
            single_plot(gcc, timebox, [-1.5, 1.5], args.yrange, False, args.labels[cnt])
        # 出力ファイル名はbasename_simulを使う
        plt.savefig(os.path.splitext(args.wavefile)[0] + '_simul.eps')
        plt.close()

    if args.add:
        gcc_sum, timebox = gcc_time(sig, args.offset[0], data.sample_rate)
        for cnt in range(1,len(args.offset)):
            offset = args.offset[cnt]
            gcc, timebox = gcc_time(sig, offset, data.sample_rate)
            gcc_sum += gcc
        single_plot(gcc_sum, timebox, [-1.5, 1.5], args.yrange, True, args.labels[0])
        # 出力ファイル名はbasename_sumを使う
        plt.savefig(os.path.splitext(args.wavefile)[0] + '_sum.eps')
        plt.close()

    if not (args.simul or args.add):
        for cnt in range(len(args.offset)):
            offset = args.offset[cnt]
            gcc, timebox = gcc_time(sig, offset, data.sample_rate)
            single_plot(gcc, timebox, [-1.5, 1.5], args.yrange, True, args.labels[cnt])
            # 出力ファイル名はbasename+オフセットを使う
            plt.savefig(os.path.splitext(args.wavefile)[0] + '_' + str(offset) + '.eps')
            plt.close()
