#!/usr/bin/env python
import os, sys
import argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jecUncertainties import jecUncertProducer
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import jetmetUncertaintiesProducer
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import jetRecalib
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import btagSFProducer
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2  import * 

# NanoTTZH Tools modules
from PhysicsTools.NanoTTZHTools.modules.eleMiniCutIDProducer import *
from PhysicsTools.NanoTTZHTools.modules.PDFUncertaintyProducer import PDFUncertaintyProducer
from PhysicsTools.NanoTTZHTools.modules.GenPartFilter import GenPartFilter
from PhysicsTools.NanoTTZHTools.modules.BtagSFWeightProducer import BtagSFWeightProducer
from PhysicsTools.NanoTTZHTools.modules.UpdateMETProducer import UpdateMETProducer

# JEC files are those recomended here for nanoAODv7 samples (as of Dec 27th, 2020)
# https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC#Recommended_for_MC
# Actual text files are found here
# JEC: https://github.com/cms-jet/JECDatabase/tree/master/textFiles
# JER: https://github.com/cms-jet/JRDatabase/tree/master/textFiles
DataDepInputs = {
    "MC": {
        "2016" : {
            "pileup_Data": "PileupData_GoldenJSON_Full2016.root",
            "pileup_MC": "pileup_profile_Summer16.root", 
        },
        "2017" : {
            "pileup_Data": "PileupHistogram-goldenJSON-13tev-2017-99bins_withVar.root", 
            "pileup_MC": "mcPileup2017.root",
        },
        "2018" : {
            "pileup_Data": "PileupHistogram-goldenJSON-13tev-2018-100bins_withVar.root",
            "pileup_MC": "mcPileup2018.root",
        }
    },

    "Data": {
        "2016B","2016C","2016D","2016E","2016F","2016G","2016H",
        "2017B","2017C","2017D","2017E","2017F",
        "2018A","2018B","2018C","2018D"
    }
}


def main(args):
    isdata = len(args.dataEra) > 0

    if isdata:
        dataType="Data"
        if not args.era + args.dataEra in DataDepInputs[dataType]:
            print "ERROR: Era \"" + args.era + "\" not recognized"
            exit(0)

    else:
        dataType = "MC"
        if not args.era in DataDepInputs[dataType].keys():
            print "ERROR: Era \"" + args.era + "\" not recognized"
            exit(0)

    mods = []

    #~~~~~ Different modules for Data and MC ~~~~~
    # These modules must be run first in order to update JEC and MET approperiately for future modules 
    # The MET update module must also be run before the JEC update modules 
    if args.era == "2017":
        # EE noise mitigation in PF MET
        # https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1865.html
        mods.append(UpdateMETProducer("METFixEE2017"))
        
    if isdata:
        # Apply resediual JEC on Data
        mods.append(createJMECorrector(isMC=False, dataYear=int(args.era), runPeriod=args.dataEra, jetType = "AK8PFPuppi")())
    else:
        mods.append(createJMECorrector(isMC=True, dataYear=int(args.era), jesUncert="Merged", applyHEMfix=(True if args.era == '2018' else False))())
        mods.append(createJMECorrector(isMC=True, dataYear=int(args.era), jesUncert="Merged", jetType = "AK8PFPuppi", applyHEMfix=(True if args.era == '2018' else False))())

    #~~~~~ Common modules for Data and MC ~~~~~
    mods.append(eleMiniCutID())

    #~~~~~ Modules for MC Only ~~~~
    if not isdata:
        pufile_data = "{0}/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/{1}".format(os.environ['CMSSW_BASE'], DataDepInputs[dataType][args.era]["pileup_Data"])
        pufile_mc   = "{0}/src/PhysicsTools/NanoAODTools/python/postprocessing/data/pileup/{1}".format(os.environ['CMSSW_BASE'], DataDepInputs[dataType][args.era]["pileup_MC"])
        ## Major modules for MC
        mods += [
            PDFUncertaintyProducer(isdata),
            puWeightProducer(pufile_mc, pufile_data, "pu_mc","pileup"),
            btagSFProducer(args.era if args.era != '2016' else 'Legacy2016', algo="deepcsv", verbose=0),
            #btagSFProducer(args.era, algo="deepjet", verbose=0),
            BtagSFWeightProducer(args.era),
            #''' 
            #statusFlag 0x2100 corresponds to "isLastCopy and fromHardProcess"
            #statusFlag 0x2080 corresponds to "IsLastCopy and isHardProcess"
            #'''
            GenPartFilter(statusFlags = [0x2100, 0x2080, 0x2000, 0], pdgIds = [0, 0, 22, 0], statuses = [0, 0, 1, 23]),
            ]
        # 2016 and 2017 L1 ECal prefiring reweighting
        if args.era == "2016" or args.era == "2017":
            era_map = {'2016':'H', '2017':'F'}
            prefargs = {
                "jetroot":"L1prefiring_jetpt_{0}Bto{1}.root".format(args.era, era_map[args.era]),
                "jetmapname":"L1prefiring_jetpt_{0}Bto{1}".format(args.era, era_map[args.era]),
                "photonroot":"L1prefiring_photonpt_{0}Bto{1}.root".format(args.era, era_map[args.era]),
                "photonmapname":"L1prefiring_photonpt_{0}Bto{1}".format(args.era, era_map[args.era])
            }
            mods.append(PrefCorr(**prefargs))

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

    p=PostProcessor(args.outputfile,files,cut=None, branchsel=None, outputbranchsel="keep_and_drop.txt", modules=mods,provenance=False,maxEntries=args.maxEvents, prefetch=True)
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
                        default = None,
                        help = 'MAximum number of events to process (Default: all events)')
    args = parser.parse_args()
    main(args)
