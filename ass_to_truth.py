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
import datetime
import pandas as pd
from itertools import groupby

#======================================================================
class AegiSubs():
    UTF8_BOM = bytearray([0xEF, 0XBB, 0XBF])

    def __init__(self, infile):
        self.infile = infile
        return

    #--------------------------------------------------
    def load(self):
        # open srt file
        with open(self.infile) as f:
            # read each group into a list
            self.sub_raw = [list(g) for b,g in groupby(f,
                                                       lambda x: bool(x.strip())) if b]
            # remove BOM if exists
            self.sub_raw[0][0] = self.__strip_bom(self.sub_raw[0][0])
        # lookup subs
        for sub_set in self.sub_raw:
            if sub_set[0].strip() == '[Events]':
                self.sub_raw = [x.strip() for x in sub_set[1:len(sub_set)]]
                self.sub_raw = filter(lambda x: x.split(":")[0] == 'Dialogue', self.sub_raw)
                return True
        return False

    #--------------------------------------------------
    def parse(self):
        # remove "Dialogue: "
        self.sub_raw = [x.split(": ")[1].split(",") for x in self.sub_raw]

        self.subs = []

        for sub in self.sub_raw:
            # extract subtitle info
            #   0,0:04:22.85,0:04:23.64,Default,,0,0,0,,R2L normal
            start   = datetime.datetime.strptime(sub[1], '%H:%M:%S.%f')
            end     = datetime.datetime.strptime(sub[2], '%H:%M:%S.%f')
            content = sub[9]
            # store
            self.subs.append([start, end, content])
        return True

    #--------------------------------------------------
    def __strip_bom(self, s):
        if s.startswith(AegiSubs.UTF8_BOM):
            return s[len(AegiSubs.UTF8_BOM):]
        return s

    #--------------------------------------------------
    def renumber(self):
        for i in range(len(self.subs)):
            self.subs[i][0] = i + 1
        return

#======================================================================
if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: python %s <truth_output> <input_ass>\n" % sys.argv[0])
        quit()

    # 引数処理
    outfile = sys.argv[1]
    infile  = sys.argv[2]

    # 字幕ファイルを読み込み
    sub = AegiSubs(infile)
    sub.load()
    sub.parse()

    # DataFrameに変換
    df = pd.DataFrame(sub.subs, columns=('start', 'end', 'type_raw'))

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
