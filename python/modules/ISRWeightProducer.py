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
            print "ISRJet efficiency histograms for sample \"%s\" are not found in file \"%s\".  Using TTBar_2016 inclusive numbers as default setting!!!!"%( self.sampleName, self.isrEffFile)

            self.sampleName = "TTbarInc_2016"

            self.h_eff         = fin.Get(("NJetsISR_" + self.sampleName));
        

        
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("ISRWeight",      "F", title="ISRWeight calculated from a Jet and gen daughter matching")
        #self.out.branch("BTagWeight_Up",   "F", title="BTag event weight up uncertainty")
        #self.out.branch("BTagWeight_Down", "F", title="BTag event weight down uncertainty")
        self.out.branch("nISRJets",      "F", title="The number of jets that contain a unmatched jet to a gen particle")
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        jets = Collection(event, "Jet")
        genParts = Collection(event, "GenPart")
        ISRWeight = 1.0
        ISRWeightD = 1.0
        mother =-1
        daughter = [[] for x in range(0,len(genParts))]
        for iGenPart, genPart in enumerate(genParts):
            mother = genPart.genPartIdxMother
            if mother == -1: continue
            daughter[mother].append(iGenPart)
 
        nisr = 0
        for jet in jets:
            matched = False 
            for iGenPart, genPart in enumerate(genParts):
                if matched: break
                if genPart.statusFlags != 23 or abs(genPart.pdgId) > 5: continue
                momid = abs(genParts[genPart.genPartIdxMother].pdgId)
                if not (momid == 6 or momid == 23 or momid == 24 or momid == 25 or momid >1e6): continue
                for dau in daughter[iGenPart]:
                    dR = deltaR(jet,genParts[dau])
                    if dR<0.3:
                        matched = True
                        break
            if not matched:
                nisr+=1

        ISRWeight = self.h_eff.GetXaxis().FindBin(nisr);

        #if debug =True does this exist??
        #print "ISRWeight =",ISRWeight
        #print "nISRJets =",nisr
        #print "Index:"
        #print range(0,len(genParts))
        #print "genParts.pdgId:"
        #print [genPart.pdgId for genPart in genParts]
        #print "mother Idx:"
        #print [genPart.genPartIdxMother for genPart in genParts]
        #print "duaghter Idx:"
        #print daughter

        self.out.fillBranch("ISRWeight", ISRWeight)
        self.out.fillBranch("nISRJets", nisr)           
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
# lepSF = lambda : lepSFProducer( "LooseWP_2016", "GPMVA90_2016")

