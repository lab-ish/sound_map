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
import pandas as pd
import numpy as np
from argparse import ArgumentParser

#======================================================================
def arg_parser():
    usage = 'python {} [-o <save_file>] [-s] [--help] <datafile1> [datafile2] ...'\
            .format(__file__)
    ap = ArgumentParser(usage=usage)
    ap.add_argument('-o', type=str,
                    nargs='?',
                    dest='save_file',
                    help='output file name')
    ap.add_argument('-s',
                    dest='simul',
                    action='store_true',
                    help='analyze simultaneous passing')
    ap.add_argument('datafiles', type=str,
                    nargs='*',
                    help='input file names')
    return ap

#----------------------------------------------------------------------
def extract_simultaneous(dframe):
    dframe = dframe.sort_values('time').reset_index(drop=True)
    dframe['time_diff']  = dframe.time.diff()
    # time_diffを1つ手前にずらしたもの
    dframe['time_diff2'] = dframe.time_diff[1:len(dframe.time_diff)].append(
        pd.Series([np.nan])).reset_index(drop=True)

    return dframe[(dframe.time_diff <= 2) | (dframe.time_diff2 <= 2)]

#======================================================================
if __name__ == '__main__':
    ap = arg_parser()
    args = ap.parse_args()
    if len(args.datafiles) < 1:
        print "no datafiles given"
        ap.print_help()
        quit()
    datafiles = args.datafiles
    savefile  = args.save_file
    # datafiles = ['150609.dat', '151014_01.dat', '151014_02.dat']

    dfs = []
    for datafile in datafiles:
        df = pd.read_csv(datafile,
                         skiprows=1,
                         delimiter='\t',
                         header=None,
                         names=('time', 'type', 'dir', 'true', 'w_img', 'wo_img'))
        dfs.append(df)

    # concat dataframes
    df = pd.concat(dfs).reset_index(drop=True)

    # dataframe storing results
    result = pd.DataFrame(columns=['tp', 'fn', 'fp'])

    # w/ image process
    tp = len(df[(df.w_img==1) & (df.true==1)])
    fn = len(df[(df.w_img==0) & (df.true==1)])
    fp = len(df[(df.w_img==1) & (df.true==0)])
    result = result.append(pd.Series([tp, fn, fp],
                                     index=('tp', 'fn', 'fp'),
                                     name='w/ img'))
    # w/ image process for each dir
    tp = len(df[(df.dir=='L2R') & (df.w_img==1) & (df.true==1)])
    fn = len(df[(df.dir=='L2R') & (df.w_img==0) & (df.true==1)])
    fp = len(df[(df.dir=='L2R') & (df.w_img==1) & (df.true==0)])
    result = result.append(pd.Series([tp, fn, fp],
                                     index=('tp', 'fn', 'fp'),
                                     name='w/ img (L2R)'))
    tp = len(df[(df.dir=='R2L') & (df.w_img==1) & (df.true==1)])
    fn = len(df[(df.dir=='R2L') & (df.w_img==0) & (df.true==1)])
    fp = len(df[(df.dir=='R2L') & (df.w_img==1) & (df.true==0)])
    result = result.append(pd.Series([tp, fn, fp],
                                     index=('tp', 'fn', 'fp'),
                                     name='w/ img (R2L)'))

    # w/o image process
    tp = len(df[(df.wo_img==1) & (df.true==1)])
    fn = len(df[(df.wo_img==0) & (df.true==1)])
    fp = len(df[(df.wo_img==1) & (df.true==0)])
    result = result.append(pd.Series([tp, fn, fp],
                                     index=('tp', 'fn', 'fp'),
                                     name='w/o img'))
    # w/o image process for each dir
    tp = len(df[(df.dir=='L2R') & (df.wo_img==1) & (df.true==1)])
    fn = len(df[(df.dir=='L2R') & (df.wo_img==0) & (df.true==1)])
    fp = len(df[(df.dir=='L2R') & (df.wo_img==1) & (df.true==0)])
    result = result.append(pd.Series([tp, fn, fp],
                                     index=('tp', 'fn', 'fp'),
                                     name='w/o img (L2R)'))
    tp = len(df[(df.dir=='R2L') & (df.wo_img==1) & (df.true==1)])
    fn = len(df[(df.dir=='R2L') & (df.wo_img==0) & (df.true==1)])
    fp = len(df[(df.dir=='R2L') & (df.wo_img==1) & (df.true==0)])
    result = result.append(pd.Series([tp, fn, fp],
                                     index=('tp', 'fn', 'fp'),
                                     name='w/o img (R2L)'))

    # normal car
    tp = len(df[((df.type=='normal')|(df.type=='middle')) & (df.w_img==1) & (df.true==1)])
    fn = len(df[((df.type=='normal')|(df.type=='middle')) & (df.w_img==0) & (df.true==1)])
    fp = len(df[((df.type=='normal')|(df.type=='middle')) & (df.w_img==1) & (df.true==0)])
    result = result.append(pd.Series([tp, fn, fp],
                                     index=('tp', 'fn', 'fp'),
                                     name='normal cars'))

    # bus, truck
    tp = len(df[((df.type=='bus')|(df.type=='truck')) & (df.w_img==1) & (df.true==1)])
    fn = len(df[((df.type=='bus')|(df.type=='truck')) & (df.w_img==0) & (df.true==1)])
    fp = len(df[((df.type=='bus')|(df.type=='truck')) & (df.w_img==1) & (df.true==0)])
    result = result.append(pd.Series([tp, fn, fp],
                                     index=('tp', 'fn', 'fp'),
                                     name='buses and trucks'))

    # small car
    tp = len(df[((df.type=='small')|(df.type=='small truck')) & (df.w_img==1) & (df.true==1)])
    fn = len(df[((df.type=='small')|(df.type=='small truck')) & (df.w_img==0) & (df.true==1)])
    fp = len(df[((df.type=='small')|(df.type=='small truck')) & (df.w_img==1) & (df.true==0)])
    result = result.append(pd.Series([tp, fn, fp],
                                     index=('tp', 'fn', 'fp'),
                                     name='small cars'))

    # bike
    tp = len(df[(df.type=='bike') & (df.w_img==1) & (df.true==1)])
    fn = len(df[(df.type=='bike') & (df.w_img==0) & (df.true==1)])
    fp = len(df[(df.type=='bike') & (df.w_img==1) & (df.true==0)])
    result = result.append(pd.Series([tp, fn, fp],
                                     index=('tp', 'fn', 'fp'),
                                     name='bikes'))

    # calculate accuracy, precision, recall, and f-measure
    result["accuracy"]  = result.tp / result.sum(axis=1)
    result["precision"] = result.tp / (result.tp+result.fp)
    result["recall"]    = result.tp / (result.tp+result.fn)
    result["f_measure"] = 2*result.precision*result.recall / (result.precision+result.recall)

    print result

    if savefile is not None:
        with open(savefile, 'w') as f:
            f.write("# ")
            result.to_csv(savefile,
                          sep='\t',
                          index=True,
                          na_rep='-',
                          mode='a',
                          )

    if args.simul is not True:
        quit()

    # extract simultaneous passing
    simuls = []
    for d in dfs:
        simuls.append(extract_simultaneous(d))
    simul = pd.concat(simuls).reset_index(drop=True)

    simul_passing = {}
    simul_passing['normal']    = len(simul[((simul.type=='normal')|(simul.type=='middle'))])
    simul_passing['bus,truck'] = len(simul[((simul.type=='bus')|(simul.type=='truck'))])
    simul_passing['small']     = len(simul[((simul.type=='small')|(simul.type=='small truck'))])
    simul_passing['bike']      = len(simul[(simul.type=='bike')])
    print
    print "simultaneous passing:"
    print simul_passing
    print simul

    if savefile is not None:
        with open(savefile, 'a') as f:
            f.write("\n# number of simultaneous passing\n# ")
            f.write(str(simul_passing) + "\n")
