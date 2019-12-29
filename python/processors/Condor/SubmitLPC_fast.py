#!/usr/bin/env python
# coding: utf-8

from __future__ import division
import os
import re
import time
import subprocess
import glob
import tarfile
import shutil
import getpass
import math
import argparse
import uproot
from collections import defaultdict
from multiprocessing import Pool
from itertools import izip_longest

# DelExe    = '../Stop0l_splitHEM.py'
DelExe    = '../Stop0l_fastsim.py'
tempdir = "/uscmst1b_scratch/lpc1/3DayLifetime/ahenckel/TestCondor/"
ShortProjectName = 'PreProcess17'
# VersionNumber = '_splitHEM'
VersionNumber = '_fastsimv4'
argument = "--inputFiles=%s.$(Process).list "
sendfiles = ["/uscms/home/benwu/python-packages.tgz", "../keep_and_drop.txt"]
TTreeName = "Events"
NProcess = 10

def tar_cmssw():
    print("Tarring up CMSSW, ignoring file larger than 100MB")
    cmsswdir = os.environ['CMSSW_BASE']
    cmsswtar = os.path.abspath('%s/CMSSW.tar.gz' % tempdir)
    if os.path.exists(cmsswtar):
        ans = raw_input('CMSSW tarball %s already exists, remove? [yn] ' % cmsswtar)
        if ans.lower()[0] == 'y':
            os.remove(cmsswtar)
        else:
            return

    def exclude(tarinfo):
        if tarinfo.size > 100*1024*1024:
            tarinfo = None
            return tarinfo
        exclude_patterns = ['/.git/', '/tmp/', '/jobs.*/', '/logs/', '/.SCRAM/', '.pyc']
        for pattern in exclude_patterns:
            if re.search(pattern, tarinfo.name):
                # print('ignoring %s in the tarball', tarinfo.name)
                tarinfo = None
                break
        return tarinfo

    with tarfile.open(cmsswtar, "w:gz",dereference=True) as tar:
        tar.add(cmsswdir, arcname=os.path.basename(cmsswdir), filter=exclude)
    return cmsswtar

def ConfigList(config):
    #Allow for grabbing the era from the config file name instead. Only does so if era argument is not given.
    if args.era == 0:
      if "2016" in config:
        temp_era = 2016
      elif "2017" in config:
        temp_era = 2017
      elif "2018" in config:
        temp_era = 2018
      else:
        raise Exception('No era given and none found in config file name. Please specify an era.')
    else:
        temp_era = args.era

    process = defaultdict(dict)
    #TODO: Split between sample set and sample collection configs
    lines = open(config).readlines()
    for line_ in lines:
        line = line_.strip()
        if(len(line) <= 0 or line[0] == '#'):
            continue
        entry = line.split(",")
        stripped_entry = [ i.strip() for i in entry]
        #print(stripped_entry)
        replaced_outdir = stripped_entry[1].replace("Pre","Post")
        process[stripped_entry[0]] = {
            #Note that anything appended with __ will not be passed along. These are for bookkeeping. Furthermore, Outpath is not used if an output directory argument is given.
            "Filepath__" : "%s/%s" % (stripped_entry[1], stripped_entry[2]),
            #"Outpath__" : "%s" % (replaced_outdir) + VersionNumber + "/" + stripped_entry[0] + "/",
            "Outpath__" : "%s" % (stripped_entry[1]) + VersionNumber + "/" + stripped_entry[0] + "/", #since these are preprocessed
            "isData__" : "Data" in stripped_entry[0],
            "isFastSim" : "fastsim" in stripped_entry[0], #isFastSim is a toggle in Stop0l_postproc.py, so it should be sent with no value.
            "era" : temp_era,
        }
        if process[stripped_entry[0]]["isData__"]:
            process[stripped_entry[0]].update( {
                "dataEra": stripped_entry[0][-1], #Example naming convention: Data_MET_2018_PeriodC. Alternate option: match "Period", take location + 6.
                "crossSection":  float(stripped_entry[4]) , #storing lumi for data
                "nEvents":  int(stripped_entry[5]),
            })
        else:
            process[stripped_entry[0]].update( {
                "crossSection":  float(stripped_entry[4]) * float(stripped_entry[7]),
                "nEvents":  int(stripped_entry[5]) - int(stripped_entry[6]), # using all event weight
                "sampleName": stripped_entry[0], #process
                "totEvents__":  int(stripped_entry[5]) + int(stripped_entry[6]), # using all event weight
            })

    return process

def Condor_Sub(condor_file):
    curdir = os.path.abspath(os.path.curdir)
    os.chdir(os.path.dirname(condor_file))
    print "To submit condor with " + condor_file
    os.system("condor_submit " + condor_file)
    os.chdir(curdir)

def GetNEvent(file):
    return (file, uproot.numentries(file, TTreeName))

def SplitPro(key, file, lineperfile=20, eventsplit=2**18, TreeName=None):
    # Default to 20 file per job, or 2**20 ~ 1M event per job
    # At 26Hz processing time in postv2, 1M event runs ~11 hours
    splitedfiles = []
    filelistdir = tempdir + '/' + "FileList"
    try:
        os.makedirs(filelistdir)
    except OSError:
        pass

    if "/store/" in file:
        subprocess.call("xrdcp root://cmseos.fnal.gov/%s %s/%s_all.list" % (file, filelistdir, key), shell=True)
        filename = os.path.abspath( "%s/%s_all.list" % (filelistdir, key))
    else:
        filename = os.path.abspath(file)

    filecnt = 0
    eventcnt  = 0
    filemap = defaultdict(list)
    if TreeName is None:
        print("Need Tree name to get number of entries")
        return splitedfiles, 0

    f = open(filename, 'r')
    filelist = [l.strip() for l in f.readlines()]
    splitbyNevent = False
    if splitbyNevent:
        r = None
        pool = Pool(processes=NProcess)
        r = pool.map(GetNEvent, filelist)
        pool.close()
        filedict = dict(r)
        for l in filelist:
            n = filedict[l]
            eventcnt += n
            if eventcnt > eventsplit:
                filecnt += 1
                eventcnt = n
            filemap[filecnt].append(l)
    else:
        g = izip_longest(fillvalue=None, *([iter(filelist)]*lineperfile))
        filemap = {i:gg for i, gg in enumerate(g)}
        filecnt = filemap.keys()[-1]

    for k,v in filemap.items():
        outf = open("%s/%s.%d.list" % (filelistdir, key, k), 'w')
        outf.write("\n".join(v))
        splitedfiles.append(os.path.abspath("%s/%s.%d.list" % (filelistdir, key, k)))
        outf.close()

    return splitedfiles, filecnt+1

def my_process(args):
    ## temp dir for submit
    global tempdir
    global ProjectName
    ProjectName = time.strftime('%b%d') + ShortProjectName + VersionNumber
    if args.era == 0:
        tempdir = tempdir + os.getlogin() + "/" + ProjectName +  "/"
    else:
        tempdir = tempdir + os.getlogin() + "/" + ProjectName + "_" + str(args.era) + "/"
    try:
        os.makedirs(tempdir)
    except OSError:
        pass

    ### Create Tarball
    Tarfiles = []
    NewNpro = {}

    ##Read config file
    Process = ConfigList(os.path.abspath(args.config))
    #Process = ConfigList(os.path.abspath(args.config), args.era)
    for key, sample in Process.items():
        print("Getting process: " + key + " " + sample['Filepath__'])
        npro, nque = SplitPro(key, sample['Filepath__'], TreeName=TTreeName)
        Tarfiles+= npro
        NewNpro[key] = nque

    Tarfiles.append(os.path.abspath(DelExe))
    tarballname ="%s/%s.tar.gz" % (tempdir, ProjectName)
    with tarfile.open(tarballname, "w:gz", dereference=True) as tar:
        [tar.add(f, arcname=f.split('/')[-1]) for f in Tarfiles]
        tar.close()
    tarballname += " , %s, " % tar_cmssw()
    tarballname += " , ".join([os.path.abspath(i) for i in sendfiles])

    ### Update condor and RunExe files
    for name, sample in Process.items():

        #define output directory
        if args.outputdir == "": outdir = sample["Outpath__"]
        else: outdir = args.outputdir + "/" + name + "/"

        #Update RunExe.csh
        RunHTFile = tempdir + "/" + name + "_RunExe.csh"
        with open(RunHTFile, "wt") as outfile:
            # for line in open("RunExe_splitHEM.csh","r"):
            for line in open("RunExe_fastsim.csh","r"):
                line = line.replace("DELSCR", os.environ['SCRAM_ARCH'])
                line = line.replace("DELDIR", os.environ['CMSSW_VERSION'])
                line = line.replace("DELEXE", DelExe.split('/')[-1])
                line = line.replace("OUTDIR", outdir)
                outfile.write(line)

        #Update condor file
        #First argument is output file name. Rest are to be passed to Stop0l_postproc.py.
        arg = "\nArguments = _$(Process).root --inputfile={common_name}.$(Process).list ".format(common_name=name)
        for k, v in sample.items():
            if "__" in k:
                continue
            if k == "isFastSim":
                if v is True:
                    arg+=" --%s" % k
            else:
                arg+=" --%s=%s" % (k, v)
        arg += "\nQueue {number} \n".format(number = NewNpro[name])

        ## Prepare the condor file
        condorfile = tempdir + "/" + "condor_" + ProjectName + "_" + name
        with open(condorfile, "wt") as outfile:
            for line in open("condor_fastsim", "r"):
                line = line.replace("EXECUTABLE", os.path.abspath(RunHTFile))
                line = line.replace("TARFILES", tarballname)
                line = line.replace("TEMPDIR", tempdir)
                line = line.replace("PROJECTNAME", ProjectName)
                line = line.replace("SAMPLENAME", name)
                line = line.replace("ARGUMENTS", arg)
                outfile.write(line)

        Condor_Sub(condorfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='NanoAOD postprocessing.')
    parser.add_argument('-c', '--config',
        default = "sampleconfig.cfg",
        help = 'Path to the input config file.')
    parser.add_argument('-e', '--era',
        default = "0",type=int,
        help = 'Era/Year of the config file. Use if this is not part of the config file name. Will also be appended to the condor directory in the user\'s nobackup area if used.')
    parser.add_argument('-o', '--outputdir',
        default = "", 
        help = 'Path to the output directory.')

    args = parser.parse_args()
    my_process(args)
