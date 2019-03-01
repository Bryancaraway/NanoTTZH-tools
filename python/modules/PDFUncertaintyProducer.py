import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class PDFUncertiantyProducer(Module):
    def __init__(self, isData):
        self.isData = isData

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        # For reading in type ROOT.TTreeReaderArray<float>, the postprocessor
        # can't read in the value properly for the first event in the root file
        # So we use below boolean to read it twice
        self.isFirstEventOfFile = True
        self.out = wrappedOutputTree
        self.out.branch("Stop0l_pdfWeightUp",   "F", title="PDF weight uncertainty up, scaled to central value")
        self.out.branch("Stop0l_pdfWeightDown", "F", title="PDF weight uncertainty down,, scaled to central value")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        if self.isData:
            return True
        PdfWs = getattr(event, "LHEPdfWeight")
        nPdfW = getattr(event, "nLHEPdfWeight")
        if self.isFirstEventOfFile:
            PdfWs = getattr(event, "LHEPdfWeight")
            nPdfW = getattr(event, "nLHEPdfWeight")
            self.isFirstEventOfFile = False

        lPdfWs = [PdfWs[i] for i in range(nPdfW)]
        maxW = max(lPdfWs)
        minW = min(lPdfWs)

        ## Setting the boundary to 50% to avoid large weight from
        ## To be decided, commented out for now
        # maxW = maxW if maxW < 1.5 else 1.5
        # minW = minW if minW > 0.5 else 0.5

        ### Store output
        self.out.fillBranch("Stop0l_pdfWeightUp",   maxW)
        self.out.fillBranch("Stop0l_pdfWeightDown", minW)
        return True
