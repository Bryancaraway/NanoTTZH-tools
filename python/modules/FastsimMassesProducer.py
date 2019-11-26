import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
import numpy as np

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoSUSYTools.modules.datamodelRemap import ObjectRemapped

class FastsimMassesProducer(Module):
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
        self.out.branch("Stop0l_MotherMass", "F")
        self.out.branch("Stop0l_LSPMass",    "F")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        if not self.isFastsim:
            return True

        genpar = Collection(event, "GenPart")

        mass = np.asarray([g.mass for g in genpar])
        pdgId = np.asarray([g.pdgId for g in genpar])
        status = np.asarray([g.status for g in genpar])
        mothermass = np.unique(mass[(status == 62) & (np.absolute(pdgId) >  1000000    ) ] )
        LSPmass    = np.unique(mass[(status == 1)  & (pdgId              == 1000022)])
        if mothermass.shape != (1,) or LSPmass.shape != (1,):
            print("Danger: mothermass or LSPmass is not unique")

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Store output ~~~~~
        self.out.fillBranch("Stop0l_MotherMass", mothermass[0])
        self.out.fillBranch("Stop0l_LSPMass", LSPmass[0])
        return True

