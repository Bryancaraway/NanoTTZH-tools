# Instructions for condor submission 

The instructions here are up to date for postprocessing v3.0.  If you are submittion for a different fine the approperiate NanoSUSY-tools tag for the desired post processing version.  

It is highly advisable to check out a clean CMSSW release and follow the setup readme from scratch for each new submission to reduce the possibility of unwanted local changes causing issues.  

The instructions here assume you have followed the main [README](../../../README.md).

### NanoSUSY-tools tag for submission

Use the following tag for postprocessing submissions 

```
cd $CMSSW_BASE/src/PhysicsTools/NanoSUSYTools/
git checkout postpro_v3.0
scram b -j8
```
### StopCfg tag for submission

For submission of postprocessing use the following pre-processing files from the stopCfg tag [PreProcessed_StopNtuple_V3](https://github.com/susy2015/StopCfg/releases/tag/PreProcessed_StopNtuple_V3).  The tag can checked out with the following command

```git clone -b PreProcessed_StopNtuple_V3 git@github.com:susy2015/StopCfg.git```

### Condor submission command

The correct command for condor submission is

```python SubmitLPC.py -c path/to/file.cfg -e [year] ```

Specific example for 2016 submission 

```python SubmitLPC.py -c StopCfg/sampleSets_PreProcessed_2016.cfg -e 2016 ```

Output log files from this command will be put in `~/nobackup/condor_temp`.  The output root files will be put in the aproperiate directories in `/store/user/lpcsusyhad/Stop_production` automatically.

### Checking for errors after all jobs are complete

Be sure to check for any failed jobs after they are complete by looking through the log files with the following command

``` ```