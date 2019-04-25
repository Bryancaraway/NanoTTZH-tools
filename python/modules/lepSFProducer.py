import ROOT
import os
import numpy as np
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class lepSFProducer(Module):
    """ This module is copied from the NanoAOD-tools,
    but developed for lastest SUSY Lepton ID
    """
    def __init__(self, era, muonSelectionTag="Loose", electronSelectionTag="Veto", photonSelectionTag="Loose"):
        self.era = era
        self.muonSelectionTag = muonSelectionTag
        self.electronSelectionTag = electronSelectionTag
        self.photonSelectionTag = photonSelectionTag

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Muon ~~~~~
        # TODO: Muon POG provides 2016 SF in different format!
        # TODO: Add MiniIso0.2 for 2016 and 2018
        mu_f =[]
        mu_h =[]
        if self.era == "2016":
            mu_f+= [ "Muon_IDScaleFactor_%sGH.root" % self.era, 
                   ]
            mu_h += ["NUM_%sID_DEN_genTracks_eta_pt" % self.muonSelectionTag, 
                    ]
        if self.era == "2017":
            mu_f+= [ "Muon_IDScaleFactor_%s.root" % self.era, 
                    "Muon_%sID_MiniIso0p2SF_%s.root" % (self.muonSelectionTag, self.era)
                   ]
            mu_h += ["NUM_%sID_DEN_genTracks_pt_abseta" % self.muonSelectionTag, 
                     "TnP_MC_NUM_MiniIso02Cut_DEN_%sID_PAR_pt_eta" % self.muonSelectionTag
                    ]
        elif self.era == "2018":
            mu_f+= [ "Muon_IDScaleFactor_%s.root" % self.era
                   ]
            mu_h += ["NUM_%sID_DEN_TrackerMuons_pt_abseta" % self.muonSelectionTag, 
                    ]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Electron ~~~~~
        ## TODO: Missing the MiniISO SF
        if self.era == "2018":
            el_f = [ "Electron_GT10GeV_RecoSF_2017v2ID_Run%s.root" % self.era,
                "Electron_SUSYScaleFactors_2017v2ID_Run%s.root" % self.era
            ]
            el_h = ["EGamma_SF2D",
                    "Run%s_CutBased%sNoIso94XV2" % (self.era, self.electronSelectionTag)
                    ]
        else:
            el_f = [ "Electron_GT20GeV_RecoSF_2017v2ID_Run%s.root" % self.era,
                "Electron_LT20GeV_RecoSF_2017v2ID_Run%s.root" % self.era,
                "Electron_SUSYScaleFactors_2017v2ID_Run%s.root" % self.era
            ]
            el_h = ["EGamma_SF2D",
                    "EGamma_SF2D",
                    "Run%s_CutBased%sNoIso94XV2" % (self.era, self.electronSelectionTag)
                    ]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Photon ~~~~~
        # TODO: Missing the Electron Veto SF
        pho_f = ["Photon_%s_2017v2Cutbased_%s.root" % (self.photonSelectionTag, self.era)]
        pho_h = ["EGamma_SF2D"]

        mu_f = ["%s/src/PhysicsTools/NanoSUSYTools/data/leptonSF/" % os.environ['CMSSW_BASE'] + f for f in mu_f]
        el_f = ["%s/src/PhysicsTools/NanoSUSYTools/data/leptonSF/" % os.environ['CMSSW_BASE'] + f for f in el_f]
        pho_f = ["%s/src/PhysicsTools/NanoSUSYTools/data/leptonSF/" % os.environ['CMSSW_BASE'] + f for f in pho_f]

        self.mu_f = ROOT.std.vector(str)(len(mu_f))
        self.mu_h = ROOT.std.vector(str)(len(mu_f))
        for i in range(len(mu_f)): self.mu_f[i] = mu_f[i]; self.mu_h[i] = mu_h[i];
        self.el_f = ROOT.std.vector(str)(len(el_f))
        self.el_h = ROOT.std.vector(str)(len(el_f))
        for i in range(len(el_f)): self.el_f[i] = el_f[i]; self.el_h[i] = el_h[i];
        self.pho_f = ROOT.std.vector(str)(len(pho_f))
        self.pho_h = ROOT.std.vector(str)(len(pho_f))
        for i in range(len(pho_f)): self.pho_f[i] = pho_f[i]; self.pho_h[i] = pho_h[i];

        for library in [ "libCondFormatsJetMETObjects", "libPhysicsToolsNanoAODTools" ]:
            if library not in ROOT.gSystem.GetLibraries():
                print("Load Library '%s'" % library)
                ROOT.gSystem.Load(library)


    def beginJob(self):
        self._worker_mu = ROOT.LeptonEfficiencyCorrector(self.mu_f,self.mu_h)
        self._worker_el = ROOT.LeptonEfficiencyCorrector(self.el_f,self.el_h)
        self._worker_pho = ROOT.LeptonEfficiencyCorrector(self.pho_f,self.pho_h)
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Muon_%sSF" % self.muonSelectionTag            , "F" , \
                        lenVar="nMuon", title="Muon scale factor per Muon")
        self.out.branch("Muon_%sSFErr" % self.muonSelectionTag         , "F" , \
                        lenVar="nMuon", title="Muon scale factor error per Muon")
        self.out.branch("Electron_%sSF" % self.electronSelectionTag    , "F" , \
                        lenVar="nElectron", title="Reco+ID scale factor error per Electron")
        self.out.branch("Electron_%sSFErr" % self.electronSelectionTag , "F" , \
                        lenVar="nElectron", title="Reco+ID scale factor per Electron")
        self.out.branch("Photon_%sSF" % self.photonSelectionTag    , "F" , \
                        lenVar="nPhoton", title="ID scale factor per Photon")
        self.out.branch("Photon_%sSFErr" % self.photonSelectionTag , "F" , \
                        lenVar="nPhoton", title="ID scale factor error  per Photon")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        muons = Collection(event, "Muon")
        electrons = Collection(event, "Electron")
        photons   = Collection(event, "Photon")
        sf_el = [ self._worker_el.getSF(el.pdgId,el.pt,el.eta) for el in electrons ]
        if self.era == "2016":
            sf_mu = [ self._worker_mu.getSF(12,mu.pt,mu.eta) for mu in muons ]
        else:
            sf_mu = [ self._worker_mu.getSF(mu.pdgId,mu.pt,mu.eta) for mu in muons ]
        sf_pho = [ self._worker_pho.getSF(pho.pdgId,pho.pt,pho.eta) for pho in photons ]

        sferr_el = [ self._worker_el.getSFErr(el.pdgId,el.pt,el.eta) for el in electrons ]
        if self.era == "2016":
            sferr_mu = [ self._worker_mu.getSFErr(12,mu.pt,mu.eta) for mu in muons ]
        else:
            sferr_mu = [ self._worker_mu.getSFErr(mu.pdgId,mu.pt,mu.eta) for mu in muons ]
        sferr_pho = [ self._worker_pho.getSFErr(pho.pdgId,pho.pt,pho.eta) for pho in photons ]
        self.out.fillBranch("Muon_%sSF" % self.muonSelectionTag            , sf_mu)
        self.out.fillBranch("Muon_%sSFErr" % self.muonSelectionTag         , sferr_mu)
        self.out.fillBranch("Electron_%sSF" % self.electronSelectionTag    , sf_el)
        self.out.fillBranch("Electron_%sSFErr" % self.electronSelectionTag , sferr_el)
        self.out.fillBranch("Photon_%sSF" % self.photonSelectionTag    , sf_pho)
        self.out.fillBranch("Photon_%sSFErr" % self.photonSelectionTag , sferr_pho)
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
# lepSF = lambda : lepSFProducer( "LooseWP_2016", "GPMVA90_2016")

