import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math

import numpy as np
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

## Soft b tagging SF from Loukas
## https://indico.cern.ch/event/823731/contributions/3446301/attachments/1851612/3040016/lg-stop0L-softb-20190527.pdf
SoftB_SF = {
    "2016": (1.08, 0.03),
    "2017": (1.05, 0.06),
    "2018": (1.19, 0.06),
}
## Soft b taggging fullsim/fastsim SF from Sicheng
# https://indico.cern.ch/event/828647/contributions/3468642/attachments/1863702/3063958/Softb_ScaleFactors_190617.pdf
SoftB_fastSF = {
    "2016": (0.935, 0.062),
    "2017": (0.930, 0.018),
    "2018": (0.932, 0.023),
}



## Deep Top SF from Loukas
## https://indico.cern.ch/event/828647/contributions/3468598/attachments/1863686/3063744/lg-hot-deepak8sf-20190617.pdf
## Also from Stop1lep AN2019_003_v11, Table 38
DeepTop_SF = {
    "2016" : {
        (400, 480)  : (1.01, 0.11),
        (480, 600)  : (1.05, 0.08),
        (600, 1200) : (1.06, 0.05),
    },
    "2017" : {
        (400, 480)  : (1.08, 0.10),
        (480, 600)  : (0.97, 0.07),
        (600, 1200) : (1.02, 0.08),
    },
    "2018" : {
        (400, 480)  : (0.95, 0.07),
        (480, 600)  : (1.06, 0.05),
        (600, 1200) : (0.94, 0.05),
    }
}
## from Stop1lep AN2019_003_v11, Table 39
DeepTop_fastSF = {
    "2016" : {
        (400,  480)  : (1.12, 0.15),
        (480,  600)  : (0.99, 0.06),
        (600,  1200) : (0.96, 0.04),
        (1200, 9999) : (0.92, 0.02),
    },
    "2017" : {
        (400,  480)  : (1.01, 0.11),
        (480,  600)  : (0.95, 0.04),
        (600,  1200) : (1.00, 0.04),
        (1200, 9999) : (0.96, 0.02),
    },
    "2018" : {
        (400, 480)  : (0.80, 0.08),
        (480, 600)  : (1.03, 0.06),
        (600, 1200) : (1.03, 0.04),
        (600, 1200) : (1.03, 0.04),
    }
}

# Get it from https://indico.cern.ch/event/840827/contributions/3527925/attachments/1895214/3126510/DeepAK8_Top_W_SFs_2017_JMAR_PK.pdf
# No direct value, get it from the png using http://www.graphreader.com/
# NOTE: Take it with a grain of salt
# No 2018 yet, using 2017 value as 2018
DeepW_SF = {
    "2016" : {
        (200, 300) : (0.875, 0.146),
        (300, 400) : (0.966, 0.132),
        (400, 800) : (0.817, 0.112),
    },
    "2017" : {
        (200, 300) : (0.857, 0.032),
        (300, 400) : (0.852, 0.033),
        (400, 800) : (0.877, 0.045),
    },
    "2018" : {
        (200, 300) : (0.857, 0.032),
        (300, 400) : (0.852, 0.033),
        (400, 800) : (0.877, 0.045),
    }
}
## Dummy value for now
DeepW_fastSF = {
    "2016" : {
        (200, 300) : (1.0, 0.01),
        (300, 400) : (1.0, 0.01),
        (400, 800) : (1.0, 0.01),
    },
    "2017" : {
        (200, 300) : (1.0, 0.01),
        (300, 400) : (1.0, 0.01),
        (400, 800) : (1.0, 0.01),
    },
    "2018" : {
        (200, 300) : (1.0, 0.01),
        (300, 400) : (1.0, 0.01),
        (400, 800) : (1.0, 0.01),
    }
}

class SoftBDeepAK8SFProducer(Module):
    def __init__(self, era, isData = False, isFastSim=False):
        self.era = era
        self.isFastSim = isFastSim
        self.isData = isData

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("SB_SF"        , "F", lenVar="nSB",       limitedPrecision=12)
        self.out.branch("SB_SFerr"     , "F", lenVar="nSB",       limitedPrecision=12)
        self.out.branch("SB_fastSF"    , "F", lenVar="nSB",       limitedPrecision=12)
        self.out.branch("SB_fastSFerr" , "F", lenVar="nSB",       limitedPrecision=12)
        self.out.branch("FatJet_SF"        , "F", lenVar="nFatJet",       limitedPrecision=12)
        self.out.branch("FatJet_SFerr"     , "F", lenVar="nFatJet",       limitedPrecision=12)
        self.out.branch("FatJet_fastSF"    , "F", lenVar="nFatJet",       limitedPrecision=12)
        self.out.branch("FatJet_fastSFerr" , "F", lenVar="nFatJet",       limitedPrecision=12)

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def GetSoftBSF(self, sbs):
        stop0l       = np.fromiter([sb.Stop0l for sb in sbs], bool)
        nsb          = len(stop0l)
        sb_sf        = [1.] * nsb
        sb_sferr     = [0.] * nsb
        sb_fastsf    = [1.] * nsb
        sb_fastsferr = [0.] * nsb

        if self.isData:
            return sb_sf, sb_sferr, sb_fastsf, sb_fastsferr

        sb_sf  = stop0l * SoftB_SF[self.era][0]
        sb_sferr  = stop0l * SoftB_SF[self.era][1]
        if self.isFastSim:
            sb_fastsf  = stop0l * SoftB_fastSF[self.era][0]
            sb_fastsferr  = stop0l * SoftB_fastSF[self.era][1]

        return sb_sf, sb_sferr, sb_fastsf, sb_fastsferr

    def GetDeepAK8SF(self, fjets):
        stop0l        = np.fromiter([fj.Stop0l for fj in fjets ], int)
        ntop          = len(stop0l)
        top_sf        = [1.] * ntop
        top_sferr     = [0.] * ntop
        top_fastsf    = [1.] * ntop
        top_fastsferr = [0.] * ntop

        if self.isData:
            return top_sf, top_sferr, top_fastsf, top_fastsferr

        for i,  fj in enumerate(fjets):
            if fj.Stop0l == 1:
                for k, v in DeepTop_SF[self.era].items():
                    if fj.pt >= k[0] and fj.pt < k[1]:
                        top_sf[i] = v[0]
                        top_sferr[i]= v[1]
                if self.isFastSim:
                    for k, v in DeepTop_fastSF[self.era].items():
                        if fj.pt >= k[0] and fj.pt < k[1]:
                            top_fastsf[i]= v[0]
                            top_fastsferr[i] = v[1]
            elif fj.Stop0l == 2:
                for k, v in DeepW_SF[self.era].items():
                    if fj.pt >= k[0] and fj.pt < k[1]:
                        top_sf[i] = v[0]
                        top_sferr[i] = v[1]
                if self.isFastSim:
                    for k, v in DeepW_fastSF[self.era].items():
                        if fj.pt >= k[0] and fj.pt < k[1]:
                            top_fastsf[i] = v[0]
                            top_fastsferr[i] = v[1]
        # print (top_sf, top_sferr, top_fastsf, top_fastsferr)
        return top_sf, top_sferr, top_fastsf, top_fastsferr



    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        isvs    = Collection(event, "SB")
        fatjets  = Collection(event, "FatJet")

        sb_sf, sb_sferr, sb_fastsf, sb_fastsferr = self.GetSoftBSF(isvs)
        top_sf, top_sferr, top_fastsf, top_fastsferr = self.GetDeepAK8SF(fatjets)

        ### Store output
        self.out.fillBranch("SB_SF",        sb_sf)
        self.out.fillBranch("SB_SFerr",     sb_sferr)
        self.out.fillBranch("SB_fastSF",    sb_fastsf)
        self.out.fillBranch("SB_fastSFerr", sb_fastsferr)
        self.out.fillBranch("FatJet_SF",        top_sf)
        self.out.fillBranch("FatJet_SFerr",     top_sferr)
        self.out.fillBranch("FatJet_fastSF",    top_fastsf)
        self.out.fillBranch("FatJet_fastSFerr", top_fastsferr)

        return True
