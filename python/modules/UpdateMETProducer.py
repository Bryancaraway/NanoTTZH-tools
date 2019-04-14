import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module


class UpdateMETProducer(Module):
    def __init__(self, metBranchName):
        self.metBranchName = metBranchName

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree

        # Copying METFixEE2017 to MET for 2017 Data/MC
        self.out.branch("MET_phi",                  "F")
        self.out.branch("MET_pt",                   "F")
        self.out.branch("MET_sumEt",                "F")
        self.out.branch("MET_MetUnclustEnUpDeltaX", "F")
        self.out.branch("MET_MetUnclustEnUpDeltaY", "F")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def CopyMETFix(self, METFixEE):
        return True

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        ## Getting objects
        met       = Object(event, self.metBranchName)

        self.out.fillBranch("MET_phi", met.phi)
        self.out.fillBranch("MET_pt", met.pt)
        self.out.fillBranch("MET_sumEt", met.sumEt)
        self.out.fillBranch("MET_MetUnclustEnUpDeltaX", met.MetUnclustEnUpDeltaX)
        self.out.fillBranch("MET_MetUnclustEnUpDeltaY", met.MetUnclustEnUpDeltaY)

        return True


 # define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
