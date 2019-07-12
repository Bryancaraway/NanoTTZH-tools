import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class UpdateEvtWeightSmear(Module):
    def __init__(self, isData, CrossSection, nEvent, Process):
        self.isData = isData
        self.xs = CrossSection
        self.nEvent = nEvent
        self.process = Process

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree, outputFileSmear, outputTreeSmear):
        self.out = wrappedOutputTree
	self.outsmear = outputTreeSmear
        if self.isData:
            infostr = "Storing lumi for %s (Lumi=%f)" % (self.process, self.xs)
        else:
            infostr = "Storing cross section/nEvent for %s (CrossSection=%f, nEvent=%f)" % (self.process, self.xs, self.nEvent)
        self.out.branch("Stop0l_evtWeight",         "F", title=infostr)
        self.outsmear.branch("Stop0l_evtWeight",    "F", title=infostr)

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        sign = 1
        if not self.isData:
            initgenWeight = getattr(event, "genWeight")
            sign          = 1 if initgenWeight > 0 else -1

        neweight = self.xs/self.nEvent * sign

        ### Store output
        self.out.fillBranch("Stop0l_evtWeight",        neweight)
        self.outsmear.fillBranch("Stop0l_evtWeight",   neweight)
        return True
