#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoSUSYTools.modules.eleMiniCutIDProducer import *
from PhysicsTools.NanoSUSYTools.modules.Stop0lObjectsProducer import *
from PhysicsTools.NanoSUSYTools.modules.Stop0lBaselineProducer import *
from PhysicsTools.NanoSUSYTools.modules.DeepTopProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *

def main(args):

    era = "2017"
    isFastSim = False
    mods = [
        eleMiniCutID(),
        Stop0lObjectsProducer(era),
        DeepTopProducer(era),
        Stop0lBaselineProducer(era, isFastSim)
    ]

    if era == "2016":
        mods += [
            puWeightProducer(pufile_mc,pufile_data,"pu_mc","pileup",verbose=False)
        ]

    if era == "2017":
        mods += [
            puWeightProducer("auto",pufile_data2017,"pu_mc","pileup",verbose=False)
        ]

    #files=["/uscms_data/d3/lpcsusyhad/benwu/Moriond2019/TestNanoAOD/CMSSW_10_4_X_2018-12-11-2300/src/prod2017MC_NANO.root"]
    #files=["/eos/uscms/store/user/benwu/Stop18/NtupleSyncMiniAOD/NanoSUSY/2018Xmas/prod2017MC_NANO.root"]
    
    files = []
    lines = open(args.inputfile).readlines()
    for line in lines:
        files.append(line)

    p=PostProcessor(".",files,cut=None, branchsel=None, outputbranchsel="keep_and_drop.txt", modules=mods,provenance=False)
    p.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='NanoAOD postprocessing.')
    parser.add_argument('-i', '--inputfile',
        help = 'Path to the input filelist.')
    #parser.add_argument('-o', '--outputfile',
    #    help = 'Path to the output file location.')
    args = parser.parse_args()
    main(args)

