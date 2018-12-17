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

    def analyze(self, event):
	jets      = Collection(event, "Jet")
	genjets   = Collection(event, "GenJet")
	met       = Object(event,     self.metBranchName)

	for j in jets :
        	self.out.fillBranch("jetFlav", j.partonFlavour)
		for gj in genjets :
			origRes_ = [ self.jetResFunction(j, gj) ]

	self.out.fillBranch("origRes", origRes_)
        return True
