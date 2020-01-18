import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
from collections import defaultdict
from itertools import permutations
import numpy as np
import itertools

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoSUSYTools.modules.Stop0lObjectsProducer import DeepCSVMediumWP, DeepCSVLooseWP

from PhysicsTools.NanoSUSYTools.modules.datamodelRemap import ObjectRemapped, CollectionRemapped

class DeepTopProducer(Module):
    def __init__(self, era, applyUncert=None):
        ## WP from Hui's study https://indico.cern.ch/event/780000/contributions/3248659/attachments/1768782/2873013/Search_bin_study_with_combine_tools_v13.pdf
        ## Updated WP from https://indico.cern.ch/event/840827/contributions/3527925/attachments/1895214/3126510/DeepAK8_Top_W_SFs_2017_JMAR_PK.pdf
        self.minAK8TopMass = 105
        self.maxAK8TopMass = 999999
        self.DeepAK8TopPt  = 400.0 # Using 400 Pt cut 
        ## Mistag 0.5% WP, using 2017 WP as 2018
        self.DeepAK8TopWP  = {
            "2016" : 0.937,
            "2017" : 0.895,
            "2018" : 0.895
        }

        ## Mistag 0.5% WP, using 2017 WP as 2018
        self.minAK8WMass   = 65
        self.maxAK8WMass   = 105
        self.DeepAK8WPt    = 200.0
        self.DeepAK8WWP    = {
            "2016" : 0.973,
            "2017" : 0.991,
            "2018" : 0.991
        }

        self.DeepResolveWP = 0.92
        self.etaMax        = 2.0
        self.bJetEtaMax    = 2.4
        self.resAK4bTagWP  = DeepCSVMediumWP[era]
        self.dR2AK4Subjet  = 0.4*0.4
        self.era = era
        self.metBranchName = "MET"

        #get resolved top eff histos
        tTagEffFileName = "tTagEff_2016.root"
        sample = "ttHToNonbb_2016"

        ROOT.TH1.AddDirectory(False)
        tTagEffFile = ROOT.TFile.Open(tTagEffFileName)
        
        h_res_sig_den = tTagEffFile.Get("d_res_sig_" + sample)
        h_res_sig = tTagEffFile.Get("n_res_sig_" + sample)
        h_res_bg_den = tTagEffFile.Get("d_res_bg_" + sample)
        h_res_bg = tTagEffFile.Get("n_res_bg_" + sample)

        tTagEffFile.Close()

        h_res_sig.Divide(h_res_sig_den)
        h_res_bg.Divide(h_res_bg_den)

        self.resEffHists = {
            "res_sig_hist": {
                "edges": np.fromiter(h_res_sig.GetXaxis().GetXbins(), np.float),
                "values": np.array([h_res_sig.GetBinContent(iBin) for iBin in range(1, h_res_sig.GetNbinsX() + 1)])
                },
            "res_bg_hist": {
                "edges": np.fromiter(h_res_bg.GetXaxis().GetXbins(), np.float),
                "values": np.array([h_res_bg.GetBinContent(iBin) for iBin in range(1, h_res_bg.GetNbinsX() + 1)])
                },
            }
        print(self.resEffHists)

        self.applyUncert = applyUncert

        self.suffix = ""

        if self.applyUncert == "JESUp":
            self.suffix = "_JESUp"
        elif self.applyUncert == "JESDown":
            self.suffix = "_JESDown"

    def beginJob(self):
        self.count = 1
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("FatJet_Stop0l", "I", lenVar="nFatJet")
        self.out.branch("ResolvedTop_Stop0l" + self.suffix, "O", lenVar="nResolvedTopCandidate" + self.suffix)
        self.out.branch("Stop0l_nTop" + self.suffix, "I")
        self.out.branch("Stop0l_nW" + self.suffix, "I")
        self.out.branch("Stop0l_nResolved" + self.suffix, "I")
        self.out.branch("Stop0l_ISRJetIdx" + self.suffix, "I")
        self.out.branch("Stop0l_ISRJetPt" + self.suffix, "F")
        self.out.branch("Stop0l_ResTopWeight" + self.suffix, "F")
        if not self.applyUncert:
            self.out.branch("Stop0l_ResTopWeight_Up" + self.suffix, "F")
            self.out.branch("Stop0l_ResTopWeight_Dn" + self.suffix, "F")
        self.out.branch("HOT_pt" + self.suffix,   "F", lenVar = "nHOT" + self.suffix)
        self.out.branch("HOT_eta" + self.suffix,  "F", lenVar = "nHOT" + self.suffix)
        self.out.branch("HOT_phi" + self.suffix,  "F", lenVar = "nHOT" + self.suffix)
        self.out.branch("HOT_mass" + self.suffix, "F", lenVar = "nHOT" + self.suffix)
        self.out.branch("HOT_type" + self.suffix, "I", lenVar = "nHOT" + self.suffix)

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def SelDeepAK8(self, fatj):
        if fatj.deepTag_TvsQCD > self.DeepAK8TopWP[self.era] and fatj.msoftdrop >= self.minAK8TopMass \
           and fatj.msoftdrop < self.maxAK8TopMass and fatj.pt > self.DeepAK8TopPt and abs(fatj.eta) < self.etaMax:
            return 1
        elif fatj.deepTag_WvsQCD > self.DeepAK8WWP[self.era] and fatj.msoftdrop >= self.minAK8WMass \
                and fatj.msoftdrop < self.maxAK8WMass and fatj.pt > self.DeepAK8WPt and abs(fatj.eta) < self.etaMax:
            return 2
        else:
            return 0

    def SelDeepResolved(self, res, jets):
        if math.fabs(res.eta) >= self.etaMax:
            return False
        #Moved elsewhere 
        #if res.discriminator <= self.DeepResolveWP:
        #    return False

        if ((abs(jets[res.j1Idx].eta) < self.bJetEtaMax and jets[res.j1Idx].btagDeepB > self.resAK4bTagWP) + (abs(jets[res.j2Idx].eta) < self.bJetEtaMax and jets[res.j2Idx].btagDeepB > self.resAK4bTagWP) + (abs(jets[res.j3Idx].eta) < self.bJetEtaMax and jets[res.j3Idx].btagDeepB > self.resAK4bTagWP)) >= 2 :
            return False
        return True

    def DeepResolvedDiscCut(self, res):
        #res here is a list with the resolved top and the existing Stop0l var
        return res[1] and (res[0].discriminator > self.DeepResolveWP)

    def ResovleOverlapDeepAK8(self, res, fatj, jets, subjets):
        ## Counting number of tops
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Getting jets ~~~~~
        ### Subjet method
        subjetides  = []
        for i, j in enumerate(fatj):
            if self.FatJet_Stop0l[i] > 0 :
                subjetides.append(j.subJetIdx1)
                subjetides.append(j.subJetIdx2)
        ### Resolved AK4 jets
        resjets = defaultdict(list)
        for i, t in enumerate(res):
            if self.ResolvedTop_Stop0l[i]:
                resjets[t.j1Idx].append(i)
                resjets[t.j2Idx].append(i)
                resjets[t.j3Idx].append(i)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Making correlation ~~~~~

        if len(subjetides) > 0 and len(resjets) > 0:
            combs = np.asarray([(x,y) for x in subjetides for y in resjets.keys() ])
            subjet_eta = np.asarray([ subjets[x].eta for x in combs[:, 0] ])
            subjet_phi = np.asarray([ subjets[x].phi for x in combs[:, 0] ])
            jet_eta = np.asarray([ jets[x].eta for x in combs[:, 1] ])
            jet_phi = np.asarray([ jets[x].phi for x in combs[:, 1] ])
            ## Using ufunc for vector operation
            deta = np.power(subjet_eta-jet_eta, 2)
            dPhi = subjet_phi - jet_phi
            np.subtract(dPhi, 2*math.pi, out = dPhi, where= (dPhi >=math.pi))
            np.add(dPhi, 2*math.pi,  out =dPhi , where=(dPhi < -1*math.pi))
            np.power(dPhi, 2, out=dPhi)
            dR2 = np.add(deta, dPhi)
            overlap = combs[np.where(dR2 < self.dR2AK4Subjet)]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Killing overlap ~~~~~
            ## Has overlap
            for j in overlap[:, 1]:
                for overlapidx in resjets[j]:
                    self.ResolvedTop_Stop0l[overlapidx] = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Clean up double counting in DeepResolved ~~~~~
        usedJets = set()
        remainingtops = [iTop for iTop in xrange(len(self.ResolvedTop_Stop0l)) if self.ResolvedTop_Stop0l[iTop]]
        #Sort remaining tops by discriminator value
        remainingtops.sort(key=lambda x: -res[x].discriminator)
        if len(remainingtops) > 1:
            for iTop in remainingtops:
                jetIndices = set( (res[iTop].j1Idx, res[iTop].j2Idx, res[iTop].j3Idx) )
                if not (jetIndices & usedJets):
                    #None of this top's jets are "used", its a good top, mark its jets as used
                    usedJets |= jetIndices
                else:
                    #Top has duplicate jet, remove from consideration
                    self.ResolvedTop_Stop0l[iTop] = False

        return True

    def Clear(self):
        self.FatJet_Stop0l = []
        self.ResolvedTop_Stop0l = []

    def GetISRJets(self, fatjets, subjets, met_phi):
        if (self.nTop + self.nW + self.nResolved ) != 0:
            return -1

        if len(fatjets) == 0:
            return -1

        leadingjet = fatjets[0]
        if leadingjet.pt < 200 or math.fabs(leadingjet.eta) > 2.4 or \
           leadingjet.btagDeepB > DeepCSVLooseWP[self.era]:
            return -1

        if leadingjet.subJetIdx1 >= 0 and leadingjet.subJetIdx1 < len(subjets) and \
           subjets[leadingjet.subJetIdx1].btagDeepB >= DeepCSVLooseWP[self.era]:
            return -1

        if leadingjet.subJetIdx2 >= 0 and leadingjet.subJetIdx2 < len(subjets) and \
           subjets[leadingjet.subJetIdx2].btagDeepB >= DeepCSVLooseWP[self.era]:
            return -1

        if math.fabs(ROOT.TVector2.Phi_mpi_pi( leadingjet.phi - met_phi )) < 2:
            return -1

        return 0

    def CreateHOTs(self, fatjets, resolves ):
        ptmap = defaultdict(list) ## in case two tops with same pt
        for i, f in enumerate(fatjets):
            if self.FatJet_Stop0l[i] >0:
                ptmap[f.pt].append(i)

        for i, r in enumerate(resolves):
            if self.ResolvedTop_Stop0l[i]:
                ptmap[r.pt].append(1000 + i)

        HOTpt = []
        HOTeta = []
        HOTphi = []
        HOTmass = []
        HOTtype = []

        for k in sorted(ptmap.keys(), reverse=True):
            for idx in ptmap[k]:
                obj = None
                Type = 0
                if idx >= 1000:
                    obj = resolves[idx-1000]
                    Type = 3
                else:
                    obj = fatjets[idx]
                    Type = self.FatJet_Stop0l[idx]
                HOTpt.append(obj.pt)
                HOTeta.append(obj.eta)
                HOTphi.append(obj.phi)
                HOTmass.append(obj.mass)
                HOTtype.append(Type)
        return (HOTpt, HOTeta, HOTphi, HOTmass, HOTtype)

    def calculateResTopSFWeight(self, res):
        #res here is all resolved tops which survive the overlap removal procedure and final cuts, except the final discriminator cut
        resTopStop0l = np.array(self.ResolvedTop_Stop0l, dtype=bool)
        resTopPt = np.array([topCand.pt for topCand in res])[resTopStop0l]
        resTopSF = np.array([topCand.sf for topCand in res])[resTopStop0l]
        resTopGM = np.array([topCand.genMatch for topCand in res], dtype=bool)[resTopStop0l]
        resTopDisc = np.array([topCand.discriminator for topCand in res], dtype=float)[resTopStop0l]

        #calculate uncertainties 
        if not self.applyUncert:
            systNames=["Btag", "Pileup", "CSPur", "Stat", "Closure"]
            uncert_up = np.zeros(len(resTopPt))
            uncert_dn = np.zeros(len(resTopPt))
            for syst in systNames:
                var_up = np.array([getattr(topCand, "syst_"+syst+"_Up") for topCand in res])[resTopStop0l]
                var_dn = np.array([getattr(topCand, "syst_"+syst+"_Down") for topCand in res])[resTopStop0l]
                # hack
                if syst == "Closure":
                    # closure is only applied to fakes 
                    filt = (~resTopGM).astype(float)
                    uncert_up += (var_up*filt)**2
                    uncert_dn += (var_dn*filt)**2
                else:
                    uncert_up += var_up**2
                    uncert_dn += var_dn**2
        
        #Get efficiencies 
        resTopEff = np.ones(resTopSF.shape)

        resTopPt_top = resTopPt[resTopGM]
        effBins_top = np.digitize(resTopPt_top, self.resEffHists["res_sig_hist"]["edges"]) - 1
        resTopEff[resTopGM] = self.resEffHists["res_sig_hist"]["values"][effBins_top]

        resTopPt_notTop = resTopPt[~resTopGM]
        effBins_notTop = np.digitize(resTopPt_notTop, self.resEffHists["res_bg_hist"]["edges"]) - 1
        resTopEff[~resTopGM] = self.resEffHists["res_bg_hist"]["values"][effBins_notTop]

        discCut = resTopDisc > self.DeepResolveWP

        resTopSF_tagged = resTopSF[discCut]
        resTopSF_notTagged = resTopSF[~discCut]

        resTopEff_tagged = resTopEff[discCut]
        resTopEff_notTagged = resTopEff[~discCut]

        numerator = (resTopSF_tagged*resTopEff_tagged).prod() * (1 - (resTopSF_notTagged*resTopEff_notTagged)).prod()
        denominator = resTopEff_tagged.prod() * (1 - resTopEff_notTagged).prod()

        #calculate uncertainty variations of weight
        if not self.applyUncert:
            uncert_up_tagged = uncert_up[discCut]
            uncert_up_notTagged = uncert_up[~discCut]

            uncert_dn_tagged = uncert_dn[discCut]
            uncert_dn_notTagged = uncert_dn[~discCut]

            numerator_up = ((1 + uncert_up_tagged)*resTopSF_tagged*resTopEff_tagged).prod() * (1 - ((1 + uncert_up_notTagged)*resTopSF_notTagged*resTopEff_notTagged)).prod()
            numerator_dn = ((1 - uncert_dn_tagged)*resTopSF_tagged*resTopEff_tagged).prod() * (1 - ((1 - uncert_dn_notTagged)*resTopSF_notTagged*resTopEff_notTagged)).prod()
        else:
            numerator_up = 0.0
            numerator_dn = 0.0

        return numerator/denominator, numerator_up/denominator, numerator_dn/denominator

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        ## Getting objects
        if self.applyUncert == "JESUp":
            resolves  = Collection(event, "ResolvedTopCandidate_JESUp")
            jets      = CollectionRemapped(event, "Jet", replaceMap={"pt":"pt_jesTotalUp", "mass":"mass_jesTotalUp"})
            met       = ObjectRemapped(event,     "MET", replaceMap={"pt":"pt_jesTotalUp", "phi":"phi_jesTotalUp"})
        elif self.applyUncert == "JESDown":
            resolves  = Collection(event, "ResolvedTopCandidate_JESDown")
            jets      = CollectionRemapped(event, "Jet", replaceMap={"pt":"pt_jesTotalDown", "mass":"mass_jesTotalDown"})
            met       = ObjectRemapped(event,     "MET", replaceMap={"pt":"pt_jesTotalDown", "phi":"phi_jesTotalDown"})
        else:
            resolves  = Collection(event, "ResolvedTopCandidate")
            jets      = Collection(event, "Jet")
            met       = Object(event,     "MET")

        fatjets  = Collection(event, "FatJet")
        subjets  = Collection(event, "SubJet")
        self.Clear()

        ## Selecting objects
        self.FatJet_Stop0l = map(self.SelDeepAK8, fatjets)
        #apply initial selection to reduce combinatorics, discriminator cut moved later for SF calculation
        self.ResolvedTop_Stop0l = map(lambda x : self.SelDeepResolved(x, jets), resolves)
        #resolve overlap between resolved top candidates and between resovled tops and merged top/W
        self.ResovleOverlapDeepAK8(resolves, fatjets, jets, subjets)
        #calcualte resolved top scaler factor (the merged top SF is calculated in SoftBDeepAK8SFProducer.py for ... reasons ...)
        resolvedTopSF, resolvedTopSF_Up, resolvedTopSF_Dn = self.calculateResTopSFWeight(resolves)
        #we need all the overlap resolved candidates in the step above, so the discriminator filter is moved here
        self.ResolvedTop_Stop0l = map(lambda x : self.DeepResolvedDiscCut(x), zip(resolves, self.ResolvedTop_Stop0l))
        self.nTop = sum( [ i for i in self.FatJet_Stop0l if i == 1 ])
        self.nW = sum( [ 1 for i in self.FatJet_Stop0l if i == 2 ])
        self.nResolved = sum(self.ResolvedTop_Stop0l)
        self.ISRJetidx = self.GetISRJets(fatjets, subjets, met.phi)
        ISRJetPt = fatjets[self.ISRJetidx].pt if self.ISRJetidx != -1 else 0
        (HOTpt, HOTeta, HOTphi, HOTmass, HOTtype) =  self.CreateHOTs(fatjets, resolves)

        ### Store output
        self.out.fillBranch("FatJet_Stop0l", self.FatJet_Stop0l)
        self.out.fillBranch("ResolvedTop_Stop0l" + self.suffix, self.ResolvedTop_Stop0l)
        self.out.fillBranch("Stop0l_nTop" + self.suffix, self.nTop)
        self.out.fillBranch("Stop0l_nW" + self.suffix, self.nW)
        self.out.fillBranch("Stop0l_nResolved" + self.suffix, self.nResolved)
        self.out.fillBranch("Stop0l_ISRJetIdx" + self.suffix, self.ISRJetidx)
        self.out.fillBranch("Stop0l_ISRJetPt" + self.suffix, ISRJetPt)
        self.out.fillBranch("Stop0l_ResTopWeight" + self.suffix, resolvedTopSF)
        if not self.applyUncert:
            self.out.fillBranch("Stop0l_ResTopWeight_Up" + self.suffix, resolvedTopSF_Up)
            self.out.fillBranch("Stop0l_ResTopWeight_Dn" + self.suffix, resolvedTopSF_Dn)
        self.out.fillBranch("HOT_pt" + self.suffix, HOTpt)
        self.out.fillBranch("HOT_eta" + self.suffix, HOTeta)
        self.out.fillBranch("HOT_phi" + self.suffix, HOTphi)
        self.out.fillBranch("HOT_mass" + self.suffix, HOTmass)
        self.out.fillBranch("HOT_type" + self.suffix, HOTtype)
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
