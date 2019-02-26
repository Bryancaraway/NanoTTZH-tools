# NanoSUSY-tools
Postprocessing script for Stop 0L analysis

### Set up CMSSW

```tcsh
source /cvmfs/cms.cern.ch/cmsset_default.csh
setenv SCRAM_ARCH slc6_amd64_gcc700
cmsrel CMSSW_10_2_6
cd CMSSW_10_2_6/src/
cmsenv
```

### Set up CMSSW
```tcsh
cd $CMSSW_BASE/src
cmsenv
git clone -b Stop0l git@github.com:susy2015/nanoAOD-tools.git PhysicsTools/NanoAODTools
git clone git@github.com:susy2015/NanoSUSY-tools.git PhysicsTools/NanoSUSYTools
scram b
```


## To Do:
* PDF uncertainty module 
    * weights stored in NanoAOD accordingly already, need code to extract the envelope
* lepton SF module follow [SUSY](https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSLeptonSF#Scale_Factors_for_SUSY_IDs)
    * Need to update based upon the existing example code from NanoAOD-tools
* PU reweighting 
    * Example code existed, but need recompute the pileup distribution from data
* btag SF update (instead of the btag weight stored during production)
    * Need follow up with which method to be apply (iterative fit for DeepCSV?)
* JEC uncertainty update
    * Need to understand the existing tool in NanoAOD-Tools
* DeepAK8/DeepResolved SF
    * Are they available yet?
* update Jet ID : [JetID Twiki](https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetID13TeVRun2018)
    * Do we need it in post-processing, or wait for next production?
* L1EcalPrefiring [twiki]* (https://twiki.cern.ch/twiki/bin/viewauth/CMS/L1ECALPrefiringWeightRecipe#Call_the_producer_in_your_config)
    * Rumor is it will be included in next NanoAOD
    * If not, we will make a module for it
* Various systematics 
* Trigger path and efficiency:
    * Once Hui's study is finalized, we will store the bit and efficiency + systematic
