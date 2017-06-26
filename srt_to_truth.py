# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM NOR A PART OF THIS PROGRAM.
#

import sys
import datetime
import pandas as pd
from itertools import groupby

#======================================================================
class SubRip():
    UTF8_BOM = bytearray([0xEF, 0XBB, 0XBF])

    def __init__(self, infile):
        self.infile = infile
        return

    #--------------------------------------------------
    def load(self):
        # open srt file
        with open(self.infile) as f:
            # read each group into a list
            self.srt_raw = [list(g) for b,g in groupby(f,
                                                       lambda x: bool(x.strip())) if b]
            # remove BOM if exists
            self.srt_raw[0][0] = self.__strip_bom(self.srt_raw[0][0])
        self.__parse()

    #--------------------------------------------------
    def __parse(self):
        self.subs = []

        for sub in self.srt_raw:
            # skip invalid entries
            if len(sub) < 3:
                continue

            # extract subtitle info
            sub = [x.strip() for x in sub]
            try:
                num     = int(sub[0])
            except:
                print "Invalid sub format %s\n%s\n%s" % (sub[0], sub[1], sub[2])
                return False
            st_end  = sub[1]
            content = sub[2:len(sub)]
            # retrieve start and end
            [start, end] = st_end.split(' --> ')
            start = datetime.datetime.strptime(start, '%H:%M:%S,%f')
            end   = datetime.datetime.strptime(end, '%H:%M:%S,%f')

            # store
            self.subs.append([num, start, end, content])
        return True

    #--------------------------------------------------
    def __strip_bom(self, s):
        if s.startswith(SubRip.UTF8_BOM):
            return s[len(SubRip.UTF8_BOM):]
        return s

    #--------------------------------------------------
    def renumber(self):
        for i in range(len(self.subs)):
            self.subs[i][0] = i + 1
        return

#======================================================================
if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: python %s <truth_output> <input_srt>\n" % sys.argv[0])
        quit()

    # 引数処理
    outfile = sys.argv[1]
    infile  = sys.argv[2]

    # 字幕ファイルを読み込み
    srt = SubRip(infile)
    srt.load()

    # DataFrameに変換
    df = pd.DataFrame(srt.subs, columns=('sub_num', 'start', 'end', 'type_raw'))
    df = df.drop('sub_num', axis=1)

    # 重なるタイミングで字幕を付けると2回現れるので、最初の1つだけを見るようにする
    df['type_raw'] = df.type_raw.apply(lambda x: x[0])

    # 方向とタイプを分離
    df['dir']  = df.type_raw.apply(lambda x: x.split(' ')[0])
    df['type'] = df.type_raw.apply(lambda x: ' '.join(x.split(' ')[1:len(x.split(' '))]))

    # 自転車は削除
    df = df[(df.type != 'bicycle')]

    # 通過時刻を作成
    df['time'] = df.start.apply(lambda x: (x - datetime.datetime(1900,1,1)).total_seconds())

    # 書き出し
    with open(outfile, 'w') as f:
        f.write("#")
        df[['time', 'type', 'dir']].to_csv(f,
                                           sep='\t',
                                           index=False,
                                           mode='a',
                                           )
