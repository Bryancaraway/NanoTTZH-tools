#!/usr/bin/env python
# coding: utf-8

import uproot
from collections import defaultdict
import glob
import uproot
from multiprocessing import Pool
import subprocess 
import os

TreeName = "Events"
NProcess = 8

def CheckMCProcess(quenue, filelist, outname, outdir):
    for i in range(0, quenue):
        inputlist_ = filelist.replace("$(Process)", str(i))
        outputname_ = outname.replace("$(Process)", str(i))
        inputlist = "FileList/%s" % inputlist_
        outputname = "root://cmseos.fnal.gov/%s/%s" % (outdir, outputname_)
        if not os.path.exists(inputlist):
            continue
        ncnt_dict = GetNEventFromList(inputlist)
        ncnt_list = sum(ncnt_list.values())
        outcnt = 0
        try:
            outcnt = uproot.numentries(outputname, TreeName)
        except:
            print("Soemthing wrong with file")
        if (ncnt_list != outcnt):
            print("Production failed for %s : input file %s , outputname %s"  % (condorfile, inputlist, outputname ))


def CheckFastProcess(quenue, filelist, outname, outdir):
    # Getting all the output file in outdir and their event counts
    p = subprocess.Popen("eos root://cmseos.fnal.gov ls %s" % outdir, shell=True, stdout=subprocess.PIPE)
    outfile = p.communicate()
    out = GetNEvent(outdir, outfile[0].split())
    compout = {}
    postedout = set()
    for k, v in out.items():
        newk = k.split("/")[-1].split("_Skim")[0]
        compout[newk] = v
    
    for i in range(0, quenue):
        inputlist_ = filelist.replace("$(Process)", str(i))
        outputname_ = outname.replace("$(Process)", str(i))
        inputlist = "FileList/%s" % inputlist_
        if not os.path.exists(inputlist):
            print("Missing input file in queue: %s" %  inputlist)
            continue
        ncnt_dict = GetNEventFromList(inputlist)
        compin = {}
        for k, v in ncnt_dict.items():
            filename = k.split("/")[-1].split(".")[0]
            if filename not in compout:
                print("Missing output %s in job %d " % (filename, i))
            elif compout[filename] != v:
                print("Event mismatch of %s in job %d, expecting %d, obtained %d" % (filename, i, v, compout[filename]))
                postedout.add(filename)
            else:
                postedout.add(filename)
    
    if postedout != compout.keys():
        missing = postedout - set(compout.keys())
        extra = set(compout.keys()) - postedout 
        if len(missing) != 0:
            print("Missed signals: %s" % (", ".join(list(missing))))
        if len(extra) != 0:
            print("Extra signals: %s" % (", ".join(list(extra))))

def CheckProcess(condorfile):
    print("Checking %s" % condorfile)
    confile = open(condorfile)
    runscript = None
    quenue = 0
    argument  = None
    filelist = None
    outdir = None
    outname = None

    for l_ in confile.readlines():
        l = l_.strip()
        if "Executable" in l:
            runscript = l.split("=")[-1].strip()
        if "Arguments" in l:
            argument = l.split("=", 1)[-1]
            filelist = argument.split(" ")[2].split("=")[-1]
            outname = argument.split(" ")[1]
        if "Queue" in l:
            quenue = int(l.split(" ", 1)[-1])

    if runscript is not None:
        with open(runscript) as exefile:
            for l in exefile.readlines():
                if "set OUTPUT" in l:
                    outdir = l.split("=")[-1].strip()

    if "fastsim" in condorfile:
        CheckFastProcess(quenue, filelist, outname, outdir)
    else:
        CheckMCProcess(quenue, filelist, outname, outdir)


def PoolStopfile(file):
    return (file, uproot.numentries(file, TreeName))

def GetNEvent(outdir, outfiles):
    filelist = [ "root://cmseos.fnal.gov/%s/%s" % (outdir, i) for i in outfiles ]
    r = None
    pool = Pool(processes=NProcess)
    r = pool.map(PoolStopfile, filelist)
    pool.close()
    pool.join()
    dfdict = dict(r)
    return dfdict


def GetNEventFromList(inputlist):
    filelist = open(inputlist, 'r').read().splitlines()
    r = None
    pool = Pool(processes=NProcess)
    r = pool.map(PoolStopfile, filelist)
    pool.close()
    pool.join()
    dfdict = dict(r)
    return dfdict

if __name__ == "__main__":
    files = glob.glob("condor*")
    for f in files:
        CheckProcess(f)
        # break
