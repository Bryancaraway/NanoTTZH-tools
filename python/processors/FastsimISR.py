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
import ROOT
import os


def GetNISRJetDist(files, isrEffFile, fileDirectory = os.environ['CMSSW_BASE'] + "/src/PhysicsTools/NanoSUSYTools/data/isrSF/"):
    # Assuming each file is a unique process
    outfile = ROOT.TFile(fileDirectory + "/" + isrEffFile, "RECREATE")
    for i, filename in enumerate(files):
        f = uproot.open(filename)["Events"]
        procname=os.path.splitext(os.path.basename(filename))[0].split("_split")[0]
        hist, binedges = np.histogram(f.array("nISRJets"), bins=10, range=(0, 10))
        histogram = ROOT.TH1F("NJetsISR_"+procname, procname, 10, 0, 10)
        for i in range(0, 10):
            histogram.SetBinContent(i+1, hist[i])
        outfile.cd()
        histogram.Write()
    outfile.Close()

if __name__ == "__main__":
    with open("./SMS_T2tt_mStop_150to250_fastsim_2018.txt") as f:
        files = [line.strip() for line in f]
    GetNISRJetDist(files, "test.root")
