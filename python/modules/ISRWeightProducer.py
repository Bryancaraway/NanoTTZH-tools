import ROOT
import os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import deltaPhi, deltaR, closest

class ISRSFWeightProducer(Module):

    def __init__(self, isrEffFile, sampleName, jetPtMin = 20, jetEtaMax = 2.4, fileDirectory = os.environ['CMSSW_BASE'] + "/src/PhysicsTools/NanoSUSYTools/data/isrSF/"):
        self.jetPtMin = jetPtMin
        self.jetEtaMax = jetEtaMax
        

        self.isrEffFile = isrEffFile
        self.sampleName = sampleName
        self.fileDirectory = fileDirectory

    def beginJob(self):
        ROOT.TH1.AddDirectory(False)
        
        fin = ROOT.TFile.Open(self.fileDirectory + "/" + self.isrEffFile)

        self.h_eff          = fin.Get(("NJetsISR_" + self.sampleName));
        #NJetsISR_eff          = fin.Get(("NJetsISR_" + self.sampleName));

        if not self.h_eff:
            print "ISRJet efficiency histograms for sample \"%s\" are not found in file \"%s\".  Using TTBar_2016 inclusive numbers as default setting!!!!"%( self.sampleName, self.iseEffFile)

            self.sampleName = "TTbar_HT_600to800_2016"

            self.h_eff         = fin.Get(("NJetsISR_" + self.sampleName));
        

        
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("ISRWeight",      "F", title="ISRWeight calculated from a Jet and gen daughter matching")
        #self.out.branch("BTagWeight_Up",   "F", title="BTag event weight up uncertainty")
        #self.out.branch("BTagWeight_Down", "F", title="BTag event weight down uncertainty")
        self.out.branch("nISRJets",      "F", title="The number of events that contain a none matched jet to a gen particle")
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        jets = Collection(event, "Jet")
        genPart = Collection(event, "GenPart")

        ISRWeightN = 1.0
        ISRWeightD = 1.0

        for jet in jets:
           pt = jet.pt
           eta = abs(jet.eta)
           for genPart in genParts:
              mother = genParts.genPartIdxMother
              if mother == -1: continue
              #if (genPart.statusFlags != 23 || abs(genParts.pdgId) > 5) continue
              for mother in mothers:
                 mother_pdgId = genParts.pdgId

              if not (mother_pdgId == 6 or mother_pdgId == 23 or mother_pdgId == 24 or mother_pdgId == 25 or mother_pdgId >1e6): continue
              daughter = mother.genParts
              print daughter
              daughter.at(mother).push_back(genParts)
              for daughter in daughters:
                 dR = jet.deltaR(genPart)
                 if dR<0.3:
                   matched = True
                   break
           if not matched:
             nisr+=1

        for nisr in nisrs:
            ISRWeight = self.h_eff.GetXaxis().FindBin(nisr);

        self.out.fillBranch("ISRWeight", ISRWeight)
        self.out.fillBranch("nISRJets", nisr)           
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
# lepSF = lambda : lepSFProducer( "LooseWP_2016", "GPMVA90_2016")

