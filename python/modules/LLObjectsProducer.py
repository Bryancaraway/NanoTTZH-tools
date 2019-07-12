import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
import numpy as np

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import deltaPhi, deltaR, closest

#2016 MC: https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation80XReReco#Data_MC_Scale_Factors_period_dep
#2017 MC: https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation94X

DeepCSVLooseWP = {
    "2016" : 0.2217,
    "2017" : 0.1522,
    "2018" : 0.1241
}

DeepCSVMediumWP ={
    "2016" : 0.6324,
    "2017" : 0.4941,
    "2018" : 0.4184
}

CSVv2MediumWP = {
    "2016" : 0.8484,
    "2017" : 0.8838,
    "2018" : 0.8838  # Not recommended, use 2017 as temp
}


class LLObjectsProducer(Module):
    def __init__(self, era, isData = False):
        self.era = era
	self.isData = isData
        self.metBranchName = "MET"
        # EE noise mitigation in PF MET
        # https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1865.html
        if self.era == "2017":
            self.metBranchName = "METFixEE2017"

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
	self.out.branch("Stop0l_nJets_HighPt",  		"I")
	self.out.branch("Stop0l_nJets30",  			"I")
	self.out.branch("Stop0l_nbtags_Loose",  		"I")
	self.out.branch("Stop0l_MtLepMET", 			"F")
	self.out.branch("nLeptonVeto",    			"I")
	self.out.branch("Stop0l_nIsoTracksLep", 		"I")
	self.out.branch("Stop0l_nIsoTracksHad", 		"I")
	self.out.branch("Stop0l_nIsoTracksHad_ptgeq20", 	"I")
	self.out.branch("Stop0l_nVetoElec", 			"I")
	self.out.branch("Stop0l_nVetoMuon", 			"I")
	self.out.branch("Stop0l_nVetoElecMuon", 		"I")
	self.out.branch("Pass_dPhiMETMedDM", 			"O")
	self.out.branch("Stop0l_dPhiISRMET",			"F")
	self.out.branch("Stop0l_TauPOG",			"I")
	if not self.isData:
		self.out.branch("Stop0l_GenVisTau",			"I")
		self.out.branch("Stop0l_GenVisTau_pt10to20",		"I")
		self.out.branch("Stop0l_GenVisTau_ptgeq20",		"I")
		self.out.branch("Stop0l_GenVisTau_1Prong0PiZero",	"I")
		self.out.branch("Stop0l_GenVisTau_1Prong1PiZero",	"I")
		self.out.branch("Stop0l_GenVisTau_1Prong2PiZero",	"I")
		self.out.branch("Stop0l_GenVisTau_3Prong0PiZero",	"I")
		self.out.branch("Stop0l_GenVisTau_3Prong1PiZero",	"I")
		self.out.branch("Stop0l_GenVisTau_other",		"I")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def SelMtlepMET(self, ele, muon, isks, met):
	mt = 0.0
	for l in ele:
		if l.Stop0l: mt += math.sqrt( 2 * l.pt * met.pt * (1 - np.cos(deltaPhi(l.phi,met.phi))))
	for l in muon:
		if l.Stop0l: mt += math.sqrt( 2 * l.pt * met.pt * (1 - np.cos(deltaPhi(l.phi,met.phi))))
	for l in isks:
		if l.Stop0l: mt += math.sqrt( 2 * l.pt * met.pt * (1 - np.cos(deltaPhi(l.phi,met.phi))))
	return mt

    def SelJets(self, jet):
        if jet.pt < 20 or math.fabs(jet.eta) > 2.4 :
            return False
        return True

    def SelJets30(self, jet):
        if jet.pt < 30 or math.fabs(jet.eta) > 2.4 :
            return False
        return True

    def SelJetsHighPt(self, jet):
        if jet.pt < 75 or math.fabs(jet.eta) > 2.4 :
            return False
        return True

    def SelBtagJets(self, jet):
        global DeepCSVLooseWP
        if jet.btagDeepB >= DeepCSVLooseWP[self.era]:
            return True
        return False

    def GetJetSortedIdx(self, jets):
        ptlist = []
        dphiMET = []
        for j in jets:
            if math.fabs(j.eta) > 4.7 or j.pt < 20:
                pass
            else:
                ptlist.append(j.pt)
                dphiMET.append(j.dPhiMET)
        return [dphiMET[j] for j in np.argsort(ptlist)[::-1]]

    def PassdPhi(self, sortedPhi, dPhiCuts, invertdPhi =False):
        if invertdPhi:
            return any( a < b for a, b in zip(sortedPhi, dPhiCuts))
        else:
            return all( a > b for a, b in zip(sortedPhi, dPhiCuts))

    def SelTauPOG(self, tau):
	if tau.pt < 20 or abs(tau.eta) > 2.4 or not tau.idDecayMode or not (tau.idMVAoldDM2017v2 & 8):
		return False
	return True

    def SelGenTau(self, gentau):
	if gentau.pt < 10 or abs(gentau.eta) > 2.4:
		return False
	return True

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        ## Getting objects
        electrons = Collection(event, "Electron")
        muons     = Collection(event, "Muon")
        isotracks = Collection(event, "IsoTrack")
	muons     = Collection(event, "Muon")
	electrons = Collection(event, "Electron")
	jets      = Collection(event, "Jet")
	met       = Object(event, self.metBranchName)
	#tau	  = Collection(event, "Tau")
	if not self.isData:
		gentau	  = Collection(event, "GenVisTau")
	stop0l    = Object(event, "Stop0l")
	fatjets   = Collection(event, "FatJet")

        ## Selecting objects
	self.Jet_Stop0lHighPt= map(self.SelJetsHighPt, jets)
	self.Jet_Stop0l      = map(self.SelJets, jets)
	self.Jet_Stop0l30    = map(self.SelJets30, jets)
	local_BJet_Stop0l    = map(self.SelBtagJets, jets)
        self.BJet_Stop0l     = [a and b for a, b in zip(self.Jet_Stop0l, local_BJet_Stop0l )]
	mt 		     = self.SelMtlepMET(electrons, muons, isotracks, met)
	countIskLep 	     = sum([(i.Stop0l and (abs(i.pdgId) == 11 or abs(i.pdgId) == 13)) for i in isotracks])
	countIskHad 	     = sum([(i.Stop0l and abs(i.pdgId) == 211) for i in isotracks])
	countIskHad_ptgeq20  = sum([(i.Stop0l and abs(i.pdgId) == 211 and i.pt > 20) for i in isotracks])
	countEle	     = sum([e.Stop0l for e in electrons])
	countMuon	     = sum([m.Stop0l for m in muons])
	sortedPhi 	     = self.GetJetSortedIdx(jets)
        PassdPhiMedDM        = self.PassdPhi(sortedPhi, [0.15, 0.15, 0.15], invertdPhi=True)
	dphiISRMet	     = abs(deltaPhi(fatjets[stop0l.ISRJetIdx].phi, met.phi)) if stop0l.ISRJetIdx >= 0 else -1
	#self.Tau_Stop0l      = map(self.SelTauPOG, tau)
	#countTauPOG	     = sum(self.Tau_Stop0l)
	if not self.isData:
		self.GenVisTau_Stop0l= map(self.SelGenTau, gentau)
		countGenTau	     = sum(self.GenVisTau_Stop0l)
		countGenTau_pt10to20  =sum([g.pt > 10 and g.pt < 20 and gt for g, gt in zip(gentau, self.GenVisTau_Stop0l)])
		countGenTau_ptgeq20  = sum([g.pt > 20 and gt for g, gt in zip(gentau, self.GenVisTau_Stop0l)])
		countGenTau_1Prong0PiZero  = sum([g.status == 0  and gt for g, gt in zip(gentau, self.GenVisTau_Stop0l)])
		countGenTau_1Prong1PiZero  = sum([g.status == 1  and gt for g, gt in zip(gentau, self.GenVisTau_Stop0l)])
		countGenTau_1Prong2PiZero  = sum([g.status == 2  and gt for g, gt in zip(gentau, self.GenVisTau_Stop0l)])
		countGenTau_3Prong0PiZero  = sum([g.status == 10 and gt for g, gt in zip(gentau, self.GenVisTau_Stop0l)])
		countGenTau_3Prong1PiZero  = sum([g.status == 11 and gt for g, gt in zip(gentau, self.GenVisTau_Stop0l)])
		countGenTau_other	   = sum([g.status == 15 and gt for g, gt in zip(gentau, self.GenVisTau_Stop0l)])

        ### Store output
	self.out.fillBranch("Stop0l_nJets_HighPt",    	sum(self.Jet_Stop0lHighPt))
	self.out.fillBranch("Stop0l_nJets30",    	sum(self.Jet_Stop0l30))
	self.out.fillBranch("Stop0l_nbtags_Loose",   	sum(self.BJet_Stop0l))
	self.out.fillBranch("Stop0l_MtLepMET",  	mt)
	self.out.fillBranch("nLeptonVeto",    		countMuon + countEle + countIskLep)
	self.out.fillBranch("Stop0l_nIsoTracksLep",	countIskLep)
	self.out.fillBranch("Stop0l_nIsoTracksHad",	countIskHad)
	self.out.fillBranch("Stop0l_nIsoTracksHad_ptgeq20",	countIskHad_ptgeq20)
	self.out.fillBranch("Stop0l_nVetoElec", 	countEle)
	self.out.fillBranch("Stop0l_nVetoMuon", 	countMuon)
	self.out.fillBranch("Stop0l_nVetoElecMuon", 	countEle + countMuon)
	self.out.fillBranch("Pass_dPhiMETMedDM", 	PassdPhiMedDM)
	self.out.fillBranch("Stop0l_dPhiISRMET",	dphiISRMet)
	#self.out.fillBranch("Stop0l_TauPOG",		countTauPOG)
	if not self.isData:
		self.out.fillBranch("Stop0l_GenVisTau",		countGenTau)
		self.out.fillBranch("Stop0l_GenVisTau_pt10to20",countGenTau_pt10to20)
		self.out.fillBranch("Stop0l_GenVisTau_ptgeq20",	countGenTau_ptgeq20)
		self.out.fillBranch("Stop0l_GenVisTau_1Prong0PiZero",		countGenTau_1Prong0PiZero)
		self.out.fillBranch("Stop0l_GenVisTau_1Prong1PiZero",		countGenTau_1Prong1PiZero)
		self.out.fillBranch("Stop0l_GenVisTau_1Prong2PiZero",		countGenTau_1Prong2PiZero)
		self.out.fillBranch("Stop0l_GenVisTau_3Prong0PiZero",		countGenTau_3Prong0PiZero)
		self.out.fillBranch("Stop0l_GenVisTau_3Prong1PiZero",		countGenTau_3Prong1PiZero)
		self.out.fillBranch("Stop0l_GenVisTau_other",			countGenTau_other)
	return True


 # define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
