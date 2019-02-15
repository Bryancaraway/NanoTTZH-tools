import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class UpdateGenWeight(Module):
    def __init__(self, CrossSection, nEvent):
        self.xs = CrossSection
        self.nEvent = nEvent

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Stop0l_evtWeight",         "F", title="Storing cross section/nEvent for MC, lumi for Data")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        initgenWeight = getattr(event, "genWeight")

        sign          = 1 if initgenWeight > 0 else -1
        neweight = self.xs/self.nEvent * sign

        ### Store output
        self.out.fillBranch("Stop0l_evtWeight",        neweight)
        return True
