# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import numpy as np

#======================================================================
class SignalProcess():
    # winsize: FFT windowサイズ
    # shift  : FFT windowをシフトするサイズ
    def __init__(self, data1, data2, winsize=512, shift=128):
        # シフトサイズの倍数がFFT windowサイズであるかチェック
        if winsize % shift != 0:
            sys.stderr.write("Invalid shift size: window size is a multiple of shift size.\n")
            raise ValueError
        self.winsize = winsize
        self.shift   = shift
        self.folds   = self.winsize / self.shift

        # データの長さは一致する？
        if len(data1) != len(data2):
            sys.stderr.write("Data length not match.\n")
            raise ValueError

        # データを格納
        #   長さがシフトサイズの倍数でない場合には最後をカット
        if len(data1) % self.shift != 0:
            self.data1 = data1[0:-(len(data1) % self.shift)]
            self.data2 = data2[0:-(len(data2) % self.shift)]
        else:
            self.data1 = data1
            self.data2 = data2

        # シフトサイズで折り返したテーブルを作成
        self.data1 = self.data1.reshape(-1,self.shift)
        self.data2 = self.data2.reshape(-1,self.shift)

        return

    #--------------------------------------------------
    def __call__(self, end=None):
        if end is None:
            end = self.data1.shape[0]-self.folds
        if end > self.data1.shape[0]-self.folds:
            end = self.data1.shape[0]-self.folds

        sound_map = np.array([self.gcc_phat(offset) for offset in range(0,end)])
        return sound_map

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
        gcc = self.gcc(fft_data1, fft_data2)

        # # 帯域を制限するマスクをかける
        # mask = np.zeros(self.winsize, dtype='int8')
        # mask[(512-86):(512+86)] = 1
        # gcc *= mask

        delay_result = []
        gcc = abs(gcc)
        if np.amax(gcc) >= 0.06:
            max_value = np.amax(gcc)
            delay = np.where(gcc == max_value)[0][0]
            if delay >= self.winsize/2:
                delay -= self.winsize-1
            #マイク幅50cmの場合の有効値
            if delay > 71 or delay < -71:
                 delay = -100
            delay_result.append(delay)
        else :
        # GCCが閾値以上でない場合は破棄
            delay_result.append(-100)

        return delay_result

    #--------------------------------------------------
    def gcc(self, fdata1, fdata2):
        ret = fdata1 * np.conj(fdata2)
        # 0で割るとエラーになるので小さい値を足しておく
        ret /= (abs(ret)+1e-6)

        return np.fft.ifft(ret)

    #--------------------------------------------------
    def fft(self, data, offset=0):
        # FFT window
        win = np.hamming(self.winsize)

        # ウィンドウをかける
        #   データは折り返してあるので、必要行数を取り出してから1行に変換する
        win_data = win * (data[offset:offset+self.folds].reshape(1,-1)[0])

        # FFT
        fft_ret = np.fft.fft(win_data)
        return fft_ret

    #--------------------------------------------------
    def count(self, soundmap):
        state = 0
        hit_count = 0
        miss_count = 0
        num_count = 0
        start = 0
        temp = 0
        prev_pos = 0
        now_pos = 0
        through = 0
        THRESHOLD_VER = 10
        THRESHOLD_HORI = 20

        for i in range(1,len(soundmap)-1):
            if soundmap[i] == -100:
                through += 1
                continue
            else:
                prev_pos = now_pos
                now_pos = i
            if state == 0:
                if abs(soundmap[now_pos] - soundmap[prev_pos]) <= THRESHOLD_VER:
                    start = now_pos
                    hit_count += 1
                    state = 1
            elif state == 1:
                if abs(soundmap[now_pos] - soundmap[prev_pos]) <= THRESHOLD_VER:
                    hit_count += 1
                else:
                    miss_count += 1
                    state = 2
                    temp = soundmap[prev_pos]
            elif state == 2:
                if abs(soundmap[now_pos] - temp) <= THRESHOLD_VER:
                   hit_count += 1
                   miss_count = 0
                   state = 1
                else:
                    miss_count += 1

                if miss_count >=THRESHOLD_HORI:
                    if hit_count >= 100 and (soundmap[start] * temp) < 0:
                        print "○○○○○○○○○○○○"
                        print str(start) + "to" + str(prev_pos)
                        print str(start * (1.0/375.0))+ "秒" + "to" + str(prev_pos * (1.0/375.0)) + "秒"
                        print str(((start + prev_pos)/2.0) * (1.0/375.0)) + "秒"
                        print "○○○○○○○○○○○○"
                        num_count += 1
                    # else :
                    #      print "××××××××××××"
                    #      print hit_count
                    #      print soundmap[start]
                    #      print temp
                    #      print str(start) + "to" + str(prev_pos)
                    #      print str(((start + prev_pos)/2.0) * (1.0/375.0)) + "秒"
                    #      print "××××××××××××"
                    state = 0
                    hit_count = 0
                    miss_count = 0
            through = 0

        if hit_count >= 100 and (soundmap[start] * temp) < 0:
            print str(start) + "to" + str(prev_pos)
            print str(start * (1.0/375.0))+ "秒" + "to" + str(prev_pos * (1.0/375.0)) + "秒"
            print str(((start + prev_pos)/2.0) * (1.0/375.0)) + "秒"
            num_count += 1

        print "台数" + str(num_count)
        return



    #--------------------------------------------------
    def __del__(self):
        return
