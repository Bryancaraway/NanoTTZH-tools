# NanoTTZ-tools
Postprocessing script for ttZ/H->bb  analysis

See the [readme](python/processors/Condor/README.md) in "NanoTTZHTools/python/processors/Condor" for specific instructions for condor submission.

### Set up CMSSW

```tcsh
source /cvmfs/cms.cern.ch/cmsset_default.csh
cmsrel CMSSW_10_6_19
cd CMSSW_10_6_19/src/
cmsenv
```

### Set up NanoTTZHTools framework
```tcsh
cd $CMSSW_BASE/src
cmsenv
git clone -b TTZH git@github.com:Bryancaraway/nanoAOD-tools.git PhysicsTools/NanoAODTools
# For condor submission check the specific tag checkout instructions in [readme](python/processors/Condor/README.md)
git clone -b TTZH git@github.com:Bryancaraway/NanoTTZH-tools.git PhysicsTools/NanoTTZHTools
scram b
cd $CMSSW_BASE/src/PhysicsTools/NanoTTZHTools/python/processors
```

### Run local MC test
```tcsh
python TTZH_postproc.py -i file:[input file] -s [MC sample name (from sampleSet cfg file)] -e [year]
```

### Run local Data test
```tcsh
python TTZH_postproc.py -i file:[input file] -d [data period] -e [year]
```


## To Do:
* propagate jec uncertainties to jet/fatjet selection (not super necessary)
