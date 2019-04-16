import ROOT
import os
import numpy as np
import bisect
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import deltaPhi, deltaR, closest

class ISRSFWeightProducer(Module):

    def __init__(self, era, isSUSY, isrEffFile, sampleName, fileDirectory = os.environ['CMSSW_BASE'] + "/src/PhysicsTools/NanoSUSYTools/data/isrSF/"):
        self.era = era
        self.isSUSY = isSUSY
        self.isrEffFile = isrEffFile
        self.sampleName = sampleName
        self.fileDirectory = fileDirectory
        self.isSUSY = None
        # ISR Recommendation: https://hypernews.cern.ch/HyperNews/CMS/get/susy/2524.html
        # Use 2016 (Moriond17 value) for Run 2 from 
        # https://indico.cern.ch/event/592621/contributions/2398559/attachments/1383909/2105089/16-12-05_ana_manuelf_isr.pdf
        # https://indico.cern.ch/event/811884/contributions/3383484/attachments/1824913/2986231/ISR_ConcMarch2019.pdf
        # Apply to 2016 TTbar and Run2 Signal only
        self.Corr2016 = np.asarray([1 , 0.920 , 0.821 , 0.715 , 0.662 , 0.561 , 0.511])
        self.nISRbins = [0 , 1     , 2     , 3     , 4     , 5     , 6]
        self.ISRcentral = np.ones(self.Corr2016.shape)
        self.ISRUp      = np.ones(self.Corr2016.shape)
        self.ISRDown    = np.ones(self.Corr2016.shape)


    def beginJob(self):
        ROOT.TH1.AddDirectory(False)
        fin = ROOT.TFile.Open(self.fileDirectory + "/" + self.isrEffFile)
        self.h_eff          = fin.Get(("NJetsISR_" + self.sampleName));

        if not self.h_eff:
            print "ISRJet efficiency histograms for sample \"%s\" are not found in file \"%s\".  Using TTBar_2016 inclusive numbers as default setting!!!!"%( self.sampleName, self.isrEffFile)
            self.sampleName = "TTbarInc_2016"
            self.h_eff         = fin.Get(("NJetsISR_" + self.sampleName));
        if  ("TTbar" in self.sampleName and self.era == "2016") or self.isSUSY:
            self.PropISRWeightUnc()

    def PropISRWeightUnc(self):
        err        = (1 - self.Corr2016)/2
        errup      = self.Corr2016 + err
        errdown    = self.Corr2016 - err
        heff_Nbins = self.h_eff.GetNbinsX()
        orgtotal   = self.h_eff.Integral(0, heff_Nbins+1)
        orghist    = np.zeros(self.Corr2016.shape)
        ## +2 to include overflow bin, also for range
        for i in range(heff_Nbins+2):
            nbin = bisect.bisect(self.nISRbins, self.h_eff.GetBinCenter(i))
            orghist[nbin-1] += self.h_eff.GetBinContent(i)

        # Recommendation: choose D such that sample normalization is
        # preserved, both for central value and 1sigma
        # if you get D greater than 1.2-1.3, ikely over-counting ISR jets, maybe a sign that jets are not clean
        Dcentral = orgtotal/ sum(orghist * self.Corr2016)
        Dup      = orgtotal/ sum(orghist * errup)
        Ddown    = orgtotal/ sum(orghist * errdown)

        if Dcentral > 1.2 or Dup > 1.2 or Ddown > 1.2:
            print("In ISRReweighting, D is greater than 1.2. Likely over-counting ISR jet :", Dcentral, Dup, Ddown)
        self.ISRcentral = self.Corr2016 * Dcentral
        self.ISRUp      = errup         * Dup
        self.ISRDown    = errdown       * Ddown
        
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("ISRWeight",      "F", title="ISRWeight calculated from a Jet and gen daughter matching")
        self.out.branch("ISRWeight_Up",   "F", title="ISR event weight up uncertainty")
        self.out.branch("ISRWeight_Down", "F", title="ISR event weight down uncertainty")
        self.out.branch("nISRJets",       "F", title="The number of jets that contain a unmatched jet to a gen particle")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def RecursiveMother(self, genpar, daughter):
        mother = daughter.genPartIdxMother
        motherID = abs(mother.pdgId)
        if motherID == -1:
            return False
        if mother_pdgId == 6 or mother_pdgId == 23 or mother_pdgId == 24 or \
           mother_pdgId == 25 or mother_pdgId >1e6:
            return True
        return self.RecursiveMother(genpar, genpar[mother])

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Code for ISR jet cal from Scarlet ~~~~~
        # Looks like room for speed up
        jets = Collection(event, "Jet")
        genParts = Collection(event, "GenPart")

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

        nbin = bisect.bisect(self.nISRbins, nisr) -1
        self.out.fillBranch("nISRJets", nisr)           
        self.out.fillBranch("ISRWeight", self.ISRcentral[nbin])
        self.out.fillBranch("ISRWeight_Up", self.ISRUp[nbin])
        self.out.fillBranch("ISRWeight_Down", self.ISRDown[nbin])
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
# lepSF = lambda : lepSFProducer( "LooseWP_2016", "GPMVA90_2016")

