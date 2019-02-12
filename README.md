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
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
git clone git@github.com:susy2015/NanoSUSY-tools.git PhysicsTools/NanoSUSYTools
scram b
```


## To Do:
* PDF uncertainty module
* lepton SF module follow [SUSY](https://twiki.cern.ch/twiki/bin/viewauth/CMS/SUSLeptonSF#Scale_Factors_for_SUSY_IDs)
* PU reweighting (need updates)
* btag SF update (instead of the btag weight stored during production)
* JEC uncertainty update
* DeepAK8/DeepResolved SF
