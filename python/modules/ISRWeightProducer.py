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

        if  ("TTbar" in self.sampleName and self.era == "2016") or self.isSUSY:
            if not self.h_eff:
                print "ISRJet efficiency histograms for sample \"%s\" are not found in file \"%s\".  Using TTBar_2016 inclusive numbers as default setting!!!!"%( self.sampleName, self.isrEffFile)
                self.sampleName = "TTbarInc_2016"
                self.h_eff         = fin.Get(("NJetsISR_" + self.sampleName));
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


    def GetBabySigMuonList(self, muons):
        ''' original code use lepton cleaning. 
        http://github.com/manuelfs/babymaker/blob/0136340602ee28caab14e3f6b064d1db81544a0a/bmaker/plugins/bmaker_full.cc#L395
        The signal Muon was used: https://github.com/manuelfs/babymaker/blob/0136340602ee28caab14e3f6b064d1db81544a0a/bmaker/src/lepton_tools.cc#L34-L43
        Muon cuts are defined here : https://github.com/manuelfs/babymaker/blob/0136340602ee28caab14e3f6b064d1db81544a0a/bmaker/interface/lepton_tools.hh#L25-L30
        ''' 
        muonidx = []
        for m in muons:
            if m.mediumId and m.pt > 20 and abs(m.eta) <= 2.4 and m.miniPFRelIso_all <= 0.2:
                muonidx.append(m.jetIdx)
        return np.asarray(muonidx)
    
    def GetBabySigEleList(self, electrons):
        ''' original code use lepton cleaning. 
        http://github.com/manuelfs/babymaker/blob/0136340602ee28caab14e3f6b064d1db81544a0a/bmaker/plugins/bmaker_full.cc#L395
        The signal Electron was used: https://github.com/manuelfs/babymaker/blob/0136340602ee28caab14e3f6b064d1db81544a0a/bmaker/src/lepton_tools.cc#L34-L43
        Electron cuts are defined here : https://github.com/manuelfs/babymaker/blob/0136340602ee28caab14e3f6b064d1db81544a0a/bmaker/src/lepton_tools.cc#L105-L115
        ''' 
        eleidx = []
        for e in electrons:
            # Medium ID
            if e.cutBasedNoIso >= 3 and e.pt > 20 and abs(e.eta) <= 2.5 and e.miniPFRelIso_all <= 0.1:
                eleidx.append(e.jetIdx)
        return np.asarray(eleidx)

    def GetBabyJetList(self, jets, muons, electrons):
        muonidx = self.GetBabySigMuonList(muons)
        eleidx  = self.GetBabySigEleList(electrons)

        # Jets cuts
        # https://github.com/manuelfs/babymaker/blob/0136340602ee28caab14e3f6b064d1db81544a0a/bmaker/plugins/bmaker_full.cc#L395
        jetidx = []
        for i, j in enumerate(jets):
            # https://github.com/manuelfs/babymaker/blob/0136340602ee28caab14e3f6b064d1db81544a0a/bmaker/interface/jet_met_tools.hh#L34-L36
            if j.pt > 30 and abs(j.eta) <= 2.4 :
                jetidx.append(i)
        lepcleaned = np.setdiff1d(np.asarray(jetidx), eleidx, assume_unique=True)
        lepcleaned = np.setdiff1d(lepcleaned, muonidx, assume_unique=True)
        return lepcleaned

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
        jets      = Collection(event, "Jet")
        genParts  = Collection(event, "GenPart")
        electrons = Collection(event, "Electron")
        muons     = Collection(event, "Muon")

        # Follow babymaker code to produce nisr in the event, following the ICHEP recommendation
        # https://github.com/manuelfs/babymaker/blob/0136340602ee28caab14e3f6b064d1db81544a0a/bmaker/plugins/bmaker_full.cc#L1268-L1295
        jetidx = self.GetBabyJetList(jets, muons, electrons)
        nisr = 0
        for j in jetidx:
            jet = jets[j]
            matched = False 
            for genPart in genParts:
                if genPart.statusFlags != 23 or abs(genPart.pdgId) > 5: 
                    continue
                if self.RecursiveMother(genPart):
                    dR = deltaR(jet,genPart)
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

