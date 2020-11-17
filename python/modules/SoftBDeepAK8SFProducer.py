import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
import numba
import os

import numpy as np
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

## Soft b tagging SF from Loukas
## https://indico.cern.ch/event/823731/contributions/3446301/attachments/1851612/3040016/lg-stop0L-softb-20190527.pdf
SoftB_SF = {
    "2016": (1.08, 0.03),
    "2017": (1.05, 0.06),
    "2018": (1.19, 0.06),
}
## Soft b taggging fullsim/fastsim SF from Sicheng
# https://indico.cern.ch/event/828647/contributions/3468642/attachments/1863702/3063958/Softb_ScaleFactors_190617.pdf
SoftB_fastSF = {
    "2016": (0.935, 0.062),
    "2017": (0.930, 0.018),
    "2018": (0.932, 0.023),
}



## Deep Top SF from Loukas
## https://indico.cern.ch/event/828647/contributions/3468598/attachments/1863686/3063744/lg-hot-deepak8sf-20190617.pdf
## Also from Stop1lep AN2019_003_v11, Table 38
DeepTop_SF = {
    "2016" : [
        ((400, 480)  , (1.01, 0.11)),
        ((480, 600)  , (1.05, 0.08)),
        ((600, 9999) , (1.06, 0.05)),
    ],
    "2017" : [
        ((400, 480)  , (1.08, 0.10)),
        ((480, 600)  , (0.97, 0.07)),
        ((600, 9999) , (1.02, 0.08)),
    ],
    "2018" : [
        ((400, 480)  , (0.95, 0.07)),
        ((480, 600)  , (1.06, 0.05)),
        ((600, 9999) , (0.94, 0.05)),
    ]
}
## from Stop1lep AN2019_003_v11, Table 39
DeepTop_fastSF = {
    "2016" : [
        ((400,  480)  , (0.99, 0.06)),
        ((480,  600)  , (0.96, 0.04)),
        ((600,  9999) , (0.92, 0.02)),
    ],
    "2017" : [
        ((400,  480)  , (0.95, 0.04)),
        ((480,  600)  , (1.00, 0.04)),
        ((600,  9999) , (0.96, 0.02)),
    ],
    "2018" : [
        ((400, 480)  , (1.03, 0.06)),
        ((480, 600)  , (1.03, 0.04)),
        ((600, 9999) , (1.03, 0.04)),
    ]
}

DeepTop_Fake_SF = {
    "2016": [
        ((400, 9999) , (0.921, 0.072))
    ],
    "2017": [
        ((400, 9999) , (1.213, 0.079))
    ],
    "2018": [
        ((400, 9999) , (1.086, 0.069))
    ],
}

# Get it from https://indico.cern.ch/event/840827/contributions/3527925/attachments/1895214/3126510/DeepAK8_Top_W_SFs_2017_JMAR_PK.pdf
# No direct value, get it from the png using http://www.graphreader.com/
# Take it with a grain of salt
# Use 1% mistag rate plots, taking the large side of asymmetric systematic as symmetric uncertainty
# Using 2017 SF and uncertainty for 2018 
DeepW_SF = {
    "2016" : [
        ((200, 300) , (0.946, 0.132)),
        ((300, 400) , (0.88, 0.107)),
        ((400, 9999) , (0.901, 0.103)),
    ],
    "2017" : [
        ((200, 300) , (0.941, 0.037)),
        ((300, 400) , (0.937, 0.078)),
        ((400, 9999) , (0.908, 0.115)),
    ],
    "2018" : [
        ((200, 300) , (0.941, 0.037)),
        ((300, 400) , (0.937, 0.078)),
        ((400, 9999) , (0.908, 0.115)),
    ]
}

## Fullsim/fastsim SF measured from 
# https://indico.cern.ch/event/877611/contributions/3762997/attachments/1992874/3326860/Zhenbin_WtaggerSF_v3.pdf
DeepW_fastSF = {
    "2016" : [
        ((200, 300) , (0.94, 0.05)),
        ((300, 400) , (0.99, 0.19)),
        ((400, 9999) , (1.08, 0.12)),
    ],
    "2017" : [
        ((200, 300) , (1.05, 0.02)),
        ((300, 400) , (1.12, 0.23)),
        ((400, 9999) , (1.05, 0.12)),
    ],
    "2018" : [
        ((200, 300) , (1.11, 0.09)),
        ((300, 400) , (1.04, 0.01)),
        ((400, 9999) , (1.16, 0.02)),
    ]
}

DeepW_Fake_SF = {
    "2016" : [
        ((200, 300) ,  (1.161, 0.059)),
        ((300, 400) ,  (1.178, 0.060)),
        ((400, 9999) , (1.314, 0.064)),
    ],
    "2017" : [
        ((200, 300) ,  (1.072, 0.073)),
        ((300, 400) ,  (1.132, 0.065)),
        ((400, 9999) , (1.159, 0.065)),
    ],
    "2018" : [
        ((200, 300) ,  (1.087, 0.065)),
        ((300, 400) ,  (1.058, 0.067)),
        ((400, 9999) , (1.139, 0.071)),
    ]
}

@numba.jit(nopython=True)
def recursiveMotherSearch(startIdx, targetIdx, GenPartCut_genPartIdxMother):
    if startIdx < 0:
        return False

    mom = GenPartCut_genPartIdxMother[startIdx]

    if mom < 0:
        return False
    elif startIdx == targetIdx:
        return True
    else:
        return recursiveMotherSearch(mom, targetIdx, GenPartCut_genPartIdxMother)

@numba.jit(nopython=True)
def genParticleAssociation(GenPart_genPartIdxMother, GenPart_pdgId, GenPart_statusFlags):
    GenPart_momPdgId = GenPart_pdgId[GenPart_genPartIdxMother]
    #set any particles with an index of -1 to id 0                                                                                                                      
    GenPart_momPdgId[GenPart_genPartIdxMother < 0] = 0

    genTopDaughters = []
    genWDaughters = []
    for iGP, pdgId in enumerate(GenPart_pdgId):
        if (GenPart_statusFlags[iGP] & 0x2100) != 0x2100:
            continue
        if abs(pdgId) == 6:
            gtd = []
            for iGP2, pdgId2 in enumerate(GenPart_pdgId):
                if abs(pdgId2) >= 1 and abs(pdgId2) <= 5 and (GenPart_statusFlags[iGP2] & 0x2100) == 0x2100:
                    if recursiveMotherSearch(iGP2, iGP, GenPart_genPartIdxMother):
                        gtd.append(iGP2)
            if len(gtd) == 3:
                genTopDaughters.extend(gtd)
        elif abs(pdgId) == 24:
            gwd = []
            for iGP2, pdgId2 in enumerate(GenPart_pdgId):
                if abs(pdgId2) >= 1 and abs(pdgId2) <= 5 and (GenPart_statusFlags[iGP2] & 0x2100) == 0x2100:
                    if recursiveMotherSearch(iGP2, iGP, GenPart_genPartIdxMother):
                        gwd.append(iGP2)
            if len(gwd) == 2:
                genWDaughters.extend(gwd)

    return genTopDaughters, genWDaughters

def deltaRMatch(fatJetEta, fatJetPhi, genTopDaughters_eta, genTopDaughters_phi, genWDaughters_eta, genWDaughters_phi):

    matches = np.zeros(len(fatJetEta), dtype=int)

    if len(genWDaughters_eta):

        wEtaVals = np.array(np.meshgrid(fatJetEta, genWDaughters_eta)).T.reshape(-1,2)
        wPhiVals = np.array(np.meshgrid(fatJetPhi, genWDaughters_phi)).T.reshape(-1,2)

        ## Using ufunc for vector operation
        deta = np.power(wEtaVals[:,0] - wEtaVals[:,1], 2)
        dPhi = wPhiVals[:,0] - wPhiVals[:,1]
        dR = np.sqrt((( abs(abs(dPhi)-np.pi)-np.pi )**2+(deta)**2)).reshape([-1,len(genWDaughters_eta)/2, 2])

        matches[dR.max(axis=2).min(axis=1) < 0.6] = 2

    if len(genTopDaughters_eta):

        topEtaVals = np.array(np.meshgrid(fatJetEta, genTopDaughters_eta)).T.reshape(-1,2)
        topPhiVals = np.array(np.meshgrid(fatJetPhi, genTopDaughters_phi)).T.reshape(-1,2)
    
        ## Using ufunc for vector operation
        deta = np.power(topEtaVals[:,0] - topEtaVals[:,1], 2)
        dPhi = topPhiVals[:,0] - topPhiVals[:,1]
        dR = np.sqrt((( abs(abs(dPhi)-np.pi)-np.pi )**2+(deta)**2)).reshape([-1,len(genTopDaughters_eta)/3, 3])

        matches[dR.max(axis=2).min(axis=1) < 0.6] = 1
    
    return matches

class SoftBDeepAK8SFProducer(Module):
    def __init__(self, era, taggerWD, isData = False, isFastSim=False, sampleName=None):
        self.era = era
        self.taggerWD = taggerWD
        self.isFastSim = isFastSim
        self.isData = isData
        self.sampleName = sampleName

        ROOT.TH1.AddDirectory(False)

        #create a numpy friendly version of the SF maps 

        def createSFMap(inputData):
            return {
                "edges": np.unique([edge  for pair in inputData[self.era] for edge in pair[0]]),
                "values": np.array([pair[1][0] for pair in inputData[self.era]]),
                "errors": np.array([pair[1][1] for pair in inputData[self.era]]),
                }
            
        self.topWSFMap = {}
        self.topWSFMap["DeepTop_SF"] = createSFMap(DeepTop_SF)
        self.topWSFMap["DeepTop_Fake_SF"] = createSFMap(DeepTop_Fake_SF)
        self.topWSFMap["DeepTop_fastSF"] = createSFMap(DeepTop_fastSF)
        self.topWSFMap["DeepW_SF"] = createSFMap(DeepW_SF)
        self.topWSFMap["DeepW_Fake_SF"] = createSFMap(DeepW_Fake_SF)
        self.topWSFMap["DeepW_fastSF"] = createSFMap(DeepW_fastSF)

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        # self.out.branch("SB_SF"        , "F", lenVar="nSB")
        # self.out.branch("SB_SFerr"     , "F", lenVar="nSB")
        # self.out.branch("SB_fastSF"    , "F", lenVar="nSB")
        # self.out.branch("SB_fastSFerr" , "F", lenVar="nSB")
        self.out.branch("FatJet_SF"        , "F", lenVar="nFatJet")
        self.out.branch("FatJet_SFerr"     , "F", lenVar="nFatJet")
        self.out.branch("FatJet_fastSF"    , "F", lenVar="nFatJet")
        self.out.branch("FatJet_fastSFerr" , "F", lenVar="nFatJet")
        if not self.isData:
            self.out.branch("Stop0l_DeepAK8_SFWeight" , "F")
            self.out.branch("Stop0l_DeepAK8_SFWeight_total_up" , "F")
            self.out.branch("Stop0l_DeepAK8_SFWeight_total_dn" , "F")
            self.out.branch("Stop0l_DeepAK8_SFWeight_top_up" , "F")
            self.out.branch("Stop0l_DeepAK8_SFWeight_top_dn" , "F")
            self.out.branch("Stop0l_DeepAK8_SFWeight_w_up" , "F")
            self.out.branch("Stop0l_DeepAK8_SFWeight_w_dn" , "F")
            self.out.branch("Stop0l_DeepAK8_SFWeight_veto_up" , "F")
            self.out.branch("Stop0l_DeepAK8_SFWeight_veto_dn" , "F")
            self.out.branch("Stop0l_DeepAK8_SFWeight_densetop_up" , "F")
            self.out.branch("Stop0l_DeepAK8_SFWeight_densetop_dn" , "F")
            if self.isFastSim:
                self.out.branch("Stop0l_DeepAK8_SFWeight_fast", "F")
                self.out.branch("Stop0l_DeepAK8_SFWeight_fast_total_up", "F")
                self.out.branch("Stop0l_DeepAK8_SFWeight_fast_total_dn", "F")
                self.out.branch("Stop0l_DeepAK8_SFWeight_fast_top_up", "F")
                self.out.branch("Stop0l_DeepAK8_SFWeight_fast_top_dn", "F")
                self.out.branch("Stop0l_DeepAK8_SFWeight_fast_w_up", "F")
                self.out.branch("Stop0l_DeepAK8_SFWeight_fast_w_dn", "F")
                self.out.branch("Stop0l_DeepAK8_SFWeight_fast_veto_up", "F")
                self.out.branch("Stop0l_DeepAK8_SFWeight_fast_veto_dn", "F")
        self.out.branch("FatJet_nGenPart" , "I", lenVar="nFatJet", title="NO. of quarks and hard gluons matched to FatJet")
        self.out.branch("FatJet_GenMatch" , "I", lenVar="nFatJet", title="Type of Gen Match of FatJet: 1 match to top, 2 match to W")

        if not self.isData:
            if self.isFastSim:
                import re
                filename_  = os.path.splitext(os.path.basename(inputFile.GetName()))[0]
                sample = re.split("_Skim|_split", filename_)[0]
            else:
                # For QCD smear, using the orignal QCD
                sample = self.sampleName.replace("Smear_", "")

            defaultSampleName = "TTbarInc_%s"%self.era
    
            #get top eff histos
            def getRatioHist(name, sample, tTagEffFile):
                h_den = tTagEffFile.Get(sample + "/d_" + name.split("_as_")[0] + "_" + sample)
                h_num = tTagEffFile.Get(sample + "/n_" + name + "_" + sample)
    
    
                try:
                    h_num.Divide(h_den)
                except AttributeError:
                    print("SoftBDeepAK8Producer: Sample '%s' NOT found in '%s'!!! Instead trying default sample '%s'"%(sample, tTagEffFileName, defaultSampleName))  
                    sample = defaultSampleName
                    h_den = tTagEffFile.Get(sample + "/d_" + name.split("_as_")[0] + "_" + sample)
                    h_num = tTagEffFile.Get(sample + "/n_" + name + "_" + sample)
                    h_num.Divide(h_den)
    
    
                retval = {
                    "edges": np.fromiter(h_num.GetXaxis().GetXbins(), np.float),
                    "values": np.array([h_num.GetBinContent(iBin) for iBin in range(1, h_num.GetNbinsX() + 1)])
                    }
                
                return retval
    
            tTagEffFileName = self.taggerWD + "/tTagEff_%(era)s.root"%{"era":self.era}
    
            tTagEffFile = ROOT.TFile.Open(tTagEffFileName)
    
            self.topEffHists = {}
            self.topEffHists["t_as_t"] = getRatioHist("merged_t_as_t", sample, tTagEffFile)
            self.topEffHists["t_as_w"] = getRatioHist("merged_t_as_w", sample, tTagEffFile)
            self.topEffHists["w_as_t"] = getRatioHist("merged_w_as_t", sample, tTagEffFile)
            self.topEffHists["w_as_w"] = getRatioHist("merged_w_as_w", sample, tTagEffFile)
            self.topEffHists["bg_as_t"] = getRatioHist("merged_bg_as_t", sample, tTagEffFile)
            self.topEffHists["bg_as_w"] = getRatioHist("merged_bg_as_w", sample, tTagEffFile)
    
            tTagEffFile.Close()



    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def GetSoftBSF(self, sbs):
        stop0l       = np.fromiter([sb.Stop0l for sb in sbs], bool)
        nsb          = len(stop0l)
        sb_sf        = [1.] * nsb
        sb_sferr     = [0.] * nsb
        sb_fastsf    = [1.] * nsb
        sb_fastsferr = [0.] * nsb

        if self.isData:
            return sb_sf, sb_sferr, sb_fastsf, sb_fastsferr

        sb_sf  = stop0l * SoftB_SF[self.era][0]
        sb_sferr  = stop0l * SoftB_SF[self.era][1]
        if self.isFastSim:
            sb_fastsf  = stop0l * SoftB_fastSF[self.era][0]
            sb_fastsferr  = stop0l * SoftB_fastSF[self.era][1]

        return sb_sf, sb_sferr, sb_fastsf, sb_fastsferr

    def GetDeepAK8SF(self, fatJetGenMatch, jetPt, stop0l):
        ntop          = len(stop0l)
        self.top_sf        = np.ones(ntop)
        self.top_sferr     = np.zeros(ntop)
        self.top_fastsf    = np.ones(ntop)
        self.top_fastsferr = np.zeros(ntop)

        bgFilter = stop0l==0
        nbg = len(bgFilter[bgFilter])
        self.top_sf_bg_t     = np.ones(nbg)
        self.top_sf_bg_t_err = np.zeros(nbg)
        self.top_sf_bg_w     = np.ones(nbg)
        self.top_sf_bg_w_err = np.zeros(nbg)

        self.top_fastsf_bg_t     = np.ones(nbg)
        self.top_fastsf_bg_t_err = np.zeros(nbg)
        self.top_fastsf_bg_w     = np.ones(nbg)
        self.top_fastsf_bg_w_err = np.zeros(nbg)

        if self.isData:
            return

        def setSF(jetPt, filt, SFMap, sf_top, sf_topErr):
            sfBins = np.digitize(jetPt[filt], SFMap["edges"][:-1]) - 1
            sf_top[filt] = SFMap["values"][sfBins]
            sf_topErr[filt] = SFMap["errors"][sfBins]
       
        #veto SF for non-tagged jets in computed below because it needs to be weighted by efficiency 
        setSF(jetPt, (fatJetGenMatch == 1) & (stop0l == 1), self.topWSFMap["DeepTop_SF"],      self.top_sf, self.top_sferr)
        setSF(jetPt, (fatJetGenMatch != 1) & (stop0l == 1), self.topWSFMap["DeepTop_Fake_SF"], self.top_sf, self.top_sferr)
        setSF(jetPt, (fatJetGenMatch == 2) & (stop0l == 2), self.topWSFMap["DeepW_SF"],        self.top_sf, self.top_sferr)
        setSF(jetPt, (fatJetGenMatch != 2) & (stop0l == 2), self.topWSFMap["DeepW_Fake_SF"],   self.top_sf, self.top_sferr)

        setSF(jetPt[bgFilter], fatJetGenMatch[bgFilter] == 1, self.topWSFMap["DeepTop_SF"],      self.top_sf_bg_t, self.top_sf_bg_t_err)
        setSF(jetPt[bgFilter], fatJetGenMatch[bgFilter] != 1, self.topWSFMap["DeepTop_Fake_SF"], self.top_sf_bg_t, self.top_sf_bg_t_err)
        setSF(jetPt[bgFilter], fatJetGenMatch[bgFilter] == 2, self.topWSFMap["DeepW_SF"],        self.top_sf_bg_w, self.top_sf_bg_w_err)
        setSF(jetPt[bgFilter], fatJetGenMatch[bgFilter] != 2, self.topWSFMap["DeepW_Fake_SF"],   self.top_sf_bg_w, self.top_sf_bg_w_err)

        setSF(jetPt,                          stop0l == 1 , self.topWSFMap["DeepTop_fastSF"],  self.top_fastsf, self.top_fastsferr)
        setSF(jetPt,                          stop0l == 2 , self.topWSFMap["DeepW_fastSF"],    self.top_fastsf, self.top_fastsferr)

        setSF(jetPt[bgFilter], np.ones(nbg).astype(bool) , self.topWSFMap["DeepTop_fastSF"],  self.top_fastsf_bg_t, self.top_fastsf_bg_t_err)
        setSF(jetPt[bgFilter], np.ones(nbg).astype(bool) , self.topWSFMap["DeepW_fastSF"],    self.top_fastsf_bg_w, self.top_fastsf_bg_w_err)

        return

    class TTreeReaderArrayWrapper:
        def __init__(self, ttarray):
            self.ttarray = ttarray

        def __iter__(self):
            for i in xrange(len(self.ttarray)):
                yield self.ttarray[i]
            return

    def nGenParts(self, event):
        if not self.isData:
            GenPart_pdgId = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_pdgId), int)
            GenPart_statusFlags = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_statusFlags), int)
            GenPart_eta = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_eta), float)
            GenPart_phi = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_phi), float)

            fatJet_eta = np.fromiter(self.TTreeReaderArrayWrapper(event.FatJet_eta), float)
            fatJet_phi = np.fromiter(self.TTreeReaderArrayWrapper(event.FatJet_phi), float)

            # statusFlag 0x2100 corresponds to "isLastCopy and fromHardProcess"
            # statusFlag 0x2080 corresponds to "IsLastCopy and isHardProcess"
            genPartsFilt = (((abs(GenPart_pdgId) >= 1) & (abs(GenPart_pdgId) <= 5)) | (abs(GenPart_pdgId) == 21)) & (((GenPart_statusFlags & 0x2100) == 0x2100) | ((GenPart_statusFlags & 0x2080) == 0x2080))

            #calculate deltaR matches
            etas = np.array(np.meshgrid(fatJet_eta, GenPart_eta[genPartsFilt])).T
            deta = np.power(etas[:, :, 0] - etas[:, :, 1], 2)
            phis = np.array(np.meshgrid(fatJet_phi, GenPart_phi[genPartsFilt])).T
            dPhi = phis[:, :, 0] - phis[:, :, 1]
            np.subtract(dPhi, 2*math.pi, out = dPhi, where= (dPhi >=math.pi))
            np.add(dPhi, 2*math.pi,  out =dPhi , where=(dPhi < -1*math.pi))
            np.power(dPhi, 2, out=dPhi)
            dR2 = np.add(deta, dPhi)
            nGenPartMatch = (dR2 < 0.6*0.6).sum(axis=1)
            return nGenPartMatch
        else:
            return np.zeros(len(event.FatJet_pt)).astype(int)

    def fatJetGenMatch(self, event, fatJetEta, fatJetPhi):
        
        if self.isData:
            return np.zeros(fatJetEta.shape).astype(int)

        GenPart_eta              = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_eta),              dtype=float)
        GenPart_phi              = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_phi),              dtype=float)

        GenPart_genPartIdxMother = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_genPartIdxMother), dtype=int)
        GenPart_pdgId            = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_pdgId),            dtype=int)
        GenPart_statusFlags      = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_statusFlags),      dtype=int)
    
        genTopDaughters_list, genWDaughters_list = genParticleAssociation(GenPart_genPartIdxMother, GenPart_pdgId, GenPart_statusFlags)
    
        genTopDaughters, genWDaughters = np.array(genTopDaughters_list), np.array(genWDaughters_list)
    
        if(len(genTopDaughters)):
            genTopDaughters_eta = GenPart_eta[genTopDaughters]
            genTopDaughters_phi = GenPart_phi[genTopDaughters]
        else:
            genTopDaughters_eta = np.array([])
            genTopDaughters_phi = np.array([])
    
        if len(genWDaughters):
            genWDaughters_eta = GenPart_eta[genWDaughters]
            genWDaughters_phi = GenPart_phi[genWDaughters]
        else:
            genWDaughters_eta = np.array([])
            genWDaughters_phi = np.array([])
    
        return deltaRMatch(fatJetEta, fatJetPhi, genTopDaughters_eta, genTopDaughters_phi, genWDaughters_eta, genWDaughters_phi)

    def calculateTopSFWeight(self, fatJetStop0l, fatJetPt, fatJetGenMatch, nGenPart):

        #Get efficiencies 
        def setEff(topPt, catName, topEff, filterArray):
            effBins_top = np.digitize(topPt[filterArray], self.topEffHists[catName]["edges"][:-1]) - 1
            topEff[filterArray] =  self.topEffHists[catName]["values"][effBins_top]

        topEff_t = np.ones(len(self.top_sf_bg_t))
        topEff_w = np.ones(len(self.top_sf_bg_w))

        recoBGFilter = fatJetStop0l == 0

        setEff(fatJetPt[recoBGFilter], "t_as_t",  topEff_t, fatJetGenMatch[recoBGFilter] == 1)
        setEff(fatJetPt[recoBGFilter], "w_as_t",  topEff_t, fatJetGenMatch[recoBGFilter] == 2)
        setEff(fatJetPt[recoBGFilter], "bg_as_t", topEff_t, fatJetGenMatch[recoBGFilter] == 0)
        setEff(fatJetPt[recoBGFilter], "t_as_w",  topEff_w, fatJetGenMatch[recoBGFilter] == 1)
        setEff(fatJetPt[recoBGFilter], "w_as_w",  topEff_w, fatJetGenMatch[recoBGFilter] == 2)
        setEff(fatJetPt[recoBGFilter], "bg_as_w", topEff_w, fatJetGenMatch[recoBGFilter] == 0)

        #safety against very rare cases where eff = 0
        topEff_t[topEff_t <= 0.0001] = 0.0001
        topEff_w[topEff_w <= 0.0001] = 0.0001

        topSF_t_tagged  = self.top_sf[fatJetStop0l == 1]
        topSF_w_tagged  = self.top_sf[fatJetStop0l == 2]

        denseTopFilter = (nGenPart >= 4)[fatJetStop0l == 1].astype(float)

        numerator = topSF_t_tagged.prod() * topSF_w_tagged.prod() * (1 - topEff_t*self.top_sf_bg_t - topEff_w*self.top_sf_bg_w).prod()

        denominator = (1 - topEff_t - topEff_w).prod()

        if self.isFastSim:
            topSF_fast_t_tagged  = self.top_fastsf[fatJetStop0l == 1]
            topSF_fast_w_tagged  = self.top_fastsf[fatJetStop0l == 2]

            numerator_fast = (topSF_t_tagged*topSF_fast_t_tagged).prod() * (topSF_w_tagged*topSF_fast_w_tagged).prod() * (1 - topEff_t*self.top_sf_bg_t*self.top_fastsf_bg_t - topEff_w*self.top_sf_bg_w*self.top_fastsf_bg_w).prod()


        #calculate uncertainty variations of weight
        if not self.isData:
            uncert_t = self.top_sferr[fatJetStop0l == 1]
            uncert_w = self.top_sferr[fatJetStop0l == 2]
        
            numerator_up = (topSF_t_tagged + uncert_t).prod() * (topSF_w_tagged + uncert_w).prod() * (1 - topEff_t*(self.top_sf_bg_t + self.top_sf_bg_t_err) - topEff_w*(self.top_sf_bg_w + self.top_sf_bg_w_err)).prod()
            numerator_dn = (topSF_t_tagged - uncert_t).prod() * (topSF_w_tagged - uncert_w).prod() * (1 - topEff_t*(self.top_sf_bg_t - self.top_sf_bg_t_err) - topEff_w*(self.top_sf_bg_w - self.top_sf_bg_w_err)).prod()

            numerator_t_up = (topSF_t_tagged + uncert_t).prod() * (topSF_w_tagged).prod()            * (1 - topEff_t*(self.top_sf_bg_t)                        - topEff_w*(self.top_sf_bg_w)).prod()
            numerator_t_dn = (topSF_t_tagged - uncert_t).prod() * (topSF_w_tagged).prod()            * (1 - topEff_t*(self.top_sf_bg_t)                        - topEff_w*(self.top_sf_bg_w)).prod()
            numerator_w_up = (topSF_t_tagged).prod()            * (topSF_w_tagged + uncert_w).prod() * (1 - topEff_t*(self.top_sf_bg_t)                        - topEff_w*(self.top_sf_bg_w)).prod()
            numerator_w_dn = (topSF_t_tagged).prod()            * (topSF_w_tagged - uncert_w).prod() * (1 - topEff_t*(self.top_sf_bg_t)                        - topEff_w*(self.top_sf_bg_w)).prod()
            numerator_v_up = (topSF_t_tagged).prod()            * (topSF_w_tagged).prod()            * (1 - topEff_t*(self.top_sf_bg_t + self.top_sf_bg_t_err) - topEff_w*(self.top_sf_bg_w + self.top_sf_bg_w_err)).prod()
            numerator_v_dn = (topSF_t_tagged).prod()            * (topSF_w_tagged).prod()            * (1 - topEff_t*(self.top_sf_bg_t - self.top_sf_bg_t_err) - topEff_w*(self.top_sf_bg_w - self.top_sf_bg_w_err)).prod()

            numerator_densetop_up = (topSF_t_tagged*(1+0.2*denseTopFilter)).prod() * topSF_w_tagged.prod() * (1 - topEff_t*self.top_sf_bg_t - topEff_w*self.top_sf_bg_w).prod()
            numerator_densetop_dn = (topSF_t_tagged/(1+0.2*denseTopFilter)).prod() * topSF_w_tagged.prod() * (1 - topEff_t*self.top_sf_bg_t - topEff_w*self.top_sf_bg_w).prod()

            if self.isFastSim:
                uncert_fast_t  = self.top_fastsferr[fatJetStop0l == 1]
                uncert_fast_w  = self.top_fastsferr[fatJetStop0l == 2]

                numerator_fast_up = (topSF_t_tagged*(topSF_fast_t_tagged + uncert_fast_t)).prod() * (topSF_w_tagged*(topSF_fast_w_tagged + uncert_fast_w)).prod() * (1 - topEff_t*self.top_sf_bg_t*(self.top_fastsf_bg_t + self.top_fastsf_bg_t_err) - topEff_w*self.top_sf_bg_w*(self.top_fastsf_bg_w + self.top_fastsf_bg_w_err)).prod()
                numerator_fast_dn = (topSF_t_tagged*(topSF_fast_t_tagged - uncert_fast_t)).prod() * (topSF_w_tagged*(topSF_fast_w_tagged - uncert_fast_w)).prod() * (1 - topEff_t*self.top_sf_bg_t*(self.top_fastsf_bg_t - self.top_fastsf_bg_t_err) - topEff_w*self.top_sf_bg_w*(self.top_fastsf_bg_w - self.top_fastsf_bg_w_err)).prod()

                numerator_fast_t_up = (topSF_t_tagged*(topSF_fast_t_tagged + uncert_fast_t)).prod() * (topSF_w_tagged*(topSF_fast_w_tagged)).prod()                 * (1 - topEff_t*self.top_sf_bg_t*(self.top_fastsf_bg_t)                            - topEff_w*self.top_sf_bg_w*(self.top_fastsf_bg_w)).prod()
                numerator_fast_t_dn = (topSF_t_tagged*(topSF_fast_t_tagged - uncert_fast_t)).prod() * (topSF_w_tagged*(topSF_fast_w_tagged)).prod()                 * (1 - topEff_t*self.top_sf_bg_t*(self.top_fastsf_bg_t)                            - topEff_w*self.top_sf_bg_w*(self.top_fastsf_bg_w)).prod()
                numerator_fast_w_up = (topSF_t_tagged*(topSF_fast_t_tagged)).prod()                 * (topSF_w_tagged*(topSF_fast_w_tagged + uncert_fast_w)).prod() * (1 - topEff_t*self.top_sf_bg_t*(self.top_fastsf_bg_t)                            - topEff_w*self.top_sf_bg_w*(self.top_fastsf_bg_w)).prod()
                numerator_fast_w_dn = (topSF_t_tagged*(topSF_fast_t_tagged)).prod()                 * (topSF_w_tagged*(topSF_fast_w_tagged - uncert_fast_w)).prod() * (1 - topEff_t*self.top_sf_bg_t*(self.top_fastsf_bg_t)                            - topEff_w*self.top_sf_bg_w*(self.top_fastsf_bg_w)).prod()
                numerator_fast_v_up = (topSF_t_tagged*(topSF_fast_t_tagged)).prod()                 * (topSF_w_tagged*(topSF_fast_w_tagged)).prod()                 * (1 - topEff_t*self.top_sf_bg_t*(self.top_fastsf_bg_t + self.top_fastsf_bg_t_err) - topEff_w*self.top_sf_bg_w*(self.top_fastsf_bg_w + self.top_fastsf_bg_w_err)).prod()
                numerator_fast_v_dn = (topSF_t_tagged*(topSF_fast_t_tagged)).prod()                 * (topSF_w_tagged*(topSF_fast_w_tagged)).prod()                 * (1 - topEff_t*self.top_sf_bg_t*(self.top_fastsf_bg_t - self.top_fastsf_bg_t_err) - topEff_w*self.top_sf_bg_w*(self.top_fastsf_bg_w - self.top_fastsf_bg_w_err)).prod()




            else:
                numerator_fast_up = 0.0
                numerator_fast_dn = 0.0

                numerator_fast_t_up = 0.0
                numerator_fast_t_dn = 0.0
                numerator_fast_w_up = 0.0
                numerator_fast_w_dn = 0.0
                numerator_fast_v_up = 0.0
                numerator_fast_v_dn = 0.0

            self.out.fillBranch("Stop0l_DeepAK8_SFWeight" , numerator/denominator)
            self.out.fillBranch("Stop0l_DeepAK8_SFWeight_total_up" , numerator_up/denominator)
            self.out.fillBranch("Stop0l_DeepAK8_SFWeight_total_dn" , numerator_dn/denominator)
            self.out.fillBranch("Stop0l_DeepAK8_SFWeight_top_up" , numerator_t_up/denominator)
            self.out.fillBranch("Stop0l_DeepAK8_SFWeight_top_dn" , numerator_t_dn/denominator)
            self.out.fillBranch("Stop0l_DeepAK8_SFWeight_w_up" , numerator_w_up/denominator)
            self.out.fillBranch("Stop0l_DeepAK8_SFWeight_w_dn" , numerator_w_dn/denominator)
            self.out.fillBranch("Stop0l_DeepAK8_SFWeight_veto_up" , numerator_v_up/denominator)
            self.out.fillBranch("Stop0l_DeepAK8_SFWeight_veto_dn" , numerator_v_dn/denominator)
            self.out.fillBranch("Stop0l_DeepAK8_SFWeight_densetop_up" , numerator_densetop_up/denominator)
            self.out.fillBranch("Stop0l_DeepAK8_SFWeight_densetop_dn" , numerator_densetop_dn/denominator)
            if self.isFastSim:
                self.out.fillBranch("Stop0l_DeepAK8_SFWeight_fast" , numerator_fast/denominator)
                self.out.fillBranch("Stop0l_DeepAK8_SFWeight_fast_total_up" , numerator_fast_up/denominator)
                self.out.fillBranch("Stop0l_DeepAK8_SFWeight_fast_total_dn" , numerator_fast_dn/denominator)
                self.out.fillBranch("Stop0l_DeepAK8_SFWeight_fast_top_up", numerator_fast_t_up/denominator)
                self.out.fillBranch("Stop0l_DeepAK8_SFWeight_fast_top_dn", numerator_fast_t_dn/denominator)
                self.out.fillBranch("Stop0l_DeepAK8_SFWeight_fast_w_up", numerator_fast_w_up/denominator)
                self.out.fillBranch("Stop0l_DeepAK8_SFWeight_fast_w_dn", numerator_fast_w_dn/denominator)
                self.out.fillBranch("Stop0l_DeepAK8_SFWeight_fast_veto_up", numerator_fast_v_up/denominator)
                self.out.fillBranch("Stop0l_DeepAK8_SFWeight_fast_veto_dn", numerator_fast_v_dn/denominator)


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        # isvs    = Collection(event, "SB")
        fatjets  = Collection(event, "FatJet")

        fatJetStop0l = np.fromiter(self.TTreeReaderArrayWrapper(event.FatJet_Stop0l), dtype=int)
        fatJetPt = np.fromiter(self.TTreeReaderArrayWrapper(event.FatJet_pt), dtype=float)
        fatJetEta = np.fromiter(self.TTreeReaderArrayWrapper(event.FatJet_eta), dtype=float)
        fatJetPhi = np.fromiter(self.TTreeReaderArrayWrapper(event.FatJet_phi), dtype=float)

        #gen match the fat jets
        fatJetGenMatch = self.fatJetGenMatch(event, fatJetEta, fatJetPhi)

        #add additional uncertainty for tops with more than 3 gen particles matched 
        nGenPart = self.nGenParts(event)

        fatJetPtFilter = fatJetPt >= 200.0
        # sb_sf, sb_sferr, sb_fastsf, sb_fastsferr = self.GetSoftBSF(isvs)
        self.GetDeepAK8SF(fatJetGenMatch[fatJetPtFilter], fatJetPt[fatJetPtFilter], fatJetStop0l[fatJetPtFilter])

        ### Store output
        # self.out.fillBranch("SB_SF",        sb_sf)
        # self.out.fillBranch("SB_SFerr",     sb_sferr)
        # self.out.fillBranch("SB_fastSF",    sb_fastsf)
        # self.out.fillBranch("SB_fastSFerr", sb_fastsferr)
        self.out.fillBranch("FatJet_SF",        self.top_sf)
        self.out.fillBranch("FatJet_SFerr",     self.top_sferr)
        self.out.fillBranch("FatJet_fastSF",    self.top_fastsf)
        self.out.fillBranch("FatJet_fastSFerr", self.top_fastsferr)
        self.out.fillBranch("FatJet_nGenPart",  nGenPart)
        self.out.fillBranch("FatJet_GenMatch",  fatJetGenMatch)

        if not self.isData:
            ### store all event weights for merged top/W 
            # apply pT cut before calculation 
            self.calculateTopSFWeight(fatJetStop0l[fatJetPtFilter], fatJetPt[fatJetPtFilter], fatJetGenMatch[fatJetPtFilter], nGenPart[fatJetPtFilter])
        return True
