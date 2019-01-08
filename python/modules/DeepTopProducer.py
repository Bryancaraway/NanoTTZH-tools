import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
from collections import defaultdict
from itertools import permutations
import numpy as np
import itertools

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoSUSYTools.modules.Stop0lObjectsProducer import DeepCSVMediumWP


class DeepTopProducer(Module):
    def __init__(self, era):
        ## WP from Hui's study https://indico.cern.ch/event/780000/contributions/3248659/attachments/1768782/2873013/Search_bin_study_with_combine_tools_v13.pdf
        self.DeepAK8TopWP  = 0.9377
        self.minAK8TopMass = 105
        self.minAK8WMass = 65
        self.DeepAK8WWP    = 0.9530
        self.DeepResolveWP = 0.92
        self.era = era
        self.metBranchName = "MET"

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("FatJet_Stop0l",      "O", lenVar="nFatJet")
        self.out.branch("ResolvedTop_Stop0l", "O", lenVar="nResolvedTop")
        self.out.branch("Stop0l_nTop", "I")
        self.out.branch("Stop0l_nW", "I")
        self.out.branch("Stop0l_nResolved", "I")
        self.out.branch("Stop0l_ISRJetIdx", "I")
        self.out.branch("Stop0l_ISRJetPt", "F")
        self.out.branch("Stop0l_nHOT", "I")
        self.out.branch("Stop0l_HOTpt",   "F", lenVar = "Stop0l_nHOT")
        self.out.branch("Stop0l_HOTeta",  "F", lenVar = "Stop0l_nHOT")
        self.out.branch("Stop0l_HOTphi",  "F", lenVar = "Stop0l_nHOT")
        self.out.branch("Stop0l_HOTmass", "F", lenVar = "Stop0l_nHOT")
        self.out.branch("Stop0l_HOTtype", "I", lenVar = "Stop0l_nHOT")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def SelDeepAK8(self, fatj):
        if fatj.deepTag_TvsQCD > self.DeepAK8TopWP and fatj.msoftdrop > self.minAK8TopMass:
            return 1
        elif fatj.deepTag_WvsQCD > self.DeepAK8WWP and fatj.msoftdrop > self.minAK8WMass:
            return 2
        else:
            return 0

    def SelDeepResolved(self, res, jets):
        if math.fabs(res.eta) > 2.0:
            return False
        if res.discriminator < self.DeepResolveWP:
            return False
        ## Veto resolved with two b-tagged jets
        if (jets[res.j1Idx].btagStop0l + jets[res.j2Idx].btagStop0l+ jets[res.j3Idx].btagStop0l) >= 2 :
            return False
        return True

    def ResovleOverlapDeepAK8(self, res, fatj, jets, subjets):
        ## Counting number of tops
        if sum(self.FatJet_Stop0l ) == 0  or sum(self.ResolvedTop_Stop0l) == 0:
            return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Getting jets ~~~~~
        ### Subjet method
        subjetides  = []
        for i, j in enumerate(fatj):
            if self.FatJet_Stop0l[i] > 0 :
                subjetides.append(j.subJetIdx1)
                subjetides.append(j.subJetIdx2)
        ## Resolved AK4 jets
        resjets = defaultdict(list)
        for i, t in enumerate(res):
            if self.ResolvedTop_Stop0l[i]:
                resjets[t.j1Idx].append(i)
                resjets[t.j2Idx].append(i)
                resjets[t.j3Idx].append(i)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Making correlation ~~~~~
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
        overlap = combs[np.where(dR2 < 0.04)]
        if overlap.size == 0:
            return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Killing overlap ~~~~~
        ## Has overlap
        for j in overlap[:, 1]:
            for overlapidx in resjets[j]:
                self.ResolvedTop_Stop0l[overlapidx] = False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Clean up double counting in DeepResolved ~~~~~
        for k, v in resjets.items():
            ## counting tops per jets
            if len(v) <= 1:
                continue
            ## Recount tops per jets
            newtops = [ n for n in v if self.ResolvedTop_Stop0l[n] ]
            if len(newtops) <= 1:
                continue
            ## Shit, duplicate tops, keep the highest discriminate
            topbyscore = {}
            for j in newtops:
                topbyscore [ res[j].discriminator ] = j

            for k in sorted(topbyscore.keys())[:-1]:
                self.ResolvedTop_Stop0l[topbyscore[k]] = False
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
           leadingjet.btagDeepB > DeepCSVMediumWP[self.era]:
            return -1

        if subjets[leadingjet.subJetIdx1]  > DeepCSVMediumWP[self.era] or \
           subjets[leadingjet.subJetIdx2]  > DeepCSVMediumWP[self.era]:
            return -1

        if math.fabs(ROOT.TVector2.Phi_mpi_pi( leadingjet.phi - met_phi )) < -2:
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

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        ## Getting objects
        jets     = Collection(event, "Jet")
        fatjets  = Collection(event, "FatJet")
        subjets  = Collection(event, "SubJet")
        resolves = Collection(event, "ResolvedTopCandidate")
        met       = Object(event, self.metBranchName)
        self.Clear()

        ## Selecting objects
        self.FatJet_Stop0l = map(self.SelDeepAK8, fatjets)
        self.ResolvedTop_Stop0l = map(lambda x : self.SelDeepResolved(x, jets), resolves)
        self.ResovleOverlapDeepAK8(resolves, fatjets, jets, subjets)
        self.nTop = sum( [ i for i in self.FatJet_Stop0l if i == 1 ])
        self.nW = sum( [ 1 for i in self.FatJet_Stop0l if i == 2 ])
        self.nResolved = sum(self.ResolvedTop_Stop0l)
        self.ISRJetidx = self.GetISRJets(fatjets, subjets, met.phi)
        ISRJetPt = fatjets[self.ISRJetidx].pt if self.ISRJetidx != -1 else 0
        (HOTpt, HOTeta, HOTphi, HOTmass, HOTtype) =  self.CreateHOTs(fatjets, resolves)

        ### Store output
        self.out.fillBranch("FatJet_Stop0l", self.FatJet_Stop0l)
        self.out.fillBranch("ResolvedTop_Stop0l", self.ResolvedTop_Stop0l)
        self.out.fillBranch("Stop0l_nTop", self.nTop)
        self.out.fillBranch("Stop0l_nW", self.nW)
        self.out.fillBranch("Stop0l_nResolved", self.nResolved)
        self.out.fillBranch("Stop0l_ISRJetIdx", self.ISRJetidx)
        self.out.fillBranch("Stop0l_ISRJetPt", ISRJetPt)
        self.out.fillBranch("Stop0l_nHOT", len(HOTpt))
        self.out.fillBranch("Stop0l_HOTpt", HOTpt)
        self.out.fillBranch("Stop0l_HOTeta", HOTeta)
        self.out.fillBranch("Stop0l_HOTphi", HOTphi)
        self.out.fillBranch("Stop0l_HOTmass", HOTmass)
        self.out.fillBranch("Stop0l_HOTtype", HOTtype)
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
