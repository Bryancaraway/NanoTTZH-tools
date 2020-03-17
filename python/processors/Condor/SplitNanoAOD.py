#!/usr/bin/env python
import os, sys
import argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
import uproot
import numpy as np
from multiprocessing import Process

def RunPost(outdir, file, ran, i):
    p=PostProcessor(args.outputfile, [file], cut="Entry$ >= %d && Entry$ < %d" % (ran[i], ran[i+1]),
                    postfix = "_split%d" % i, modules=[],provenance=False)
    p.run()

def main(args):
    mods = []

    #============================================================================#
    #-------------------------     Run PostProcessor     ------------------------#
    #============================================================================#
    files = []
    if len(args.inputfile) > 5 and args.inputfile[0:5] == "file:":
        #This is just a single test input file
        files.append(args.inputfile[5:])
    else:
        #this is a file list
        with open(args.inputfile) as f:
            files = [line.strip() for line in f]

    nsplit = args.nSplit + 2
    for file in files:
        nevt = uproot.numentries(file, "Events")
        ran = np.linspace(0, nevt+1, 5, dtype=int)
        print(file, nevt, ran)
        plist  =[]
        for i in range(len(ran)-1):
            print (i, ran[i], ran[i+1])
            p = Process(target=RunPost, args=(args.outputfile, file, ran, i))
            p.start()
            plist.append(p)
        exit_codes = [p.join() for p in plist]

    ### Split before and post HEM for 2018 data
    # p=PostProcessor(args.outputfile,files,cut="run < 319077", branchsel=None, outputbranchsel=None, postfix = "_preHEM", modules=mods,provenance=False,maxEvents=args.maxEvents)
    # p.run()
    # p=PostProcessor(args.outputfile,files,cut="run >= 319077", branchsel=None, outputbranchsel=None, postfix = "_postHEM", modules=mods,provenance=False,maxEvents=args.maxEvents)
    # p.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='NanoAOD postprocessing.')
    parser.add_argument('-i', '--inputfile',
        default = "testing.txt",
        help = 'Path to the input filelist. To run with a single file instead of a file list prepend the filepath with \"file:\" (Default: testing.txt)')
    parser.add_argument('-o', '--outputfile',
                        default="./",
                        help = 'Path to the output file location. (Default: .)')
    parser.add_argument('-n', '--nSplit',
                        type=float,
                        default = 4,
                        help = 'Split ntuple into N equal subfiles')
    args = parser.parse_args()
    main(args)
