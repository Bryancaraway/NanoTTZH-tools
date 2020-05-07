import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
import numpy as np
from functools import reduce
import operator
import os

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoSUSYTools.modules.datamodelRemap import ObjectRemapped, CollectionRemapped
from PhysicsTools.NanoAODTools.postprocessing.tools import deltaPhi, deltaR, closest

class TopReweightProducer(Module):
    def __init__(self, era, Process, isData = False):
        self.era = era
        self.sampleName = Process
        self.isData = isData
        self.xsRoot_mg = os.environ["CMSSW_BASE"] + "/src/PhysicsTools/NanoSUSYTools/data/toppt/topPT_MGPowheg_comp.root"
        self.xsRoot_topptSyst = os.environ["CMSSW_BASE"] + "/src/PhysicsTools/NanoSUSYTools/data/toppt/LostLepton_topPt_systematics.root"
        self.hist_toppt_up = "topPt_up";
        self.hist_toppt_dn = "topPt_dn";

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def loadhisto(self,filename,hname):
        file =ROOT.TFile.Open(filename)
        hist_ = file.Get(hname)
        hist_.SetDirectory(0)
        return hist_

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        if "TTbar" in self.sampleName:
           self.topMGPowheg=self.loadhisto(self.xsRoot_mg,self.era)
           self.topPTSyst_up=self.loadhisto(self.xsRoot_topptSyst,self.hist_toppt_up)
           self.topPTSyst_dn=self.loadhisto(self.xsRoot_topptSyst,self.hist_toppt_dn)

        ## Description of variables
        ## Stop0l_topptWeight is the full reweighting correction with the top pT + Pow/MG
        ## Stop0l_topMGPowWeight is only the Pow/MG correction
        ## Stop0l_topptOnly is only the top Pt reweighting that is done on gentops
        ## Stop0l_topptOnly_Up/Down is the systematic variation using inputs from Zhenbin
        ## Mathematically the relation is Stop0l_topptWeight = Stop0l_topptOnly * Stop0l_topMGPowWeight
        if not self.isData:
            self.out.branch('Stop0l_topptWeight', 			"F")
            self.out.branch('Stop0l_topMGPowWeight', 			"F")
            self.out.branch('Stop0l_topptOnly', 		        "F")
            self.out.branch('Stop0l_topptOnly_Up', 			"F")
            self.out.branch('Stop0l_topptOnly_Down', 			"F")

    def topPTSyst(self, toppt):
        ptrange = [0, 25, 75, 125, 200, 250, 300, 350, 450, 600]
        pt_index = -1
        y_up = []
        y_dn = []
        x = []
        syst_out = []
        for i in xrange(len(ptrange)):
            if toppt < float(ptrange[i]):
                if toppt >= 25: pt_index = i - 1
                else:           pt_index = 1
                x = [ptrange[pt_index + 1], ptrange[pt_index]]
                y_up = [self.topPTSyst_up.GetBinContent(self.topPTSyst_up.GetXaxis().FindBin(ptrange[pt_index + 1])), self.topPTSyst_up.GetBinContent(self.topPTSyst_up.GetXaxis().FindBin(ptrange[pt_index]))]
                y_dn = [self.topPTSyst_dn.GetBinContent(self.topPTSyst_dn.GetXaxis().FindBin(ptrange[pt_index + 1])), self.topPTSyst_dn.GetBinContent(self.topPTSyst_dn.GetXaxis().FindBin(ptrange[pt_index]))]
                break
            else:
                pt_index = len(ptrange) - 1
                x = [ptrange[pt_index], ptrange[pt_index - 1]]
                y_up = [self.topPTSyst_up.GetBinContent(self.topPTSyst_up.GetXaxis().FindBin(ptrange[pt_index])), self.topPTSyst_up.GetBinContent(self.topPTSyst_up.GetXaxis().FindBin(ptrange[pt_index - 1]))]
                y_dn = [self.topPTSyst_dn.GetBinContent(self.topPTSyst_dn.GetXaxis().FindBin(ptrange[pt_index])), self.topPTSyst_dn.GetBinContent(self.topPTSyst_dn.GetXaxis().FindBin(ptrange[pt_index - 1]))]

        def line(pt, m, c):
            return m*np.clip(pt, 0, 800) + c

        coef_up = np.polyfit(x, y_up, 1)
        coef_dn = np.polyfit(x, y_dn, 1)
        up = line(toppt, coef_up[0], coef_up[1])
        dn = line(toppt, coef_dn[0], coef_dn[1])

        if up < 0.5 or dn < 0.5: print("toppt: {0}, coef_up: {1}, coef_dn: {2}, x: {3}, y_up: {4}, y_dn: {5}, ptrange: {6}".format(toppt, coef_up, coef_dn, x, y_up, y_dn, ptrange[pt_index]))

        return up, dn

    def topPTWeight(self, genparts):
        genTops = []
        genTops_up = []
        genTops_dn = []
        mgpowheg = []
        for gp in genparts:
            if gp.statusFlags & 8192 == 0: continue
            if abs(gp.pdgId) == 6:
                genTops.append(gp)
                mgpowheg.append(self.topMGPowheg.GetBinContent(self.topMGPowheg.GetNbinsX()) if gp.pt >= 1000 else self.topMGPowheg.GetBinContent(self.topMGPowheg.GetXaxis().FindBin(gp.pt)))
                up, dn = self.topPTSyst(gp.pt)
                genTops_up.append(up)
                genTops_dn.append(dn)

            if len(mgpowheg) != 0: topptWeight = 1.*mgpowheg[0]
            else:                  topptWeight = 1.
            topptWeight_only = 1.
            if len(mgpowheg) != 0: topptWeight_mgpow = mgpowheg[0]
            else:                  topptWeight_mgpow = 1.
            if len(genTops_up) != 0: topptWeight_up = genTops_up[0]
            else:                    topptWeight_up = 1.
            if len(genTops_dn) != 0: topptWeight_dn = genTops_dn[0]
            else:                    topptWeight_dn = 1.

            if len(genTops) == 2:
                def wgt(pt):
                    return np.exp(0.0615 - 0.0005 * np.clip(pt, 0, 800))
        
                topptWeight = np.sqrt(wgt(genTops[0].pt) * mgpowheg[0] * wgt(genTops[1].pt) * mgpowheg[1])
                topptWeight_only = np.sqrt(wgt(genTops[0].pt) * wgt(genTops[1].pt))
                topptWeight_up = np.sqrt(wgt(genTops[0].pt) * genTops_up[0] * wgt(genTops[1].pt) * genTops_up[1])
                topptWeight_dn = np.sqrt(wgt(genTops[0].pt) * genTops_dn[0] * wgt(genTops[1].pt) * genTops_dn[1])
                topptWeight_mgpow = np.sqrt(mgpowheg[0] * mgpowheg[1])

        #print("toppt1: {0}, mgpow2: {1}, toppt2: {2}, mgpow2: {3}".format(genTops[0].pt, mgpowheg[0], genTops[1].pt, mgpowheg[1]))
        return topptWeight, topptWeight_only, topptWeight_mgpow, topptWeight_up, topptWeight_dn

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        ## Getting objects
        if not self.isData: genpart   = Collection(event, "GenPart")
        
        if "TTbar" in self.sampleName:
            toppt_wgt, toppt_only, toppt_mgpow, toppt_up, toppt_dn  = self.topPTWeight(genpart) 
        else:
            toppt_wgt = 1.
            toppt_only = 1.
            toppt_mgpow = 1.
            toppt_up = 1.
            toppt_dn = 1.
        #print("toppt_wgt: {0}".format(toppt_lep))
        self.out.fillBranch('Stop0l_topptWeight', 		toppt_wgt)
        self.out.fillBranch('Stop0l_topMGPowWeight', 		toppt_mgpow)
        self.out.fillBranch('Stop0l_topptOnly', 	        toppt_only)
        self.out.fillBranch('Stop0l_topptOnly_Up', 		toppt_up)
        self.out.fillBranch('Stop0l_topptOnly_Down', 		toppt_dn)
        
        return True


 # define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
