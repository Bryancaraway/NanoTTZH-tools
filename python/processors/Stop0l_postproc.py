#!/usr/bin/env python
import os, sys
import argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoSUSYTools.modules.eleMiniCutIDProducer import *
from PhysicsTools.NanoSUSYTools.modules.Stop0lObjectsProducer import *
from PhysicsTools.NanoSUSYTools.modules.Stop0lBaselineProducer import *
from PhysicsTools.NanoSUSYTools.modules.DeepTopProducer import *
from PhysicsTools.NanoSUSYTools.modules.updateEvtWeight import *
from PhysicsTools.NanoSUSYTools.modules.lepSFProducer import *
from PhysicsTools.NanoSUSYTools.modules.updateJetIDProducer import *
from PhysicsTools.NanoSUSYTools.modules.PDFUncertaintyProducer import *
from PhysicsTools.NanoSUSYTools.modules.GenPartFilter import GenPartFilter
from PhysicsTools.NanoSUSYTools.modules.BtagSFWeightProducer import BtagSFWeightProducer
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import jetmetUncertaintiesProducer
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import jetRecalib
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import btagSFProducer
from TopTagger.TopTagger.TopTaggerProducer import TopTaggerProducer

# JEC files are those recomended here (as of Mar 1, 2019)
# https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC#Recommended_for_MC
# Actual text files are found here
# JEC: https://github.com/cms-jet/JECDatabase/tree/master/textFiles
# JER: https://github.com/cms-jet/JRDatabase/tree/master/textFiles
DataDepInputs = {
    "MC": {
        "2016" : { "pileup": "Cert271036_284044_23Sep2016ReReco_Collisions16.root",
                   "JERMC": "Summer16_25nsV1_MC",
                   "JECMC": "Summer16_07Aug2017_V11_MC",
                   "redoJEC": False,
                   },
        "2017" : { "pileup": "Cert294927_306462_EOY2017ReReco_Collisions17.root",
                   "JERMC": "Fall17_V3_MC",
                   "JECMC": "Fall17_17Nov2017_V32_MC",
                   "redoJEC": False,
                   },
        "2018" : { "pileup": "Cert314472_325175_PromptReco_Collisions18.root",
                   "JERMC": "Autumn18_V1_MC",
                   "JECMC": "Autumn18_V8_MC",
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

def main(args):
    isdata = len(args.dataEra) > 0
    isfastsim = args.isFastSim

    if isdata and isfastsim:
        print "ERROR: It is impossible to have a dataset that is both data and fastsim"
        exit(0)

    if isdata:
        if not args.era + args.dataEra in DataDepInputs["Data"].keys():
            print "ERROR: Era \"" + args.era + "\" not recognized"
            exit(0)
    else:
        if not args.era in DataDepInputs["MC"].keys():
            print "ERROR: Era \"" + args.era + "\" not recognized"
            exit(0)

    mods = [
        eleMiniCutID(),
        Stop0lObjectsProducer(args.era),
        DeepTopProducer(args.era),
        Stop0lBaselineProducer(args.era, isData=isdata, isFastSim=isfastsim),
        UpdateEvtWeight(isdata, args.crossSection, args.nEvents)
    ]
    if args.era == "2018":
        mods.append(UpdateJetID(args.era))

    #~~~~~ For MC ~~~~~
    if not isdata:
        pufile = "%s/src/PhysicsTools/NanoSUSYTools/data/pileup/%s" % (os.environ['CMSSW_BASE'], DataDepInputs["MC"][args.era]["pileup"])
        mods += [
            # jecUncertProducer(DataDepInputs[args.era]["JECU"]),
            jetmetUncertaintiesProducer(args.era, DataDepInputs["MC"][args.era]["JECMC"], jerTag=DataDepInputs["MC"][args.era]["JERMC"], redoJEC=DataDepInputs["MC"][args.era]["redoJEC"], doSmearing=False),
#            PDFUncertiantyProducer(isdata),
            # lepSFProducer(args.era),
            puWeightProducer("auto", pufile, "pu_mc","pileup", verbose=False),
            btagSFProducer(era=args.era, algo="deepcsv"),
            BtagSFWeightProducer("allInOne_bTagEff_deepCSVb_med.root", args.sampleName, DeepCSVMediumWP[args.era]),
            # statusFlag 0x2100 corresponds to "isLastCopy and fromHardProcess"
            # statusFlag 0x2080 corresponds to "IsLastCopy and isHardProcess"
            GenPartFilter(statusFlags = [0x2100, 0x2080, 0x2000], pdgIds = [0, 0, 22], statuses = [0, 0, 1]),
            TopTaggerProducer(recalculateFromRawInputs=True,                   AK4JetInputs=("Jet_pt",              "Jet_eta", "Jet_phi", "Jet_mass"),              topDiscCut=0.6),
            TopTaggerProducer(recalculateFromRawInputs=True, suffix="JESUp",   AK4JetInputs=("Jet_pt_jesTotalUp",   "Jet_eta", "Jet_phi", "Jet_mass_jesTotalUp"),   topDiscCut=0.6),
            TopTaggerProducer(recalculateFromRawInputs=True, suffix="JESDown", AK4JetInputs=("Jet_pt_jesTotalDown", "Jet_eta", "Jet_phi", "Jet_mass_jesTotalDown"), topDiscCut=0.6),
        ]
    else:
        if DataDepInputs["Data"][args.era + args.isData]["redoJEC"]:
            mods += [
                jetRecalib(DataDepInputs["Data"][args.era + args.isData]["JEC"]),
                ]
            
        mods += [
            TopTaggerProducer(recalculateFromRawInputs=True, AK4JetInputs=("Jet_pt", "Jet_eta", "Jet_phi", "Jet_mass"),  topDiscCut=0.6),
        ]
        

    files = []
    if len(args.inputfile) > 5 and args.inputfile[0:5] == "file:":
        #This is just a single test input file
        files.append(args.inputfile[5:])
    else:
        #this is a file list
        with open(args.inputfile) as f:
            files = [line.strip() for line in f]

    p=PostProcessor(args.outputfile,files,cut=None, branchsel=None, outputbranchsel="keep_and_drop.txt", modules=mods,provenance=False)
    p.run()




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
                        help = "Input file is data (Default: false)")
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
    args = parser.parse_args()
    main(args)
