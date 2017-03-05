# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import os.path
import numpy as np
from matplotlib import pyplot as plt

import wave_data
import signal_process

#======================================================================
def single_plot(sig, offset, xrange=None, newfig=True):
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
    timebox = np.arange(-sig.winsize/2, sig.winsize/2) * 1e3 / data.sample_rate

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

    plt.plot(timebox, gcc,
             marker='',
             linestyle='-',
             )
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
    ap.add_argument("offset", type=int, action="store", nargs="*",
                    default=[0],
                    help="Set of offset values for plotting (default: 0)",
                    )
    return ap

#======================================================================
if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()

    # データ読み込み
    data = wave_data.WaveData(args.wavefile)

    # データ処理
    sig = signal_process.SignalProcess(data.left, data.right)

    if args.simul:
        single_plot(sig, args.offset[0], [-1.5, 1.5])
        for offset in args.offset[1:len(args.offset)]:
            single_plot(sig, offset, [-1.5, 1.5], False)
        # 出力ファイル名はbasename_simulを使う（拡張子を変更したものにする）
        plt.savefig(os.path.splitext(args.wavefile)[0] + '_simul.eps')
    else:
        for offset in args.offset:
            single_plot(sig, offset, [-1.5, 1.5])
            # 出力ファイル名はbasename+オフセットを使う（拡張子を変更したものにする）
            plt.savefig(os.path.splitext(args.wavefile)[0] + '_' + str(offset) + '.eps')
