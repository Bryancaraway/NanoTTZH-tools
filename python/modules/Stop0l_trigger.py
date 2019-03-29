import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class Stop0l_trigger(Module):
    def __init__(self, era):
        self.era = era
	eff_file = "%s/src/PhysicsTools/NanoSUSYTools/data/trigger_eff/" % os.environ['CMSSW_BASE']
	eff_file = eff_file + self.era + "_trigger_eff.root"
	self.tf = ROOT.TFile.Open(eff_file)

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

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def mygetattr(self, my_obj, my_branch, default_bool):
	try: getattr(my_obj, my_branch)
	except RuntimeError:
	    #print my_branch, "not found"
	    return default_bool
	else: return getattr(my_obj, my_branch)

    def get_efficiency(self, trigger_name, kinematic):
	eff_hist = self.tf.Get(trigger_name)
	return eff_hist.GetBinContent(eff_hist.FindBinNumber(kinematic))

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        hlt       = Object(event, "HLT")
        met       = Object(event, "MET")

        Pass_trigger_MET = (
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

        Pass_trigger_muon = (
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

        Pass_trigger_electron = (
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

        Pass_trigger_photon = (
	self.mygetattr(hlt, 'Photon175', False)
	or self.mygetattr(hlt, 'Photon200', False)
	)

	MET_trigger_eff_loose_baseline = get_efficiency("MET_loose_baseline", met.pt)

        ### Store output
        self.out.fillBranch("Pass_trigger_MET", Pass_trigger_MET)
        self.out.fillBranch("Pass_trigger_muon", Pass_trigger_muon)
        self.out.fillBranch("Pass_trigger_electron", Pass_trigger_electron)
        self.out.fillBranch("Pass_trigger_photon", Pass_trigger_photon)

	self.out.fillBranch("Stop0l_trigger_eff_MET_loose_baseline", MET_trigger_eff_loose_baseline)

	self.tf.Close()
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
# Stop0lBaseline = lambda : Stop0lBaselineProducer("2016", False)
