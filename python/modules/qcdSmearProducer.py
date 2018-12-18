#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import deltaPhi, deltaR, closest

class qcdSmearProducer(Module): 
    def __init__(self):
	self.writeHistFile=True
	self.metBranchName="MET"
	self.minWindow = 0.01
	self.maxWindow = 0.5;
	self.nSmears = 100;
	self.nSmearJets = 2;
	self.nBootstraps = 50;
	self.LINEAR_GRANULATED=True
	self.winType = self.LINEAR_GRANULATED;
	self.doFlatSampling = True;
	self.respInputName = "JetResByFlav";
	self.respFileName = "file:/eos/uscms/store/user/mkilpatr/13TeV/qcd_smearing/resTailOut_combined_filtered_CHEF_puWeight_weight_WoH_NORMALIZED.root"
	self.respHistoName = "res_b_comp_14"
	self.targeth = self.loadHisto(self.respFileName,self.respHistoName)
 
    def loadHisto(self,filename,hname):
	tf = ROOT.TFile.Open(filename)
	hist = tf.Get(hname)
	hist.SetDirectory(None)
	tf.Close()
	return hist

    def beginJob(self,histFile=None,histDirName=None):
   	pass
    def endJob(self):
	pass 

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
	self.out.branch("origRes", "F", lenVar="nJet*nGenJet");
	self.out.branch("jetFlav", "F");

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def jetResFunction(self, jets, genjets):
	res = jets.pt/genjets.pt
	return res

    def addFourVector(self, obj1, obj2):
	tot = ROOT.TLorentzVector()
	v1 = ROOT.TLorentzVector()
	v2 = ROOT.TLorentzVector()
	v1.SetPtEtaPhiM(obj1.pt, 0, obj1.phi, 0)
	v2.SetPtEtaPhiM(obj2.pt, 0, obj2.phi, 0)
	tot = v1+v2
	return tot

    def analyze(self, event):
	jets      = Collection(event, "Jet")
	genjets   = Collection(event, "GenJet")
	met       = Object(event,     self.metBranchName)
	weight    = Object(event,     "genWeight")

	# matching gen jet can be called by the index Jet_genJetIdx, jet.genJetIdx == matched GenJet

	#bootstrapping should be done here
	print "Try to get bin content: %d", self.targeth.GetNBinsX()
	nbinx = self.targeth.GetNBinsX()
	
	#begin smearing
	smearWeight = 1
	nj = 0
	for j in jets :
		if nj == self.nSmearJets:
			break
		else:
			nj+=1
        	gj = j.genJetIdx
		#you know have a matching index to the reco jet
		testMet = self.addFourVector(met, j).Pt()
		print "nj: %i", nj
		print "index: %i", gj
		print "testMet: %f", testMet
		jetFlavour = j.partonFlavour
		self.out.fillBranch("jetFlav", jetFlavour)
		#This calculates the response with matched gen and reco jets
		origRes_ = [ self.jetResFunction(j, genjets[gj]) ]
		#print "Try to get bin content: %d", self.targeth.GetBinContent(self.jetResFunction(j, genjets[gj]))

	self.out.fillBranch("origRes", origRes_)
        return True
