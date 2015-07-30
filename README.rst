.. -*- coding: utf-8; -*-

============================================
 ITSプロジェクト向けSound Map描画プログラム
============================================

音声ファイルの左右音声の類似性をGeneralized Cross-Correlationを使って判断するプログラム。

Required Libraries
==================

* wave
* numpy
* scipy

Usage
=====

* ``python main.py <wavefile>`` のように音声のwavファイルを指定して実行する。

注意事項
========

24-bitのwaveファイルを処理する場合はとても遅いです。

* 24-bitはそのままでは読み込めず、変換を行う必要があるため。

Copyright, License
==================

Copyright (c) 2015, Shigemi ISHIDA

**DO NOT REDISTRIBUTE THIS PROGRAM AND A PART OF THIS PROGRAM.**
