import ROOT
import os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class BtagSFWeightProducer(Module):

    def __init__(self, bTagEffFile, sampleName, bDiscCut, jetPtMin = 20, jetEtaMax = 2.4, fileDirectory = os.environ['CMSSW_BASE'] + "/src/PhysicsTools/NanoSUSYTools/data/btagSF/"):
        self.jetPtMin = jetPtMin
        self.jetEtaMax = jetEtaMax
        self.bDiscCut = bDiscCut

        self.bTagEffFile = bTagEffFile
        self.sampleName = sampleName
        self.fileDirectory = fileDirectory

    def beginJob(self):
        ROOT.TH1.AddDirectory(False)
        
        fin = ROOT.TFile.Open(self.fileDirectory + "/" + self.bTagEffFile)

        self.h_eff_b          = fin.Get(("n_eff_b_" + self.sampleName));
        self.h_eff_c          = fin.Get(("n_eff_c_" + self.sampleName));
        self.h_eff_udsg       = fin.Get(("n_eff_udsg_" + self.sampleName));
        d_eff_b          = fin.Get(("d_eff_b_" + self.sampleName));
        d_eff_c          = fin.Get(("d_eff_c_" + self.sampleName));
        d_eff_udsg       = fin.Get(("d_eff_udsg_" + self.sampleName));

        if not self.h_eff_b or not self.h_eff_c or not self.h_eff_udsg:
            print "B-tag efficiency histograms for sample \"%s\" are not found in file \"%s\".  Using TTBar_2016 inclusive numbers as default setting!!!!"%( self.sampleName, self.bTagEffFile)

            self.sampleName = "TTbarInc_2016"

            self.h_eff_b          = fin.Get(("n_eff_b_" + self.sampleName));
            self.h_eff_c          = fin.Get(("n_eff_c_" + self.sampleName));
            self.h_eff_udsg       = fin.Get(("n_eff_udsg_" + self.sampleName));
            d_eff_b          = fin.Get(("d_eff_b_" + self.sampleName));
            d_eff_c          = fin.Get(("d_eff_c_" + self.sampleName));
            d_eff_udsg       = fin.Get(("d_eff_udsg_" + self.sampleName));
        
        self.h_eff_b.Divide(d_eff_b);
        self.h_eff_c.Divide(d_eff_c);
        self.h_eff_udsg.Divide(d_eff_udsg);

        
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("BTagWeight",      	"F", title="BTag event weight following method 1a")
        self.out.branch("BTagWeight_Up",   	"F", title="BTag event weight up uncertainty")
        self.out.branch("BTagWeight_Down", 	"F", title="BTag event weight down uncertainty")
        self.out.branch("BTagWeightHeavy",      "F", title="BTag event heavy weight following method 1a")
        self.out.branch("BTagWeightHeavy_Up",   "F", title="BTag event heavy weight up uncertainty")
        self.out.branch("BTagWeightHeavy_Down", "F", title="BTag event heavy weight down uncertainty")
        self.out.branch("BTagWeightLight",      "F", title="BTag event light weight following method 1a")
        self.out.branch("BTagWeightLight_Up",   "F", title="BTag event light weight up uncertainty")
        self.out.branch("BTagWeightLight_Down", "F", title="BTag event light weight down uncertainty")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        jets = Collection(event, "Jet")

        BTagWeightN = 1.0
        BTagWeightN_up = 1.0
        BTagWeightN_down = 1.0
        BTagWeightD = 1.0
        BTagWeightNHeavy = 1.0
        BTagWeightNHeavy_up = 1.0
        BTagWeightNHeavy_down = 1.0
        BTagWeightDHeavy = 1.0
        BTagWeightNLight = 1.0
        BTagWeightNLight_up = 1.0
        BTagWeightNLight_down = 1.0
        BTagWeightDLight = 1.0

        for jet in jets:
            pt = jet.pt
            eta = abs(jet.eta)
            flavor = jet.hadronFlavour

            if not ( pt > self.jetPtMin and eta < self.jetEtaMax): continue

            if flavor == 5:
                pt_bin = self.h_eff_b.GetXaxis().FindBin(pt); 
                if pt_bin > self.h_eff_b.GetXaxis().GetNbins():
                    pt_bin = self.h_eff_b.GetXaxis().GetNbins(); 
                eta_bin = self.h_eff_b.GetYaxis().FindBin(eta); 
                if eta_bin > self.h_eff_b.GetYaxis().GetNbins():
                    eta_bin = self.h_eff_b.GetYaxis().GetNbins();

                eff = self.h_eff_b.GetBinContent(pt_bin, eta_bin);

            elif flavor == 4:
                pt_bin = self.h_eff_c.GetXaxis().FindBin(pt); 
                if pt_bin > self.h_eff_c.GetXaxis().GetNbins():
                    pt_bin = self.h_eff_c.GetXaxis().GetNbins(); 
                eta_bin = self.h_eff_c.GetYaxis().FindBin(eta); 
                if eta_bin > self.h_eff_c.GetYaxis().GetNbins():
                    eta_bin = self.h_eff_c.GetYaxis().GetNbins();

                eff = self.h_eff_c.GetBinContent(pt_bin, eta_bin);

            else:
                pt_bin = self.h_eff_udsg.GetXaxis().FindBin(pt); 
                if pt_bin > self.h_eff_udsg.GetXaxis().GetNbins():
                    pt_bin = self.h_eff_udsg.GetXaxis().GetNbins(); 
                eta_bin = self.h_eff_udsg.GetYaxis().FindBin(eta); 
                if eta_bin > self.h_eff_udsg.GetYaxis().GetNbins():
                    eta_bin = self.h_eff_udsg.GetYaxis().GetNbins();

                eff = self.h_eff_udsg.GetBinContent(pt_bin, eta_bin);

            if jet.btagDeepB > self.bDiscCut:
                #check if eff is zero
                if eff < 0.001:
                    eff = 0.001

                BTagWeightN      *= jet.btagSF * eff
                BTagWeightN_up   *= jet.btagSF_up * eff
                BTagWeightN_down *= jet.btagSF_down * eff

		if abs(flavor) == 5:
                	BTagWeightNHeavy      *= jet.btagSF * eff
                	BTagWeightNHeavy_up   *= jet.btagSF_up * eff
                	BTagWeightNHeavy_down *= jet.btagSF_down * eff
			BTagWeightDHeavy      *= eff
		else:
                	BTagWeightNLight      *= jet.btagSF * eff
                	BTagWeightNLight_up   *= jet.btagSF_up * eff
                	BTagWeightNLight_down *= jet.btagSF_down * eff
			BTagWeightDLight      *= eff

                BTagWeightD      *= eff
            else:
                #check if eff is 1.0
                if eff > 0.999:
                    eff = 0.999

                BTagWeightN      *= 1 - jet.btagSF * eff
                BTagWeightN_up   *= 1 - jet.btagSF_up * eff
                BTagWeightN_down *= 1 - jet.btagSF_down * eff

		if abs(flavor) == 5:
                	BTagWeightNHeavy      *= 1 - jet.btagSF * eff
                	BTagWeightNHeavy_up   *= 1 - jet.btagSF_up * eff
                	BTagWeightNHeavy_down *= 1 - jet.btagSF_down * eff
			BTagWeightDHeavy      *= 1 - eff
		else:
                	BTagWeightNLight      *= 1 - jet.btagSF * eff
                	BTagWeightNLight_up   *= 1 - jet.btagSF_up * eff
                	BTagWeightNLight_down *= 1 - jet.btagSF_down * eff
			BTagWeightDLight      *= 1 - eff

                BTagWeightD      *= 1 - eff

        self.out.fillBranch("BTagWeight",      BTagWeightN / BTagWeightD)
        self.out.fillBranch("BTagWeight_Up",   BTagWeightN_up / BTagWeightD)
        self.out.fillBranch("BTagWeight_Down", BTagWeightN_down / BTagWeightD)
        self.out.fillBranch("BTagWeightHeavy",      BTagWeightNHeavy / BTagWeightDHeavy)
        self.out.fillBranch("BTagWeightHeavy_Up",   BTagWeightNHeavy_up / BTagWeightDHeavy)
        self.out.fillBranch("BTagWeightHeavy_Down", BTagWeightNHeavy_down / BTagWeightDHeavy)
        self.out.fillBranch("BTagWeightLight",      BTagWeightNLight / BTagWeightDLight)
        self.out.fillBranch("BTagWeightLight_Up",   BTagWeightNLight_up / BTagWeightDLight)
        self.out.fillBranch("BTagWeightLight_Down", BTagWeightNLight_down / BTagWeightDLight)
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
# lepSF = lambda : lepSFProducer( "LooseWP_2016", "GPMVA90_2016")

