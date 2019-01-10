import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
import numpy as np

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

#2016 MC: https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation80XReReco#Data_MC_Scale_Factors_period_dep
#2017 MC: https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation94X
DeepCSVMediumWP ={
    "2016" : 0.6324,
    "2017" : 0.4941,
}

class Stop0lObjectsProducer(Module):
    def __init__(self, era):
        self.era = era
        self.metBranchName = "MET"

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
        self.out.branch("SB_Stop0l",       "O", lenVar="nSB")
        self.out.branch("Jet_btagStop0l",  "O", lenVar="nJet")
        self.out.branch("FatJet_Stop0l",   "O", lenVar="nFatJet")
        self.out.branch("Photon_Stop0l",   "O", lenVar="nPhoton")
        self.out.branch("Jet_dPhiMET",     "F", lenVar="nJet")
        self.out.branch("Stop0l_HT",       "F")
        self.out.branch("Stop0l_Mtb",      "F")
        self.out.branch("Stop0l_Ptb",      "F")
        self.out.branch("Stop0l_METSig",   "F")
        self.out.branch("Stop0l_nJets",    "I")
        self.out.branch("Stop0l_nbtags",   "I")
        self.out.branch("Stop0l_nSoftb",   "I")

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
        global DeepCSVMediumWP
        if jet.btagDeepB < DeepCSVMediumWP[self.era]:
            return False
        return True

    def SelSoftb(self, isv):
        ## Select soft bs
        ## SV is not associate with selected jets
        if isv.JetIdx >0 and isv.JetIdx < len(self.Jet_Stop0l) and self.Jet_Stop0l[isv.JetIdx]:
            return False
        if isv.ntracks < 3 or math.fabs(isv.dxy)>3. or isv.dlenSig <4:
            return False
        if isv.DdotP < 0.98 :
            return False
        return True


    def SelJets(self, jet):
        if jet.pt < 20 or math.fabs(jet.eta) > 2.4 :
            return False
        return True

    def SelPhotons(self, photon):
        if photon.pt < 200:
            return False
        abeta = math.fabs(photon.eta)
        if (abeta > 1.442 and abeta < 1.566) or (abeta > 2.5):
            return False
        ## cut-base ID, 2^0 loose ID
        if not photon.cutBasedBitmap & 0b1:
            return False
        return True

    def CalHT(self, jets):
        HT = sum([j.pt for i, j in enumerate(jets) if self.Jet_Stop0l[i]])
        return HT

    def CalMTbPTb(self, jets, met):
        Mtb = float('inf')  #Max value
        Ptb = 0

        # Getting bjet, ordered by pt
        bjets = [ j for i,j in enumerate(jets) if self.BJet_Stop0l[i]]
        # Getting btag index, ordered by b discriminator value
        btagidx = sorted(range(len(bjets)), key=lambda k: bjets[k].btagDeepB , reverse=True)

        for i in range(min(len(bjets), 2)):
            Ptb += bjets[i].pt

        for i in range(min(len(btagidx), 2)):
            bj = bjets[btagidx[i]]
            Mtb = min(Mtb, math.sqrt( 2 * met.pt * bj.pt * (1 - math.cos(ROOT.TVector2.Phi_mpi_pi(met.phi-bj.phi)))))

        if Mtb == float('inf'):
            Mtb = 0
        return Mtb, Ptb


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        ## Getting objects
        electrons = Collection(event, "Electron")
        muons     = Collection(event, "Muon")
        isotracks = Collection(event, "IsoTrack")
        jets      = Collection(event, "Jet")
        isvs      = Collection(event, "SB")
        photons   = Collection(event, "Photon")
        met       = Object(event, self.metBranchName)
        flags     = Object(event, "Flag")

        ## Selecting objects
        self.Electron_Stop0l = map(self.SelEle, electrons)
        self.Muon_Stop0l     = map(self.SelMuon, muons)
        self.IsoTrack_Stop0l = map(lambda x : self.SelIsotrack(x, met), isotracks)
        self.Jet_Stop0l      = map(self.SelJets, jets)
        local_BJet_Stop0l    = map(self.SelBtagJets, jets)
        self.BJet_Stop0l     = [a and b for a, b in zip(self.Jet_Stop0l, local_BJet_Stop0l )]
        self.SB_Stop0l       = map(self.SelSoftb, isvs)
        self.Photon_Stop0l   = map(self.SelPhotons, photons)

        ## Jet variables
        jet_phi = np.asarray([jet.phi for jet in jets])
        Jet_dPhi = jet_phi - met.phi
        np.subtract(Jet_dPhi, 2*math.pi, out = Jet_dPhi, where= (Jet_dPhi >=math.pi))
        np.add(Jet_dPhi, 2*math.pi,  out =Jet_dPhi , where=(Jet_dPhi < -1*math.pi))
        np.fabs(Jet_dPhi, out=Jet_dPhi)
        ## TODO: Need to improve speed
        HT = self.CalHT(jets)
        Mtb, Ptb = self.CalMTbPTb(jets, met)

        ### Store output
        self.out.fillBranch("Electron_Stop0l", self.Electron_Stop0l)
        self.out.fillBranch("Muon_Stop0l",     self.Muon_Stop0l)
        self.out.fillBranch("IsoTrack_Stop0l", self.IsoTrack_Stop0l)
        self.out.fillBranch("Jet_btagStop0l",  self.BJet_Stop0l)
        self.out.fillBranch("Jet_Stop0l",      self.Jet_Stop0l)
        self.out.fillBranch("SB_Stop0l",       self.SB_Stop0l)
        self.out.fillBranch("Photon_Stop0l",   self.Photon_Stop0l)
        self.out.fillBranch("Jet_dPhiMET",     Jet_dPhi)
        self.out.fillBranch("Stop0l_HT",       HT)
        self.out.fillBranch("Stop0l_Mtb",      Mtb)
        self.out.fillBranch("Stop0l_Ptb",      Ptb)
        self.out.fillBranch("Stop0l_nJets",    sum(self.Jet_Stop0l))
        self.out.fillBranch("Stop0l_nbtags",   sum(self.BJet_Stop0l))
        self.out.fillBranch("Stop0l_nSoftb",   sum(self.SB_Stop0l))
        self.out.fillBranch("Stop0l_METSig",   met.pt / math.sqrt(HT) if HT > 0 else 0)
        return True


 # define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
