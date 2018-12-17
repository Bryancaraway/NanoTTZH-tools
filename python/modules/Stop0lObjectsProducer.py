import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class Stop0lObjectsProducer(Module):
    def __init__(self, era):
        self.era = era
        self.metBranchName = "MET"
        #2016 MC: https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation80XReReco#Data_MC_Scale_Factors_period_dep
        #2017 MC: https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation94X
        self.DeepCSVMediumWP ={
            "2016" : 0.8484,
            "2017" : 0.8838
        }

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Electron_Stop0l", "O", lenVar="nElectron", title="cutBased Veto ID with miniISO < 0.1, pT > 5")
        self.out.branch("Muon_Stop0l",     "O", lenVar="nMuon")
        self.out.branch("IsoTrack_Stop0l", "O", lenVar="nIsoTrack")
        self.out.branch("Photon_Stop0l",   "O", lenVar="nPhoton")
        self.out.branch("Jet_Stop0l",      "O", lenVar="nJet")
        self.out.branch("Jet_btagStop0l",  "O", lenVar="nJet")
        self.out.branch("FatJet_Stop0l",   "O", lenVar="nFatJet")
        self.out.branch("Jet_dPhiMET",     "F", lenVar="nJet")
        self.out.branch("HT_Stop0l",       "F")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def SelEle(self, ele):
        if math.fabs(ele.eta) > 2.5 or ele.pt < 5:
            return False
        ## Veto ID electron
        if ele.cutBasedNoIso < 1:
            return False
        ## MiniIso < 0.1
        if ele.miniPFRelIso_all > 0.1:
            return False
        return True

    def SelMuon(self, mu):
        ## NanoAOD store loose ID Muon by default
        if math.fabs(mu.eta) > 2.4 or mu.pt < 5:
            return False
        ## MiniIso < 0.1
        if mu.miniPFRelIso_all > 0.2:
            return False
        return True

    def SelIsotrack(self, isk, met):
        iso = isk.pfRelIso03_chg/isk.pt
        if abs(isk.pdgId) == 11 or abs(isk.pdgId) == 13:
            if isk.pt < 5 or iso > 0.2:
                return False
        if abs(isk.pdgId) == 211:
            if isk.pt < 10 or iso > 0.1:
                return False
        mtW = math.sqrt( 2 * met.pt * isk.pt * (1 - math.cos(met.phi-isk.phi)))
        if mtW  > 100:
            return False
        return True

    def SelBtagJets(self, jet):
        if jet.btagDeepB < self.DeepCSVMediumWP[self.era]:
            return False
        return True

    def SelJets(self, jet):
        if jet.pt < 20 or math.fabs(jet.eta) > 2.4 :
            return False
        return True

    def CalHT(self, jets, Jet_Stop0l):
        HT = sum([j.pt for i, j in enumerate(jets) if Jet_Stop0l[i]])
        return HT


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        ## Getting objects
        electrons = Collection(event, "Electron")
        muons     = Collection(event, "Muon")
        isotracks = Collection(event, "IsoTrack")
        jets      = Collection(event, "Jet")
        met       = Object(event, self.metBranchName)
        flags     = Object(event, "Flag")

        ## Selecting objects
        Electron_Stop0l = map(self.SelEle, electrons)
        Muon_Stop0l     = map(self.SelMuon, muons)
        IsoTrack_Stop0l = map(lambda x : self.SelIsotrack(x, met), isotracks)
        BJet_Stop0l     = map(self.SelBtagJets, jets)
        Jet_Stop0l      = map(self.SelJets, jets)

        ## Jet variables
        ## TODO: Need to improve speed
        Jet_dPhi = [math.fabs(ROOT.TVector2.Phi_mpi_pi( jet.phi - met.phi )) for jet in jets]
        HT = self.CalHT(jets, Jet_Stop0l)

        ### Store output
        self.out.fillBranch("Electron_Stop0l", Electron_Stop0l)
        self.out.fillBranch("Muon_Stop0l",     Muon_Stop0l)
        self.out.fillBranch("IsoTrack_Stop0l", IsoTrack_Stop0l)
        self.out.fillBranch("Jet_btagStop0l",  BJet_Stop0l)
        self.out.fillBranch("Jet_Stop0l",      Jet_Stop0l)
        self.out.fillBranch("Jet_dPhiMET",     Jet_dPhi)
        self.out.fillBranch("HT_Stop0l",       HT)
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
