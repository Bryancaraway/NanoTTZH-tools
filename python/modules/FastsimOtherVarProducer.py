import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
import numpy as np

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoSUSYTools.modules.datamodelRemap import ObjectRemapped

class FastsimOtherVarProducer(Module):
    def __init__(self, isFastsim, applyUncert = None):
        self.metBranchName = "MET"
        self.isFastsim = isFastsim
        self.applyUncert = applyUncert
        self.suffix = ""
        if self.applyUncert == "JESUp":
            self.suffix = "_JESUp"
        elif self.applyUncert == "METUnClustUp":
            self.suffix = "_METUnClustUp"
        elif self.applyUncert == "JESDown":
            self.suffix = "_JESDown"
        elif self.applyUncert == "METUnClustDown":
            self.suffix = "_METUnClustDown"

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        if not self.isFastsim:
            return True
        self.out = wrappedOutputTree
        if self.applyUncert == "JESUp":
            self.out.branch("MET_pt_jesTotalUp", "F")
        elif self.applyUncert == "JESDown":
            self.out.branch("MET_pt_jesTotalDown", "F")
        elif self.applyUncert == "METUnClustUp":
            self.out.branch("MET_pt_unclustEnUp", "F")
        elif self.applyUncert == "METUnClustDown":
            self.out.branch("MET_pt_unclustEnDown", "F")
        else:
            self.out.branch("MET_pt",            "F")
            self.out.branch("MET_pt_fasterr",    "F")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        if not self.isFastsim:
            return True

        if self.applyUncert == "JESUp":
            met       = ObjectRemapped(event, self.metBranchName, replaceMap={"pt":"pt_jesTotalUp", "phi":"phi_jesTotalUp"})
        elif self.applyUncert == "JESDown":
            met       = ObjectRemapped(event, self.metBranchName, replaceMap={"pt":"pt_jesTotalDown", "phi":"phi_jesTotalDown"})
        elif self.applyUncert == "METUnClustUp":
            met       = ObjectRemapped(event, self.metBranchName, replaceMap={"pt":"pt_unclustEnUp", "phi":"phi_unclustEnUp"})
        elif self.applyUncert == "METUnClustDown":
            met       = ObjectRemapped(event, self.metBranchName, replaceMap={"pt":"pt_unclustEnDown", "phi":"phi_unclustEnDown"})
        else:
            met       = Object(event, self.metBranchName)

        genmet = Object(event, "GenMET")

        fastmet = (met.pt + genmet.pt)/2.0
        fastmet_err = math.fabs(fastmet - met.pt)

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Store output ~~~~~
        if self.applyUncert == "JESUp":
            self.out.fillBranch("MET_pt_jesTotalUp", fastmet)
        elif self.applyUncert == "JESDown":
            self.out.fillBranch("MET_pt_jesTotalDown", fastmet)
        elif self.applyUncert == "METUnClustUp":
            self.out.fillBranch("MET_pt_unclustEnUp", fastmet)
        elif self.applyUncert == "METUnClustDown":
            self.out.fillBranch("MET_pt_unclustEnDown", fastmet)
        else:
            self.out.fillBranch("MET_pt", fastmet)
            self.out.fillBranch("MET_pt_fasterr", fastmet_err)

        return True
