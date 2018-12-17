import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
from collections import defaultdict
from itertools import permutations
import numpy as np
import itertools

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class DeepTopProducer(Module):
    def __init__(self):
        ## WP from Hui's study https://indico.cern.ch/event/780000/contributions/3248659/attachments/1768782/2873013/Search_bin_study_with_combine_tools_v13.pdf
        self.DeepAK8TopWP  = 0.9377
        self.minAK8TopMass = 105
        self.minAK8WMass = 65
        self.DeepAK8WWP    = 0.9530
        self.DeepResolveWP = 0.92

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("FatJet_Stop0l",      "O", lenVar="nFatJet")
        self.out.branch("ResolvedTop_Stop0l", "O", lenVar="nResolvedTop")

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
        # deepak8 = [ j
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

    def GetISRJets(self, fatjets, jets, subjets):
        ISRcans = [j for i, j in enumerate(fatjets) if self.FatJet_Stop0l[i] and j.pt > 200 ]



    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        ## Getting objects
        jets     = Collection(event, "Jet")
        fatjets  = Collection(event, "FatJet")
        subjets  = Collection(event, "SubJet")
        resolves = Collection(event, "ResolvedTop")
        self.Clear()

        ## Selecting objects
        self.FatJet_Stop0l = map(self.SelDeepAK8, fatjets)
        self.ResolvedTop_Stop0l = map(lambda x : self.SelDeepResolved(x, jets), resolves)
        temp =  self.ResolvedTop_Stop0l
        self.ResovleOverlapDeepAK8(resolves, fatjets, jets, subjets)
        # if (temp != self.ResolvedTop_Stop0l) :
            # print (temp, self.ResolvedTop_Stop0l)

        ### Store output
        self.out.fillBranch("FatJet_Stop0l", self.FatJet_Stop0l)
        self.out.fillBranch("ResolvedTop_Stop0l", self.ResolvedTop_Stop0l)
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
