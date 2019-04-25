import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
import numpy as np

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class FastsimVarProducer(Module):
    def __init__(self, isFastsim):
        self.isFastsim = isFastsim

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        if not self.isFastsim:
            return True
        self.out = wrappedOutputTree
        self.out.branch("MET_pt",            "F")
        self.out.branch("MET_pt_fasterr",    "F")
        self.out.branch("Stop0l_MotherMass", "F")
        self.out.branch("Stop0l_LSPMass",    "F")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        if not self.isFastsim:
            return True

        met    = Object(event, "MET")
        genmet = Object(event, "GenMET")
        genpar = Object(event, "GenPart")

        fastmet = (met.pt + genmet.pt)/2.0
        fastmet_err = math.fabs(fastmet - met.pt)

        # print(type(genpar.status))
        # status = genpar.status == 62
        # print(type(status))
        mothermass = np.unique(genpar.mass[(genpar.status == 62) & (np.absolute(genpar.pdgId) >  1000000    ) ] )
        LSPmass    = np.unique(genpar.mass[(genpar.status == 1)  & (genpar.pdgId              == 1000022)])
        if mothermass.shape != (1,) or LSPmass.shape != (1,):
            print("Not pair SUSY? Danger!")

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Store output ~~~~~
        self.out.fillBranch("MET_pt", fastmet)
        self.out.fillBranch("MET_pt_fasterr", fastmet_err)
        self.out.fillBranch("Stop0l_MotherMass", mothermass[0])
        self.out.fillBranch("Stop0l_LSPMass", LSPmass[0])
