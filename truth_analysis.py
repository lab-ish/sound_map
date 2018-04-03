# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import pandas as pd
import numpy as np

#======================================================================
class TruthData():
    def __init__(self, truth_file):
        self.infile = truth_file
        # データファイルの読み込み
        self.data = pd.read_csv(self.infile, sep="\t")
        return

    #--------------------------------------------------
    def num_simul(self):
        # 通過時刻を並べ替えた上で差分を取る
        #   通過時刻は1列目
        self.diff = np.diff(np.sort(self.data.iloc[:,0]))

        # diffが2以下のやつのindex番号を取得
        idx = (self.diff <= 2).nonzero()[0]
        # index番号の差が1以下の個数（連続して並んでいる個数）
        d = np.diff(idx)
        num_successive = len(d[d == 1])

        # 最終的な連続通過台数は、2以下のdiffの個数*2 - 連続して並んでいる個数
        self.num_simul = len(idx) * 2 - num_successive

        return self.num_simul

#======================================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python %s <truth_data_file>\n" % sys.argv[0])
        quit()

    t = TruthData(sys.argv[1])
    print t.num_simul()
