#!/usr/bin/env python
# encoding: utf-8

# File        : test.py
# Author      : Ben Wu
# Contact     : benwu@fnal.gov
# Date        : 2019 Dec 19
#
# Description : 

import uproot
import numpy as np
import types
import os
import uproot_methods.classes.TH1

class MyTH1(uproot_methods.classes.TH1.Methods, list):
    def __init__(self, low, high, values, title=""):
        self._fXaxis = lambda:None
        self._fXaxis._fNbins = len(values)
        self._fXaxis._fXmin = low
        self._fXaxis._fXmax = high
        for x in values:
            self.append(float(x))
        self._fTitle = title
        self._classname = "TH1F"

def GetNISRJetDist(files, isrEffFile, fileDirectory = os.environ['CMSSW_BASE'] + "/src/PhysicsTools/NanoSUSYTools/data/isrSF/"):
    # Assuming each file is a unique process
    outfile = uproot.recreate(fileDirectory + "/" + isrEffFile)
    for i, filename in enumerate(files):
        f = uproot.open(filename)["Events"]
        procname=os.path.splitext(os.path.basename(filename))[0]
        hist, binedges = np.histogram(f.array("nISRJets"), bins=10, range=(0, 10))
        histogram = MyTH1(binedges[0], binedges[-1], hist)
        outfile["NJetsISR_"+procname] = histogram
    outfile.close()

if __name__ == "__main__":
    with open("./SMS_T2tt_mStop_150to250_fastsim_2018.txt") as f:
        files = [line.strip() for line in f]
    GetNISRJetDist(files, "test.root")
