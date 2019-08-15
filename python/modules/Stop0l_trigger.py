import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
import os
import numpy as np

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class Stop0l_trigger(Module):
    def __init__(self, era, isData = False):
        self.maxEvents = -1
        self.nEvents = 0
        self.era = era
	self.isData = isData
        eff_file = "%s/src/PhysicsTools/NanoSUSYTools/data/trigger_eff/" % os.environ['CMSSW_BASE']
        eff_file = eff_file + self.era + "_trigger_eff.root"
        self.tf = ROOT.TFile.Open(eff_file)

        ## Keep the TGraph in memory
        histo_name_list = ["MET_loose_baseline", "MET_high_dm", "MET_low_dm",
			   "MET_loose_baseline_QCD", "MET_high_dm_QCD", "MET_low_dm_QCD",
			   "Electron_pt", "Electron_eta", "Muon_pt", "Muon_eta", 
                           "Photon_pt", "Photon_eta", "Zmumu_pt", "Zee_pt"]
        self.effs = { }
        for histo_name in histo_name_list:
            self.effs[histo_name] = self.tf.Get(histo_name)

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Pass_trigger_MET", "O")
        self.out.branch("Pass_trigger_muon", "O")
        self.out.branch("Pass_trigger_electron", "O")
        self.out.branch("Pass_trigger_photon", "O")

        self.out.branch("Stop0l_trigger_eff_MET_loose_baseline", "F")
        self.out.branch("Stop0l_trigger_eff_MET_loose_baseline_down", "F")
        self.out.branch("Stop0l_trigger_eff_MET_loose_baseline_up", "F")
        self.out.branch("Stop0l_trigger_eff_MET_low_dm", "F")
        self.out.branch("Stop0l_trigger_eff_MET_low_dm_down", "F")
        self.out.branch("Stop0l_trigger_eff_MET_low_dm_up", "F")
        self.out.branch("Stop0l_trigger_eff_MET_high_dm", "F")
        self.out.branch("Stop0l_trigger_eff_MET_high_dm_down", "F")
        self.out.branch("Stop0l_trigger_eff_MET_high_dm_up", "F")

        self.out.branch("Stop0l_trigger_eff_MET_loose_baseline_QCD", "F")
        self.out.branch("Stop0l_trigger_eff_MET_loose_baseline_QCD_down", "F")
        self.out.branch("Stop0l_trigger_eff_MET_loose_baseline_QCD_up", "F")
        self.out.branch("Stop0l_trigger_eff_MET_low_dm_QCD", "F")
        self.out.branch("Stop0l_trigger_eff_MET_low_dm_QCD_down", "F")
        self.out.branch("Stop0l_trigger_eff_MET_low_dm_QCD_up", "F")
        self.out.branch("Stop0l_trigger_eff_MET_high_dm_QCD", "F")
        self.out.branch("Stop0l_trigger_eff_MET_high_dm_QCD_down", "F")
        self.out.branch("Stop0l_trigger_eff_MET_high_dm_QCD_up", "F")

        self.out.branch("Stop0l_trigger_eff_Electron_pt", "F")
        self.out.branch("Stop0l_trigger_eff_Electron_pt_down", "F")
        self.out.branch("Stop0l_trigger_eff_Electron_pt_up", "F")
        self.out.branch("Stop0l_trigger_eff_Electron_eta", "F")
        self.out.branch("Stop0l_trigger_eff_Electron_eta_down", "F")
        self.out.branch("Stop0l_trigger_eff_Electron_eta_up", "F")
        self.out.branch("Stop0l_trigger_eff_Muon_pt", "F")
        self.out.branch("Stop0l_trigger_eff_Muon_pt_down", "F")
        self.out.branch("Stop0l_trigger_eff_Muon_pt_up", "F")
        self.out.branch("Stop0l_trigger_eff_Muon_eta", "F")
        self.out.branch("Stop0l_trigger_eff_Muon_eta_down", "F")
        self.out.branch("Stop0l_trigger_eff_Muon_eta_up", "F")
        self.out.branch("Stop0l_trigger_eff_Photon_pt", "F")
        self.out.branch("Stop0l_trigger_eff_Photon_pt_down", "F")
        self.out.branch("Stop0l_trigger_eff_Photon_pt_up", "F")
        self.out.branch("Stop0l_trigger_eff_Photon_eta", "F")
        self.out.branch("Stop0l_trigger_eff_Photon_eta_down", "F")
        self.out.branch("Stop0l_trigger_eff_Photon_eta_up", "F")

        self.out.branch("Stop0l_trigger_eff_Zee_pt", "F")
        self.out.branch("Stop0l_trigger_eff_Zee_pt_down", "F")
        self.out.branch("Stop0l_trigger_eff_Zee_pt_up", "F")
        self.out.branch("Stop0l_trigger_eff_Zmumu_pt", "F")
        self.out.branch("Stop0l_trigger_eff_Zmumu_pt_down", "F")
        self.out.branch("Stop0l_trigger_eff_Zmumu_pt_up", "F")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def mygetattr(self, my_obj, my_branch, default_bool):
        try: getattr(my_obj, my_branch)
        except RuntimeError:
            #print my_branch, "not found"
            return default_bool
        else: return getattr(my_obj, my_branch)

    def get_efficiency(self, trigger_name, kinematic):
        if trigger_name not in self.effs:
            #self.effs[trigger_name] = self.tf.Get(trigger_name)
            print trigger_name, " not found. Talk to Hui"
            return 0, 0, 0

        eff = self.effs[trigger_name]  
        my_xrange = np.array([eff.GetX()[i] - eff.GetErrorXlow(i) for i in range(eff.GetN()) ])
        my_xrange = np.append(my_xrange, 99999)
        findbix = np.searchsorted(my_xrange, kinematic)-1
	#print " my_xrange is ", my_xrange
        if findbix == -1:
            return 0, 0, 0
        return eff.GetY()[findbix], eff.GetY()[findbix] - eff.GetErrorYlow(findbix), eff.GetY()[findbix] + eff.GetErrorYhigh(findbix)

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
    	self.nEvents += 1
        if (self.maxEvents != -1 and self.nEvents > self.maxEvents):
            return False

        hlt       = Object(event, "HLT")
        met       = Object(event, "MET")
        electrons = Collection(event, "Electron")
        muons	  = Collection(event, "Muon")
        photons   = Collection(event, "Photon")

	if not self.isData: Pass_trigger_MET = True
        else: Pass_trigger_MET = (
            self.mygetattr(hlt, 'PFMET100_PFMHT100_IDTight', False)
            or self.mygetattr(hlt, 'PFMET110_PFMHT110_IDTight', False)
            or self.mygetattr(hlt, 'PFMET120_PFMHT120_IDTight', False)
            or self.mygetattr(hlt, 'PFMET130_PFMHT130_IDTight', False)
            or self.mygetattr(hlt, 'PFMET140_PFMHT140_IDTight', False)
            or self.mygetattr(hlt, 'PFMETNoMu100_PFMHTNoMu100_IDTight', False)
            or self.mygetattr(hlt, 'PFMETNoMu110_PFMHTNoMu110_IDTight', False)
            or self.mygetattr(hlt, 'PFMETNoMu120_PFMHTNoMu120_IDTight', False)
            or self.mygetattr(hlt, 'PFMETNoMu130_PFMHTNoMu130_IDTight', False)
            or self.mygetattr(hlt, 'PFMETNoMu140_PFMHTNoMu140_IDTight', False)
            or self.mygetattr(hlt, 'PFMET100_PFMHT100_IDTight_PFHT60', False)
            or self.mygetattr(hlt, 'PFMET110_PFMHT110_IDTight_PFHT60', False)
            or self.mygetattr(hlt, 'PFMET120_PFMHT120_IDTight_PFHT60', False)
            or self.mygetattr(hlt, 'PFMET130_PFMHT130_IDTight_PFHT60', False)
            or self.mygetattr(hlt, 'PFMET140_PFMHT140_IDTight_PFHT60', False)
            or self.mygetattr(hlt, 'PFMETNoMu100_PFMHTNoMu100_IDTight_PFHT60', False)
            or self.mygetattr(hlt, 'PFMETNoMu110_PFMHTNoMu110_IDTight_PFHT60', False)
            or self.mygetattr(hlt, 'PFMETNoMu120_PFMHTNoMu120_IDTight_PFHT60', False)
            or self.mygetattr(hlt, 'PFMETNoMu130_PFMHTNoMu130_IDTight_PFHT60', False)
            or self.mygetattr(hlt, 'PFMETNoMu140_PFMHTNoMu140_IDTight_PFHT60', False)
            #or self.mygetattr(hlt, 'PFMET120_PFMHT120_IDTight_HFCleaned', False)
            #or self.mygetattr(hlt, 'PFMET120_PFMHT120_IDTight_PFHT60_HFCleaned', False)
            #or self.mygetattr(hlt, 'PFMETNoMu120_PFMHTNoMu120_IDTight_HFCleaned', False)
        )

	if not self.isData: Pass_trigger_muon = True
        else: Pass_trigger_muon = (
            self.mygetattr(hlt, 'IsoMu20', False)
            or self.mygetattr(hlt, 'IsoMu22', False)
            or self.mygetattr(hlt, 'IsoMu24', False)
            or self.mygetattr(hlt, 'IsoMu27', False)
            or self.mygetattr(hlt, 'IsoMu22_eta2p1', False)
            or self.mygetattr(hlt, 'IsoMu24_eta2p1', False)
            or self.mygetattr(hlt, 'IsoTkMu22', False)
            or self.mygetattr(hlt, 'IsoTkMu24', False)
            or self.mygetattr(hlt, 'Mu50', False)
            or self.mygetattr(hlt, 'Mu55', False)
        )

	if not self.isData: Pass_trigger_electron = True
        else: Pass_trigger_electron = (
            self.mygetattr(hlt, 'Ele105_CaloIdVT_GsfTrkIdT', False)
            or self.mygetattr(hlt, 'Ele115_CaloIdVT_GsfTrkIdT', False)
            or self.mygetattr(hlt, 'Ele135_CaloIdVT_GsfTrkIdT', False)
            or self.mygetattr(hlt, 'Ele145_CaloIdVT_GsfTrkIdT', False)
            or self.mygetattr(hlt, 'Ele25_eta2p1_WPTight_Gsf', False)
            or self.mygetattr(hlt, 'Ele20_eta2p1_WPLoose_Gsf', False)
            or self.mygetattr(hlt, 'Ele27_eta2p1_WPLoose_Gsf', False)
            or self.mygetattr(hlt, 'Ele27_WPTight_Gsf', False)
            or self.mygetattr(hlt, 'Ele35_WPTight_Gsf', False)
            or self.mygetattr(hlt, 'Ele20_WPLoose_Gsf', False)
            or self.mygetattr(hlt, 'Ele45_WPLoose_Gsf', False)
            or self.mygetattr(hlt, 'Ele23_Ele12_CaloIdL_TrackIdL_IsoVL', False)
            or self.mygetattr(hlt, 'Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', False)
            or self.mygetattr(hlt, 'DoubleEle33_CaloIdL_GsfTrkIdVL', False)
            or self.mygetattr(hlt, 'DoubleEle33_CaloIdL_GsfTrkIdVL_MW', False)
            or self.mygetattr(hlt, 'DoubleEle25_CaloIdL_MW', False)
            or self.mygetattr(hlt, 'DoubleEle33_CaloIdL_MW', False)
        )

	if not self.isData: Pass_trigger_photon = True
        else: Pass_trigger_photon = (
            self.mygetattr(hlt, 'Photon175', False)
            or self.mygetattr(hlt, 'Photon200', False)
        )

	ele_veto = []
	ele_mid = []
	ele_tight = []
	for ele in electrons:
		if (ele.pt > 5 and abs(ele.eta) < 2.5 and ele.cutBasedNoIso >= 1 and ele.miniPFRelIso_all < 0.1):
			ele_veto.append(ele)
			if (ele.cutBasedNoIso >= 3):
				ele_mid.append(ele)
			if (ele.cutBasedNoIso >= 4):
				ele_tight.append(ele)
	n_ele = len(ele_veto)
	n_ele_mid = len(ele_mid)
	n_ele_tight = len(ele_tight)

	zee_mid = []
	if (n_ele_mid == 2 and ele_mid[0].pt > 40 and ele_mid[1].pt > 20 and (ele_mid[0].charge + ele_mid[1].charge) == 0):
		zee_cand = ROOT.TLorentzVector()
		zee_cand = ele_mid[0].p4() + ele_mid[1].p4()
		#Z mass = 91 GeV
		#print "zee_cand mass = ", zee_cand.M()
		if (zee_cand.M() > 81 and zee_cand.M() < 101):
			zee_mid.append(zee_cand)
	n_zee = len(zee_mid)
		
	mu_loose = []
	mu_mid = []
	for mu in muons:
		if (mu.pt > 5 and abs(mu.eta) < 2.4 and mu.miniPFRelIso_all < 0.2):
			mu_loose.append(mu)
			if (mu.mediumId):
				mu_mid.append(mu)
	n_mu = len(mu_loose)
	n_mu_mid = len(mu_mid)

	zmumu_mid = []
	if (n_mu_mid == 2 and mu_mid[0].pt > 50 and mu_mid[1].pt > 20 and (mu_mid[0].charge + mu_mid[1].charge) == 0):
		zmumu_cand = ROOT.TLorentzVector()
		zmumu_cand = mu_mid[0].p4() + mu_mid[1].p4()
		#Z mass = 91 GeV
		#print "zmumu_cand mass = ", zmumu_cand.M()
		if (zmumu_cand.M() > 81 and zmumu_cand.M() < 101):
			zmumu_mid.append(zmumu_cand)
	n_zmumu = len(zmumu_mid)

        photon_loose = []
        photon_mid = []
        for photon in photons:
                if (abs(photon.eta) < 1.442 or (1.566 < abs(photon.eta) and abs(photon.eta) < 2.5)):
                        #cutbase =  photon.cutBasedBitmap if self.era != "2016" else photon.cutBased
                        #if(cutbase >=1):
                        #        photon_loose.append(photon)
                        #if(cutbase >=2):
                        #        photon_mid.append(photon)
			if self.era == "2016":
				if photon.cutBased >=1: photon_loose.append(photon)
				if photon.cutBased >=2: photon_mid.append(photon)
			else:
				if bool(photon.cutBasedBitmap & 1): photon_loose.append(photon)
				if bool(photon.cutBasedBitmap & 2): photon_mid.append(photon)
        n_photon = len(photon_loose)
        n_photon_mid = len(photon_mid)

	MET_trigger_eff_loose_baseline = MET_trigger_eff_loose_baseline_down = MET_trigger_eff_loose_baseline_up = 0
	MET_trigger_eff_high_dm = MET_trigger_eff_high_dm_down = MET_trigger_eff_high_dm_up = 0
	MET_trigger_eff_low_dm = MET_trigger_eff_low_dm_down = MET_trigger_eff_low_dm_up = 0
	MET_trigger_eff_loose_baseline_QCD = MET_trigger_eff_loose_baseline_QCD_down = MET_trigger_eff_loose_baseline_QCD_up = 0
	MET_trigger_eff_high_dm_QCD = MET_trigger_eff_high_dm_QCD_down = MET_trigger_eff_high_dm_QCD_up = 0
	MET_trigger_eff_low_dm_QCD = MET_trigger_eff_low_dm_QCD_down = MET_trigger_eff_low_dm_QCD_up = 0

	if (met.pt > 100):
		MET_trigger_eff_loose_baseline, MET_trigger_eff_loose_baseline_down, MET_trigger_eff_loose_baseline_up = self.get_efficiency("MET_loose_baseline", met.pt)
		MET_trigger_eff_high_dm, MET_trigger_eff_high_dm_down, MET_trigger_eff_high_dm_up = self.get_efficiency("MET_high_dm", met.pt)
		MET_trigger_eff_low_dm, MET_trigger_eff_low_dm_down, MET_trigger_eff_low_dm_up = self.get_efficiency("MET_low_dm", met.pt)
		MET_trigger_eff_loose_baseline_QCD, MET_trigger_eff_loose_baseline_QCD_down, MET_trigger_eff_loose_baseline_QCD_up = self.get_efficiency("MET_loose_baseline_QCD", met.pt)
		MET_trigger_eff_high_dm_QCD, MET_trigger_eff_high_dm_QCD_down, MET_trigger_eff_high_dm_QCD_up = self.get_efficiency("MET_high_dm_QCD", met.pt)
		MET_trigger_eff_low_dm_QCD, MET_trigger_eff_low_dm_QCD_down, MET_trigger_eff_low_dm_QCD_up = self.get_efficiency("MET_low_dm_QCD", met.pt)

	Electron_trigger_eff_pt = Electron_trigger_eff_pt_down = Electron_trigger_eff_pt_up = 0
	if (n_ele_mid >=1): Electron_trigger_eff_pt, Electron_trigger_eff_pt_down, Electron_trigger_eff_pt_up = self.get_efficiency("Electron_pt", ele_mid[0].pt)
	Electron_trigger_eff_eta = Electron_trigger_eff_eta_down = Electron_trigger_eff_eta_up = 0
	if (n_ele_mid >=1): Electron_trigger_eff_eta, Electron_trigger_eff_eta_down, Electron_trigger_eff_eta_up = self.get_efficiency("Electron_eta", ele_mid[0].eta)

	Muon_trigger_eff_pt = Muon_trigger_eff_pt_down = Muon_trigger_eff_pt_up = 0
	if (n_mu_mid >=1): Muon_trigger_eff_pt, Muon_trigger_eff_pt_down, Muon_trigger_eff_pt_up = self.get_efficiency("Muon_pt", mu_mid[0].pt)
	Muon_trigger_eff_eta = Muon_trigger_eff_eta_down = Muon_trigger_eff_eta_up = 0
	if (n_mu_mid >=1): Muon_trigger_eff_eta, Muon_trigger_eff_eta_down, Muon_trigger_eff_eta_up = self.get_efficiency("Muon_eta", mu_mid[0].eta)

	Photon_trigger_eff_pt = Photon_trigger_eff_pt_down = Photon_trigger_eff_pt_up = 0
	if (n_photon_mid >=1): Photon_trigger_eff_pt, Photon_trigger_eff_pt_down, Photon_trigger_eff_pt_up = self.get_efficiency("Photon_pt", photon_mid[0].pt)
	Photon_trigger_eff_eta = Photon_trigger_eff_eta_down = Photon_trigger_eff_eta_up = 0
	if (n_photon_mid >=1): Photon_trigger_eff_eta, Photon_trigger_eff_eta_down, Photon_trigger_eff_eta_up = self.get_efficiency("Photon_eta", photon_mid[0].eta)

	Zee_trigger_eff_pt = Zee_trigger_eff_pt_down = Zee_trigger_eff_pt_up = 0
	if (n_zee ==1): Zee_trigger_eff_pt, Zee_trigger_eff_pt_down, Zee_trigger_eff_pt_up = self.get_efficiency("Zee_pt", zee_mid[0].Pt())
	Zmumu_trigger_eff_pt = Zmumu_trigger_eff_pt_down = Zmumu_trigger_eff_pt_up = 0
	if (n_zmumu ==1): Zmumu_trigger_eff_pt, Zmumu_trigger_eff_pt_down, Zmumu_trigger_eff_pt_up = self.get_efficiency("Zmumu_pt", zmumu_mid[0].Pt())

        ### Store output
        self.out.fillBranch("Pass_trigger_MET", Pass_trigger_MET)
        self.out.fillBranch("Pass_trigger_muon", Pass_trigger_muon)
        self.out.fillBranch("Pass_trigger_electron", Pass_trigger_electron)
        self.out.fillBranch("Pass_trigger_photon", Pass_trigger_photon)

        self.out.fillBranch("Stop0l_trigger_eff_MET_loose_baseline", MET_trigger_eff_loose_baseline)
        self.out.fillBranch("Stop0l_trigger_eff_MET_loose_baseline_down", MET_trigger_eff_loose_baseline_down)
        self.out.fillBranch("Stop0l_trigger_eff_MET_loose_baseline_up", MET_trigger_eff_loose_baseline_up)
        self.out.fillBranch("Stop0l_trigger_eff_MET_low_dm", MET_trigger_eff_low_dm)
        self.out.fillBranch("Stop0l_trigger_eff_MET_low_dm_down", MET_trigger_eff_low_dm_down)
        self.out.fillBranch("Stop0l_trigger_eff_MET_low_dm_up", MET_trigger_eff_low_dm_up)
        self.out.fillBranch("Stop0l_trigger_eff_MET_high_dm", MET_trigger_eff_high_dm)
        self.out.fillBranch("Stop0l_trigger_eff_MET_high_dm_down", MET_trigger_eff_high_dm_down)
        self.out.fillBranch("Stop0l_trigger_eff_MET_high_dm_up", MET_trigger_eff_high_dm_up)

        self.out.fillBranch("Stop0l_trigger_eff_MET_loose_baseline_QCD", MET_trigger_eff_loose_baseline_QCD)
        self.out.fillBranch("Stop0l_trigger_eff_MET_loose_baseline_QCD_down", MET_trigger_eff_loose_baseline_QCD_down)
        self.out.fillBranch("Stop0l_trigger_eff_MET_loose_baseline_QCD_up", MET_trigger_eff_loose_baseline_QCD_up)
        self.out.fillBranch("Stop0l_trigger_eff_MET_low_dm_QCD", MET_trigger_eff_low_dm_QCD)
        self.out.fillBranch("Stop0l_trigger_eff_MET_low_dm_QCD_down", MET_trigger_eff_low_dm_QCD_down)
        self.out.fillBranch("Stop0l_trigger_eff_MET_low_dm_QCD_up", MET_trigger_eff_low_dm_QCD_up)
        self.out.fillBranch("Stop0l_trigger_eff_MET_high_dm_QCD", MET_trigger_eff_high_dm_QCD)
        self.out.fillBranch("Stop0l_trigger_eff_MET_high_dm_QCD_down", MET_trigger_eff_high_dm_QCD_down)
        self.out.fillBranch("Stop0l_trigger_eff_MET_high_dm_QCD_up", MET_trigger_eff_high_dm_QCD_up)

        self.out.fillBranch("Stop0l_trigger_eff_Electron_pt", Electron_trigger_eff_pt)
        self.out.fillBranch("Stop0l_trigger_eff_Electron_pt_down", Electron_trigger_eff_pt_down)
        self.out.fillBranch("Stop0l_trigger_eff_Electron_pt_up", Electron_trigger_eff_pt_up)
        self.out.fillBranch("Stop0l_trigger_eff_Electron_eta", Electron_trigger_eff_eta)
        self.out.fillBranch("Stop0l_trigger_eff_Electron_eta_down", Electron_trigger_eff_eta_down)
        self.out.fillBranch("Stop0l_trigger_eff_Electron_eta_up", Electron_trigger_eff_eta_up)
        self.out.fillBranch("Stop0l_trigger_eff_Muon_pt", Muon_trigger_eff_pt)
        self.out.fillBranch("Stop0l_trigger_eff_Muon_pt_down", Muon_trigger_eff_pt_down)
        self.out.fillBranch("Stop0l_trigger_eff_Muon_pt_up", Muon_trigger_eff_pt_up)
        self.out.fillBranch("Stop0l_trigger_eff_Muon_eta", Muon_trigger_eff_eta)
        self.out.fillBranch("Stop0l_trigger_eff_Muon_eta_down", Muon_trigger_eff_eta_down)
        self.out.fillBranch("Stop0l_trigger_eff_Muon_eta_up", Muon_trigger_eff_eta_up)
        self.out.fillBranch("Stop0l_trigger_eff_Photon_pt", Photon_trigger_eff_pt)
        self.out.fillBranch("Stop0l_trigger_eff_Photon_pt_down", Photon_trigger_eff_pt_down)
        self.out.fillBranch("Stop0l_trigger_eff_Photon_pt_up", Photon_trigger_eff_pt_up)
        self.out.fillBranch("Stop0l_trigger_eff_Photon_eta", Photon_trigger_eff_eta)
        self.out.fillBranch("Stop0l_trigger_eff_Photon_eta_down", Photon_trigger_eff_eta_down)
        self.out.fillBranch("Stop0l_trigger_eff_Photon_eta_up", Photon_trigger_eff_eta_up)

        self.out.fillBranch("Stop0l_trigger_eff_Zee_pt", Zee_trigger_eff_pt)
        self.out.fillBranch("Stop0l_trigger_eff_Zee_pt_down", Zee_trigger_eff_pt_down)
        self.out.fillBranch("Stop0l_trigger_eff_Zee_pt_up", Zee_trigger_eff_pt_up)
        self.out.fillBranch("Stop0l_trigger_eff_Zmumu_pt", Zmumu_trigger_eff_pt)
        self.out.fillBranch("Stop0l_trigger_eff_Zmumu_pt_down", Zmumu_trigger_eff_pt_down)
        self.out.fillBranch("Stop0l_trigger_eff_Zmumu_pt_up", Zmumu_trigger_eff_pt_up)

        self.tf.Close()
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
# Stop0lBaseline = lambda : Stop0lBaselineProducer("2016", False)
