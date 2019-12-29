#!/usr/bin/env python
import os, sys
import argparse
import ROOT
import time
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jecUncertainties import jecUncertProducer
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import jetmetUncertaintiesProducer
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import jetRecalib
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import btagSFProducer
from TopTagger.TopTagger.TopTaggerProducer import TopTaggerProducer

# NanoSUSY Tools modules
from PhysicsTools.NanoSUSYTools.modules.eleMiniCutIDProducer import *
from PhysicsTools.NanoSUSYTools.modules.Stop0lObjectsProducer import *
from PhysicsTools.NanoSUSYTools.modules.Stop0lBaselineProducer import *
from PhysicsTools.NanoSUSYTools.modules.DeepTopProducer import *
from PhysicsTools.NanoSUSYTools.modules.updateEvtWeight import *
from PhysicsTools.NanoSUSYTools.modules.lepSFProducer import *
from PhysicsTools.NanoSUSYTools.modules.updateJetIDProducer import UpdateJetID
from PhysicsTools.NanoSUSYTools.modules.PDFUncertaintyProducer import PDFUncertiantyProducer
from PhysicsTools.NanoSUSYTools.modules.GenPartFilter import GenPartFilter
from PhysicsTools.NanoSUSYTools.modules.BtagSFWeightProducer import BtagSFWeightProducer
from PhysicsTools.NanoSUSYTools.modules.UpdateMETProducer import UpdateMETProducer
from PhysicsTools.NanoSUSYTools.modules.FastsimMassesProducer import FastsimMassesProducer
from PhysicsTools.NanoSUSYTools.modules.PrefireCorr import PrefCorr
from PhysicsTools.NanoSUSYTools.modules.ISRWeightProducer import ISRSFWeightProducer
from PhysicsTools.NanoSUSYTools.modules.Stop0l_trigger import Stop0l_trigger
import uproot
# JEC files are those recomended here (as of Mar 1, 2019)
# https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC#Recommended_for_MC
# Actual text files are found here
# JEC: https://github.com/cms-jet/JECDatabase/tree/master/textFiles
# JER: https://github.com/cms-jet/JRDatabase/tree/master/textFiles
DataDepInputs = {
    "MC": {
        "2016" : {"pileup_Data": "Cert271036_284044_23Sep2016ReReco_Collisions16.root",
                  "pileup_MC": "pileup_profile_2016.root",
                  "JERMC": "Summer16_25nsV1_MC",
                  "JECMC": "Summer16_07Aug2017_V11_MC",
                  "redoJEC": False,
                 },
        "2017" : {"pileup_Data": "Cert294927_306462_EOY2017ReReco_Collisions17.root",
                  "pileup_MC": "pileup_profile_2017.root",
                  "JERMC": "Fall17_V3_MC",
                  "JECMC": "Fall17_17Nov2017_V32_MC",
                  "redoJEC": False,
                 },
        "2018" : {"pileup_Data": "ReReco2018ABC_PromptEraD_Collisions18.root",
                  "pileup_MC": "pileup_profile_2018.root",
                  "JERMC": "Autumn18_V1_MC",
                  "JECMC": "Autumn18_V8_MC",
                  "redoJEC": True,
                 }
    },

    "FASTSIM": {
        "2016" : {"pileup_Data": "Cert271036_284044_23Sep2016ReReco_Collisions16.root",
                  "pileup_MC": "pileup_profile_2016.root",
                  "JERMC": "Summer16_25nsV1_MC",
                  "JECMC": "Spring16_25nsFastSimV1_MC",
                  "redoJEC": False,
                 },
        "2017" : {"pileup_Data": "Cert294927_306462_EOY2017ReReco_Collisions17.root",
                  "pileup_MC": "pileup_profile_2017.root",
                  "JERMC": "Fall17_V3_MC",
                  "JECMC": "Fall17_FastsimV1_MC",
                  "redoJEC": True,
                 },
        "2018" : {"pileup_Data": "ReReco2018ABC_PromptEraD_Collisions18.root",
                  "pileup_MC": "pileup_profile_2018.root",
                  "JERMC": "Autumn18_V1_MC",
                  "JECMC": "Fall17_FastsimV1_MC",
                  "redoJEC": True,
                 }
    },

    "Data": {
        "2016B" : { "JEC": "Summer16_07Aug2017BCD_V11_DATA",
                    "redoJEC": False,
                   },
        "2016C" : { "JEC": "Summer16_07Aug2017BCD_V11_DATA",
                    "redoJEC": False,
                   },
        "2016D" : { "JEC": "Summer16_07Aug2017BCD_V11_DATA",
                    "redoJEC": False,
                   },
        "2016E" : { "JEC": "Summer16_07Aug2017EF_V11_DATA",
                    "redoJEC": False,
                   },
        "2016F" : { "JEC": "Summer16_07Aug2017EF_V11_DATA",
                    "redoJEC": False,
                   },
        "2016G" : { "JEC": "Summer16_07Aug2017GH_V11_DATA",
                    "redoJEC": False,
                   },
        "2016H" : { "JEC": "Summer16_07Aug2017GH_V11_DATA",
                    "redoJEC": False,
                   },

        "2017B" : { "JEC": "Fall17_17Nov2017B_V32_DATA",
                    "redoJEC": False,
                   },
        "2017C" : { "JEC": "Fall17_17Nov2017C_V32_DATA",
                    "redoJEC": False,
                   },
        "2017D" : { "JEC": "Fall17_17Nov2017DE_V32_DATA",
                    "redoJEC": False,
                   },
        "2017E" : { "JEC": "Fall17_17Nov2017DE_V32_DATA",
                    "redoJEC": False,
                   },
        "2017F" : { "JEC": "Fall17_17Nov2017F_V32_DATA",
                    "redoJEC": False,
                   },

        "2018A" : { "JEC": "Autumn18_RunA_V8_DATA",
                    "redoJEC": True,
                   },
        "2018B" : { "JEC": "Autumn18_RunB_V8_DATA",
                    "redoJEC": True,
                   },
        "2018C" : { "JEC": "Autumn18_RunC_V8_DATA",
                    "redoJEC": True,
                   },
        "2018D" : { "JEC": "Autumn18_RunD_V8_DATA",
                    "redoJEC": True,
                   },
            }
}

DeepResovledDiscCut = 0.6

def main(args):
    isdata = len(args.dataEra) > 0
    isfastsim = args.isFastSim
    isSUSY = args.sampleName.startswith("SMS_")

    if isdata and isfastsim:
        print "ERROR: It is impossible to have a dataset that is both data and fastsim"
        exit(0)

    if isdata:
        dataType="Data"
        if not args.era + args.dataEra in DataDepInputs[dataType].keys():
            print "ERROR: Era \"" + args.era + "\" not recognized"
            exit(0)
    elif isfastsim:
        dataType="FASTSIM"
        if not args.era + args.dataEra in DataDepInputs[dataType].keys():
            print "ERROR: Era \"" + args.era + "\" not recognized"
            exit(0)
    else:
        dataType = "MC"
        if not args.era in DataDepInputs[dataType].keys():
            print "ERROR: Era \"" + args.era + "\" not recognized"
            exit(0)

    sampleType = args.sampleName.split("_")[1]

    #mods = [FastsimVarProducer(isfastsim)]
    mods = [FastsimMassesProducer(isfastsim)]

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

    p=PostProcessor(args.outputfile,files,cut=None, branchsel=None, outputbranchsel=None, modules=mods,provenance=False,maxEvents=args.maxEvents)
    p.run()

    #g = files
    g = [f for f in os.listdir(os.curdir) if (os.path.isfile(f) and "Skim" in f)]
    import uproot
    import numpy as np
    uniq = None
    for array in uproot.iterate(g, "Events", ["Stop0l_MotherMass",
                                              "Stop0l_LSPMass"],
                                entrysteps=1000):
        comp = zip(array["Stop0l_MotherMass"], array["Stop0l_LSPMass"])
        uniqcomp = np.unique(comp, axis=0)
        if uniq is None:
            uniq = uniqcomp
        else:
            uniq = np.concatenate((uniq, uniqcomp), axis=0)
    masspoints =np.unique(uniq, axis=0)
    print(masspoints)

    for p in masspoints:
        cutstr = "Stop0l_MotherMass == %d && Stop0l_LSPMass == %d " % (p[0], p[1])
        poststr = "_Mom%d_LSP%d" % (p[0], p[1])
        pp=PostProcessor(args.outputfile,g,cut=cutstr, postfix=poststr, provenance=False,maxEvents=args.maxEvents)
        pp.run()
        print(p, poststr)
        os.system("python haddnano.py SMS_{0}_fastsim_Mom{1}_LSP{2}.root *_Mom{1}_LSP{2}_*.root".format(sampleType,int(p[0]),int(p[1])))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='NanoAOD postprocessing.')
    parser.add_argument('-i', '--inputfile',
        default = "testing.txt",
        help = 'Path to the input filelist. To run with a single file instead of a file list prepend the filepath with \"file:\" (Default: testing.txt)')
    parser.add_argument('-o', '--outputfile',
                        default="./",
                        help = 'Path to the output file location. (Default: .)')
    parser.add_argument('-e', '--era',
        default = "2017", help = 'Year of production')
    parser.add_argument('-f', '--isFastSim', action="store_true",  default = False,
                        help = "Input file is fastsim (Default: false)")
    parser.add_argument('-d', '--dataEra',    action="store",  type=str, default = "",
                        help = "Data era (B, C, D, ...).  Using this flag also switches the procesor to data mode. (Default: None, i.e. MC )")
    parser.add_argument('-s', '--sampleName',    action="store",  type=str, default = "",
                        help = "Name of MC sample (from sampleSet file) (Default: )")
    parser.add_argument('-c', '--crossSection',
                        type=float,
                        default = 1,
                        help = 'Cross Section of MC to use for MC x-sec*lumi weight (Default: 1.0)')
    parser.add_argument('-n', '--nEvents',
                        type=float,
                        default = 1,
                        help = 'Number of events to use for MC x-sec*lumi weight (NOT the number of events to run over) (Default: 1.0)')
    parser.add_argument('-m', '--maxEvents',
                        type=int,
                        default = -1,
                        help = 'MAximum number of events to process (Default: all events)')
    args = parser.parse_args()
    main(args)
