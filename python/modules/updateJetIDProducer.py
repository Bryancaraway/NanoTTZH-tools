import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module


# 2016 : https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetID13TeVRun2016
# 2017 : https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetID13TeVRun2017
# 2018 : https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVRun2018

class UpdateJetID(Module):
    def __init__(self, era):
        self.era = era

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Stop0l_evtWeight",         "F", title="Storing cross section/nEvent for MC, lumi for Data")
        self.out.branch("Jet_jetId",      "I", lenVar="nJet", title="Updated tight Jet ID for 2018")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def PassTightJetID_2018(self, jet):
        # From  https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVRun2018
        eta                = jet.eta
        NHF                = jet.neHEF                           # pfjet->neutralHadronEnergyFraction();
        NEMF               = jet.neEmEF                          # pfjet->neutralEmEnergyFraction();
        CHF                = jet.chHEF                           # pfjet->chargedHadronEnergyFraction();
        MUF                = jet.muEF                            # pfjet->muonEnergyFraction();
        CEMF               = jet.chEmEF                          # pfjet->chargedEmEnergyFraction();
        CHM                = jet.chHadMult+jet.elMult+jet.muMult # pfjet->chargedMultiplicity();
        NumConst           = jet.nConstituents                   # pfjet->chargedMultiplicity()+pfjet->neutralMultiplicity();
        NumNeutralParticle = NumConst - CHM                      # pfjet->neutralMultiplicity();

        tightJetID = False
        # For |eta|<=2.6 Apply
        tightJetID |= (abs(eta)<=2.6 and CEMF<0.8 and CHM>0 and CHF>0 and NumConst>1 and NEMF<0.9 and MUF <0.8 and NHF < 0.9 )

        #For 2.6<|eta|<=2.7 Apply
        tightJetID |= ( abs(eta)>2.6 and abs(eta)<=2.7 and CEMF<0.8 and CHM>0 and NEMF<0.99 and MUF <0.8 and NHF < 0.9 )

        #For 2.7<|eta|<= 3.0 Apply
        tightJetID |= ( NEMF>0.02 and NEMF<0.99 and NumNeutralParticle>2 and abs(eta)>2.7 and abs(eta)<=3.0)

        #For |eta|> 3.0 Apply
        tightJetID |= (NEMF<0.90 and NHF>0.2 and NumNeutralParticle>10 and abs(eta)>3.0 )

        if tightJetID:
            return 0b010
        else:
            return 0b000


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        jets      = Collection(event, "Jet")
        newJetID      = map(self.PassTightJetID_2018, jets)

        ### Store output
        self.out.fillBranch("Jet_jetId",        newJetID)
        return True
