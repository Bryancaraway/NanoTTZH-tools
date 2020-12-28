import ROOT
import os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class BtagSFWeightProducer(Module):

    def __init__(self, era, jetPtMin = 30, jetEtaMax = 2.4):
        self.jetPtMin  = jetPtMin
        self.jetEtaMax = jetEtaMax
        self.era       = era

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        # need to calculate weight, and variations from jes, lf, hf, lfstats[1,2], hfstats[1,2]
        # following method 1d: https://twiki.cern.ch/twiki/bin/view/CMS/BTagShapeCalibration
        self.out.branch("BTagWeight",           "F", title="BTag event weight following method 1d")
        # jes (jec)
        self.out.branch("BTagWeight_jes_up",    "F", title="jes up varition of BTag event weight following method 1d")
        self.out.branch("BTagWeight_jes_down",  "F", title="jes down varition of BTag event weight following method 1d")
        # lf/hf (purity)
        self.out.branch("BTagWeight_lf_up",     "F", title="lf up varition of BTag event weight following method 1d")
        self.out.branch("BTagWeight_lf_down",   "F", title="lf down varition of BTag event weight following method 1d")
        self.out.branch("BTagWeight_hf_up",     "F", title="hf up varition of BTag event weight following method 1d")
        self.out.branch("BTagWeight_hf_down",   "F", title="hf down varition of BTag event weight following method 1d")
        # lf/hf (stats)
        self.out.branch("BTagWeight_lfstats1_up",     "F", title="lf stats1 up varition of BTag event weight following method 1d")
        self.out.branch("BTagWeight_lfstats1_down",   "F", title="lf stats1 down varition of BTag event weight following method 1d")
        self.out.branch("BTagWeight_hfstats1_up",     "F", title="hf stats1 up varition of BTag event weight following method 1d")
        self.out.branch("BTagWeight_hfstats1_down",   "F", title="hf stats1 down varition of BTag event weight following method 1d")
        self.out.branch("BTagWeight_lfstats2_up",     "F", title="lf stats2 up varition of BTag event weight following method 1d")
        self.out.branch("BTagWeight_lfstats2_down",   "F", title="lf stats2 down varition of BTag event weight following method 1d")
        self.out.branch("BTagWeight_hfstats2_up",     "F", title="hf stats2 up varition of BTag event weight following method 1d")
        self.out.branch("BTagWeight_hfstats2_down",   "F", title="hf stats2 down varition of BTag event weight following method 1d")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        jets = Collection(event, "Jet")
        
        btagweight = 1.
        btagweight_jes_up = 1.
        btagweight_jes_down = 1.
        btagweight_lf_up = 1.
        btagweight_lf_down = 1.
        btagweight_hf_up = 1.
        btagweight_hf_down = 1.
        btagweight_lfstats1_up = 1.
        btagweight_lfstats1_down = 1.
        btagweight_hfstats1_up = 1.
        btagweight_hfstats1_down = 1.
        btagweight_lfstats2_up = 1.
        btagweight_lfstats2_down = 1.
        btagweight_hfstats2_up = 1.
        btagweight_hfstats2_down = 1.
        

        for jet in jets:
            pt = jet.pt
            eta = abs(jet.eta)
            jetid  = jet.jetId
            jetpid = jet.puId
            if not( jet.pt > self.jetPtMin and jet.eta < self.jetEtaMax and (jet.pt > 50 or jet.puId >= 4) and jet.jetId >= 2): continue
            btagweight               *= jet.btagSF_deepcsv_shape
            btagweight_jes_up        *= jet.btagSF_deepcsv_shape_up_jes
            btagweight_jes_down      *= jet.btagSF_deepcsv_shape_down_jes
            btagweight_lf_up         *= jet.btagSF_deepcsv_shape_up_lf
            btagweight_lf_down       *= jet.btagSF_deepcsv_shape_down_lf
            btagweight_hf_up         *= jet.btagSF_deepcsv_shape_up_hf
            btagweight_hf_down       *= jet.btagSF_deepcsv_shape_down_hf
            btagweight_lfstats1_up   *= jet.btagSF_deepcsv_shape_up_lfstats1
            btagweight_lfstats1_down *= jet.btagSF_deepcsv_shape_down_lfstats1
            btagweight_hfstats1_up   *= jet.btagSF_deepcsv_shape_up_hfstats1
            btagweight_hfstats1_down *= jet.btagSF_deepcsv_shape_down_hfstats1
            btagweight_lfstats2_up   *= jet.btagSF_deepcsv_shape_up_lfstats2
            btagweight_lfstats2_down *= jet.btagSF_deepcsv_shape_down_lfstats2
            btagweight_hfstats2_up   *= jet.btagSF_deepcsv_shape_up_hfstats2
            btagweight_hfstats2_down *= jet.btagSF_deepcsv_shape_down_hfstats2
                 
        self.out.fillBranch("BTagWeight",                 btagweight)
        # jes (jec)                                       
        self.out.fillBranch("BTagWeight_jes_up",          btagweight_jes_up)
        self.out.fillBranch("BTagWeight_jes_down",        btagweight_jes_down)
        # lf/hf (purity)                                  
        self.out.fillBranch("BTagWeight_lf_up",           btagweight_lf_up)
        self.out.fillBranch("BTagWeight_lf_down",         btagweight_lf_down)
        self.out.fillBranch("BTagWeight_hf_up",           btagweight_hf_up)
        self.out.fillBranch("BTagWeight_hf_down",         btagweight_hf_down)
        # lf/hf (stats)
        self.out.fillBranch("BTagWeight_lfstats1_up",     btagweight_lfstats1_up)
        self.out.fillBranch("BTagWeight_lfstats1_down",   btagweight_lfstats1_down)
        self.out.fillBranch("BTagWeight_hfstats1_up",     btagweight_hfstats1_up)
        self.out.fillBranch("BTagWeight_hfstats1_down",   btagweight_hfstats1_down)
        self.out.fillBranch("BTagWeight_lfstats2_up",     btagweight_lfstats2_up)
        self.out.fillBranch("BTagWeight_lfstats2_down",   btagweight_lfstats2_down)
        self.out.fillBranch("BTagWeight_hfstats2_up",     btagweight_hfstats2_up)
        self.out.fillBranch("BTagWeight_hfstats2_down",   btagweight_hfstats2_down)
        #
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
# btagSFWeight = lambda : BtagSFWeightProducer( "LooseWP_2016", "GPMVA90_2016")

