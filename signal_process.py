# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# DO NOT REDISTRIBUTE THIS PROGRAM AND A PART OF THIS PROGRAM.
#

import sys

#======================================================================
class SignalProcess():
    # winsize: windows size of FFT
    # shift  : shift size
    def __init__(self, data1, data2, winsize=1024, shift=256):
        # check shift size.
        if winsize % shift != 0:
            sys.stderr.write("Invalid shift size: window size is a multiple of shift size.\n")
            raise ValueError
        self.winsize = winsize
        self.shift   = shift
        self.folds   = self.winsize / self.shift

        # check data length.
        if len(data1) != len(data2):
            sys.stderr.write("Data length not match.\n")
            raise ValueError

        # store data.
        #   if data length is not a multiple of shift size, drop some data.
        if len(data1) % self.winsize != 0:
            self.data1 = data1[0:-(len(data1) % self.shift)]
            self.data2 = data2[0:-(len(data2) % self.shift)]
        else:
            self.data1 = data1
            self.data2 = data2

        # fold on shift size
        self.data1 = self.data1.reshape(-1,self.shift)
        self.data2 = self.data2.reshape(-1,self.shift)

        return

    def __call__(self):
        return

    def __del__(self):
        return
