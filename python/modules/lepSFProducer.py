import ROOT
import os
import numpy as np
import math
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from TauPOG.TauIDSFs.TauIDSFTool import TauIDSFTool

class lepSFProducer(Module):
    """ This module is copied from the NanoAOD-tools,
    but developed for lastest SUSY Lepton ID
    """
    def __init__(self, era, muonSelectionTag="Loose", electronSelectionTag="Veto", 
                 photonSelectionTag="Loose", tauSelectionTag="Medium"):
        self.era = era
        self.muonSelectionTag     = muonSelectionTag
        self.electronSelectionTag = electronSelectionTag
        self.photonSelectionTag   = photonSelectionTag
        self.tauSelectionTag      = tauSelectionTag

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Muon ~~~~~
        # Only looseID miniIso SF existed for 2016
        mu_f =[]
        mu_h =[]
        if self.era == "2016":
            mu_f+= [ "Muon_IDScaleFactor_%sGH.root" % self.era, 
                     "Muon_LooseID_MiniIso0p2SF_2016.root"
                   ]
            mu_h += ["NUM_%sID_DEN_genTracks_eta_pt" % self.muonSelectionTag, 
                     "SF"
                    ]
        if self.era == "2017":
            mu_f+= [ "Muon_IDScaleFactor_%s.root" % self.era, 
                    "Muon_%sID_MiniIso0p2SF_%s.root" % (self.muonSelectionTag, self.era)
                   ]
            mu_h += ["NUM_%sID_DEN_genTracks_pt_abseta" % self.muonSelectionTag, 
                     "TnP_MC_NUM_MiniIso02Cut_DEN_%sID_PAR_pt_eta" % self.muonSelectionTag
                    ]
        elif self.era == "2018":
            ##  SUSY recommend to use the 2017 Data/FullSim SFs for MiniIso also
            ##  for 2018, as no changes are expected and these SFs are very close to 1. 
            mu_f+= [ "Muon_IDScaleFactor_%s.root" % self.era, 
                    "Muon_%sID_MiniIso0p2SF_%s.root" % (self.muonSelectionTag, "2017")
                   ]
            mu_h += ["NUM_%sID_DEN_TrackerMuons_pt_abseta" % self.muonSelectionTag, 
                     "TnP_MC_NUM_MiniIso02Cut_DEN_%sID_PAR_pt_eta" % self.muonSelectionTag
                    ]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Electron ~~~~~
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

        # The production used 2016v2 ID for 2016 photon
        if self.era == "2016":
            pho_f =["Photon_%s_80XCutbased_%s.root"% (self.photonSelectionTag, self.era)]
            pho_h = ["EGamma_SF2D"]
        else:
            pho_f = ["Photon_%s_2017v2Cutbased_%s.root" % (self.photonSelectionTag, self.era)]
            pho_h = ["EGamma_SF2D"]

        # In addition to ID scale factors, analysis using it should 
        # apply the electron veto scale factors


        if self.era == "2016":
            eleveto_f =[ "ElectronVeto_ScaleFactors_80X_2016.root" ]
            eleveto_h = ["Scaling_Factors_HasPix_R9 Inclusive"]
        else:
            eleveto_f =[ "ElectronVeto_PixelSeed_ScaleFactors_2017.root" ]
            eleveto_h = ["%s_ID" % self.photonSelectionTag]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Tau ~~~~~
        self.tauSFTool = TauIDSFTool(int(self.era),'MVAoldDM2017v2',self.tauSelectionTag)


        mu_f = ["%s/src/PhysicsTools/NanoSUSYTools/data/leptonSF/" % os.environ['CMSSW_BASE'] + f for f in mu_f]
        el_f = ["%s/src/PhysicsTools/NanoSUSYTools/data/leptonSF/" % os.environ['CMSSW_BASE'] + f for f in el_f]
        pho_f = ["%s/src/PhysicsTools/NanoSUSYTools/data/leptonSF/" % os.environ['CMSSW_BASE'] + f for f in pho_f]
        eleveto_f = ["%s/src/PhysicsTools/NanoSUSYTools/data/leptonSF/" % os.environ['CMSSW_BASE'] + f for f in eleveto_f]

        self.mu_f = ROOT.std.vector(str)(len(mu_f))
        self.mu_h = ROOT.std.vector(str)(len(mu_f))
        for i in range(len(mu_f)): self.mu_f[i] = mu_f[i]; self.mu_h[i] = mu_h[i];
        self.el_f = ROOT.std.vector(str)(len(el_f))
        self.el_h = ROOT.std.vector(str)(len(el_f))
        for i in range(len(el_f)): self.el_f[i] = el_f[i]; self.el_h[i] = el_h[i];
        self.pho_f = ROOT.std.vector(str)(len(pho_f))
        self.pho_h = ROOT.std.vector(str)(len(pho_f))
        for i in range(len(pho_f)): self.pho_f[i] = pho_f[i]; self.pho_h[i] = pho_h[i];
        self.eleveto_f = ROOT.std.vector(str)(len(eleveto_f))
        self.eleveto_h = ROOT.std.vector(str)(len(eleveto_f))
        for i in range(len(eleveto_f)): self.eleveto_f[i] = eleveto_f[i]; self.eleveto_h[i] = eleveto_h[i];

        for library in [ "libCondFormatsJetMETObjects", "libPhysicsToolsNanoAODTools" ]:
            if library not in ROOT.gSystem.GetLibraries():
                print("Load Library '%s'" % library)
                ROOT.gSystem.Load(library)

    

    def beginJob(self):
        self._worker_mu = ROOT.LeptonEfficiencyCorrector(self.mu_f,self.mu_h)
        self._worker_el = ROOT.LeptonEfficiencyCorrector(self.el_f,self.el_h)
        self._worker_pho = ROOT.LeptonEfficiencyCorrector(self.pho_f,self.pho_h)
        self._worker_eleveto = ROOT.LeptonEfficiencyCorrector(self.eleveto_f,self.eleveto_h)
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
        self.out.branch("Tau_%sSF" % self.tauSelectionTag    , "F" , \
                        lenVar="nTau", title="ID scale factor per Tau")
        self.out.branch("Tau_%sSF_Up" % self.tauSelectionTag    , "F" , \
                        lenVar="nTau", title="ID scale factor up error per Tau")
        self.out.branch("Tau_%sSF_Down" % self.tauSelectionTag    , "F" , \
                        lenVar="nTau", title="ID scale factor down error per Tau")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        muons     = Collection(event, "Muon")
        electrons = Collection(event, "Electron")
        photons   = Collection(event, "Photon")
        taus      = Collection(event, "Tau")
        gens      = Collection(event, "GenPart")

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

        sferr_el = [a/b for a, b in zip(sferr_el, sf_el)] 
        sferr_mu = [a/b for a, b in zip(sferr_mu, sf_mu)] 

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Photon ~~~~~
        sf_eleveto = []
        sferr_eleveto= []
        if self.era == "2016":
            sf_eleveto = [ self._worker_eleveto.getSF(pho.pdgId,pho.pt,abs(pho.eta)) for pho in photons ]
            sferr_eleveto = [ self._worker_eleveto.getSFErr(pho.pdgId,pho.pt,abs(pho.eta)) for pho in photons ]
        else:
            for pho in photons:
                binx = 1 if pho.r9 > 0.94 else 2
                binx = binx + 3 if pho.isScEtaEE else binx 
                sf_eleveto.append(self._worker_eleveto.getSF(pho.pdgId, 0, binx ))
                sferr_eleveto.append(self._worker_eleveto.getSFErr(pho.pdgId, 0, binx ))
        ssf_pho = [a*b for a, b in zip(sf_pho, sf_eleveto)] 
        ssferr_pho = [ math.sqrt(((serrp/sp)** 2 + (serre/se)**2))/ ssf if ssf !=0 else 0 for sp, se, serrp, serre, ssf in zip(sf_pho, sf_eleveto, sferr_pho, sferr_eleveto, ssf_pho) ] 


        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Tau ~~~~~
        sf_tau = []
        sf_tau_up = []
        sf_tau_down = []
        for tau in taus:
            genmatch = -1
            ## genPartFlave: 1 = prompt electron, 2 = prompt muon, 3 = tau->e decay, 
            ## 4 = tau->mu decay, 5 = hadronic tau decay, 0 = unknown or unmatched
            if tau.genPartFlav >= 3 :
                genmatch = 5
            sf_tau.append(self.tauSFTool.getSFvsPT(tau.pt, genmatch))
            sf_tau_up.append(self.tauSFTool.getSFvsPT(tau.pt, genmatch, unc="Up"))
            sf_tau_down.append(self.tauSFTool.getSFvsPT(tau.pt, genmatch, unc="Down"))

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Photon Electron Veto SF ~~~~~


        self.out.fillBranch("Muon_%sSF" % self.muonSelectionTag            , sf_mu)
        self.out.fillBranch("Muon_%sSFErr" % self.muonSelectionTag         , sferr_mu)
        self.out.fillBranch("Electron_%sSF" % self.electronSelectionTag    , sf_el)
        self.out.fillBranch("Electron_%sSFErr" % self.electronSelectionTag , sferr_el)
        self.out.fillBranch("Photon_%sSF" % self.photonSelectionTag        , ssf_pho)
        self.out.fillBranch("Photon_%sSFErr" % self.photonSelectionTag     , ssferr_pho)
        self.out.fillBranch("Tau_%sSF" % self.tauSelectionTag              , sf_tau)
        self.out.fillBranch("Tau_%sSF_Up" % self.tauSelectionTag           , sf_tau_up)
        self.out.fillBranch("Tau_%sSF_Down" % self.tauSelectionTag         , sf_tau_down)
        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
# lepSF = lambda : lepSFProducer( "LooseWP_2016", "GPMVA90_2016")

