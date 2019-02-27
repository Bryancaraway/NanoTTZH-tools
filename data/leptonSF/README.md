This folder contains variarous lepton scale factor file for different era. 

## Sources
SUSY Lepton SF: https://twiki.cern.ch/twiki/bin/view/CMS/SUSLeptonSF
EGamma SF: https://twiki.cern.ch/twiki/bin/view/CMS/EgammaIDRecipesRun2#Efficiencies_and_scale_factors


### Electron

Only Fall2017V2 ID is used here.

#### 2018 

Data: Run2018A -17Sep2018-v2, Run2018B -17Sep2018-v1, Run2018C -17Sep2018-v1, Run2018D -PromptReco-v1, Run2018D -PromptReco-v2
MC: RunIIAutumn18MiniAOD 

 | Type                                           | URL                                                                                   | Rename file name                                | 
 | ---                                            | ----                                                                                  | ---                                             | 
 | Electron Reconstruction Efficiencies pT>20 Gev | https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/egammaEffi.txt_EGM2D.root     | Electron_GT20GeV_RecoSF_2017v2ID_Run2018.root   | 
 | Electron Reconstruction Efficiencies pT<20 Gev | https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/egammaEffi.txt_EGM2D_low.root | Electron_LT20GeV_RecoSF_2017v2ID_Run2018.root   | 
 | Data / MC SF                                   | https://twiki.cern.ch/twiki/pub/CMS/SUSLeptonSF/ElectronScaleFactors_Run2018.root     | Electron_SUSYScaleFactors_2017v2ID_Run2018.root |

#### 2017

Data: 31Mar2018-v1
MC: RunIIFall17MiniAODv2 

 | Type                                           | URL                                                                                   | Rename file name                                | 
 | ---                                            | ----                                                                                  | ---                                             | 
 | Electron Reconstruction Efficiencies pT>20 Gev | https://twiki.cern.ch/twiki/pub/CMS/Egamma2017DataRecommendations/egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root |  Electron_GT20GeV_RecoSF_2017v2ID_Run2017.root   | 
 | Electron Reconstruction Efficiencies pT<20 Gev | https://twiki.cern.ch/twiki/pub/CMS/Egamma2017DataRecommendations/egammaEffi.txt_EGM2D_runBCDEF_passingRECO_lowEt.root | Electron_LT20GeV_RecoSF_2017v2ID_Run2017.root   | 
 | Data / MC SF                                   | https://twiki.cern.ch/twiki/pub/CMS/SUSLeptonSF/ElectronScaleFactors_Run2017.root | Electron_SUSYScaleFactors_2017v2ID_Run2017.root |

#### 2016

Data: Run2016*-17Jul2018*v1
MC: RunIISummer16MiniAODv3 

  | Type                                           | URL                                                                                               | Rename file name                                | 
  | ---                                            | ----                                                                                              | ---                                             | 
  | Electron Reconstruction Efficiencies pT>20 Gev | https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root | Electron_GT20GeV_RecoSF_2017v2ID_Run2016.root   | 
  | Electron Reconstruction Efficiencies pT<20 Gev | https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/EGM2D_BtoH_low_RecoSF_Legacy2016.root     | Electron_LT20GeV_RecoSF_2017v2ID_Run2016.root   | 
  | Data / MC SF                                   | https://twiki.cern.ch/twiki/pub/CMS/SUSLeptonSF/ElectronScaleFactors_Run2016.root                 | Electron_SUSYScaleFactors_2017v2ID_Run2016.root | 
 
### Muons

  No clear yet

### Photon

Source : https://twiki.cern.ch/twiki/bin/view/CMS/EgammaIDRecipesRun2#Photon_efficiencies_and_scale_fa
Recommendation : In addition to ID scale factors, analysis using it should apply the electron veto scale factors.

Electron Veto only available for  Moriond 2017 for now : https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/ScalingFactors_80X_Summer16.root

   | Era  | URL                                                                                      | Rename                          | 
   | ---  | ----                                                                                     | ---                             | 
   | 2018 | https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/2018_PhotonsLoose.root           | Photon_Loose_Cutbased_2018.root | 
   | 2017 | https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/2017_PhotonsLoose.root           | Photon_Loose_Cutbased_2017.root | 
   | 2016 | https://twiki.cern.ch/twiki/pub/CMS/EgammaIDRecipesRun2/Fall17V2_2016_Loose_photons.root | Photon_Loose_Cutbased_2016.root | 


