import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class Stop0lBaselineProducer(Module):
    def __init__(self, era, isData = False, isFastSim=False):
        self.era = era
        self.isFastSim = isFastSim
        self.isData = isData

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Pass_JetID",         "O")
        self.out.branch("Pass_EventFilter",   "O")
        self.out.branch("Pass_LeptonVeto",    "O")
        self.out.branch("Pass_NJets20",       "O")
        self.out.branch("Pass_MET",           "O")
        self.out.branch("Pass_HT",            "O")
        self.out.branch("Pass_dPhiMET",       "O")
        self.out.branch("Pass_dPhiMETLowDM",  "O")
        self.out.branch("Pass_dPhiMETHighDM", "O")
        self.out.branch("Pass_Baseline",      "O")
        self.out.branch("Pass_highDM",      "O")
        self.out.branch("Pass_lowDM",      "O")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def PassLeptonVeto(self, eles, muons, isks):
        countEle = sum([e.Stop0l for e in eles])
        countMu  = sum([m.Stop0l for m in muons])
        countIsk = sum([i.Stop0l for i in isks])
        return (countEle + countMu + countIsk == 0)


    def PassEventFilter(self, flags):
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2#2016_data
        passEventFilter = None

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2016 ~~~~~
        if self.era == "2016":
            ## Common filters
            passEventFilter = flags.goodVertices and flags.HBHENoiseFilter and \
                    flags.HBHENoiseIsoFilter and flags.EcalDeadCellTriggerPrimitiveFilter \
                    and flags.BadPFMuonFilter and flags.BadChargedCandidateFilter # Post 2016 ICHEP
                    # and flags.BadPFMuonSummer16Filter and # flags.BadChargedCandidateSummer16Filter
            ## Only data
            if self.isData:
                passEventFilter = passEventFilter and flags.globalSuperTightHalo2016Filter and flags.eeBadScFilter
            elif not self.isFastSim:
                passEventFilter = passEventFilter and flags.globalSuperTightHalo2016Filter

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2017 ~~~~~
        if self.era == "2017" or self.era == "2018":
            ## Common filters
            passEventFilter = flags.goodVertices and flags.HBHENoiseFilter and \
                    flags.HBHENoiseIsoFilter and flags.EcalDeadCellTriggerPrimitiveFilter \
                    and flags.BadPFMuonFilter and flags.BadChargedCandidateFilter \
                    and flags.ecalBadCalibFilter  ## Need to double check whether is outdated
            ## Only data
            if self.isData:
                passEventFilter = passEventFilter and flags.globalSuperTightHalo2016Filter and flags.eeBadScFilter
            elif not self.isFastSim:
                passEventFilter = passEventFilter and flags.globalSuperTightHalo2016Filter

        return passEventFilter

    def PassJetID(self, jets):
        # In case of fastsim, it has been observed with lower efficiency
        # https://hypernews.cern.ch/HyperNews/CMS/get/jet-algorithms/379.html
        # The conclusion is to ignore it but cover with systematics.
        if self.isFastSim:
            return True

        # https://twiki.cern.ch/twiki/bin/view/CMS/JetID#Recommendations_for_13_TeV_2017
        # For 2016, loose and tight ID is the same : https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVRun2016
        # For 2017, only tight ID available: https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVRun2017
        # Select jet pt > 30GeV, which is used in jet ID study:
        # https://indico.cern.ch/event/592313/contributions/2398387/attachments/1384663/2106630/JetID_JMARmeeting_7_12_2016.pdf
        jetIDs = [j.jetId & 0b010 for j in jets if j.pt > 30]
        return (0 not in jetIDs)


    def PassNjets(self, jets):
        countJets = sum([j.Stop0l for j in jets])
        return countJets >= 2

    def PassdPhi(self, jets, dPhiCuts):
        passdPhi = True
        jetcount = 0
        for i, j in enumerate(jets):
            if math.fabs(j.eta) > 4.7 or j.pt < 20:
                continue
            if jetcount >= len(dPhiCuts):
                return passdPhi
            passdPhi = passdPhi and j.dPhiMET > dPhiCuts[jetcount]
            jetcount +=  1
        return passdPhi

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        electrons = Collection(event, "Electron")
        muons     = Collection(event, "Muon")
        isotracks = Collection(event, "IsoTrack")
        jets      = Collection(event, "Jet")
        met       = Object(event,     "MET")
        flags     = Object(event,     "Flag")
        stop0l    = Object(event,     "Stop0l")

        ## Baseline Selection
        PassJetID       = self.PassJetID(jets)
        PassEventFilter = self.PassEventFilter(flags) and PassJetID
        PassLeptonVeto  = self.PassLeptonVeto(electrons, muons, isotracks)
        PassNjets       = self.PassNjets(jets)
        PassMET         = met.pt >= 250
        PassHT          = stop0l.HT >= 300
        PassdPhiLowDM   = self.PassdPhi(jets, [0.5, 0.15, 0.15])
        PassdPhiHighDM  = self.PassdPhi(jets, [0.5, 0.5, 0.5, 0.5])
        PassBaseline    = PassEventFilter and PassLeptonVeto and PassNjets and PassMET and PassHT and PassdPhiLowDM
        PasshighDM      = PassBaseline and stop0l.nJets >= 5 and PassdPhiHighDM and stop0l.nbtags >= 1
        PasslowDM       = PassBaseline and stop0l.nTop == 0 and stop0l.nW == 0 and stop0l.nResolved == 0 and \
                stop0l.Mtb < 175 and stop0l.ISRJetPt > 200 and stop0l.METSig > 10


        ### Store output
        self.out.fillBranch("Pass_JetID",         PassJetID)
        self.out.fillBranch("Pass_EventFilter",   PassEventFilter)
        self.out.fillBranch("Pass_LeptonVeto",    PassLeptonVeto)
        self.out.fillBranch("Pass_NJets20",       PassNjets)
        self.out.fillBranch("Pass_MET",           PassMET)
        self.out.fillBranch("Pass_HT",            PassHT)
        self.out.fillBranch("Pass_dPhiMET",       PassdPhiLowDM)
        self.out.fillBranch("Pass_dPhiMETLowDM",  PassdPhiLowDM)
        self.out.fillBranch("Pass_dPhiMETHighDM", PassdPhiHighDM)
        self.out.fillBranch("Pass_Baseline",      PassBaseline)
        self.out.fillBranch("Pass_highDM",        PasshighDM)
        self.out.fillBranch("Pass_lowDM",         PasslowDM)

        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
# Stop0lBaseline = lambda : Stop0lBaselineProducer("2016", False)
