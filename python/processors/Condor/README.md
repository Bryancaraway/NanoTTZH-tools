# Instructions for condor submission 

It is highly advisable to check out a clean CMSSW release and follow the setup readme from scratch for each new submission to reduce the possibility of unwanted local changes causing issues.  

The instructions here assume you have followed the main [README](../../../README.md).

### Condor submission command

The correct command for condor submission is

```python SubmitLPC.py -c path/to/file.cfg -e [year] ```

Specific example for 2016 submission 

```python SubmitLPC.py -c sampleCfg/sampleSets_2016.cfg -e 2016 ```

Output log files from this command will be put in `~/nobackup/condor_temp`.  The output root files can be stored on lpc or transfered off-site with the `--site` option

