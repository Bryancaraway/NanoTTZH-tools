# Instructions for condor submission 

It is highly advisable to check out a clean CMSSW release and follow the setup readme from scratch for each new submission to reduce the possibility of unwanted local changes causing issues.  

The instructions here assume you have followed the main [README](../../../README.md).

Before jobs submission, get valid grid certificate:

```voms-proxy-init --voms cms```

### Condor submission command

The correct command for condor submission is:

```python SubmitLPC.py -c path/to/file.cfg -e [year] -o /store/user/foo/bar/ --site storagesit```

where the '-o' designates the output to mounted storage directory, either eos/uscms(lpc) or cms/data(kodiak)
Output log files from this command will be put in `~/nobackup/condor_temp`.  The output root files can be stored on lpc or transfered off-site with the `--site` option

Specific example for 2016 submission off-site

```python SubmitLPC.py -c TTZH_samples/sampleSets_PreProcessed_2016.cfg -e 2016 -o /store/user/bcaraway/NanoAODv7 --site kodiak ```

Currently, I have only been able to write to my personal area (and not ttxeft) off-site (todo for the future)
If writing to kodiak, make sure you choose your personal storage area

