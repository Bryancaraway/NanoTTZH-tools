#!/usr/bin/env python
# coding: utf-8

import uproot
from collections import defaultdict
import glob
import uproot
import argparse
from multiprocessing import Pool
import subprocess 
import os
import time

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

## Only work for fastsim samples. Will create a dummy file for resubmit
def ParseStopCfg(file, prodversion):
    f = open(file, 'r')
    for l in f.readlines():
        if l[0] == "#" or len(l) == 1 or "fastsim" not in l:
            continue
        else:
            pa = l.strip().split(",")
            print("+++++++++++ Processing %s " % pa[0].strip())
            out = GetNEventFromList(pa[1].strip()+"/"+pa[2].strip())
            prestopdf = {k.split("/")[-1].split(".")[0]:v for k, v in out.items()} 
            filemap =  {k.split("/")[-1].split(".")[0]:k for k, v in out.items()} 

            postfolder = pa[1].strip().replace("Pre", "Post") + "_"+prodversion + "/" + pa[0].strip()
            p = subprocess.Popen("eos root://cmseos.fnal.gov ls %s" % postfolder, shell=True, stdout=subprocess.PIPE)
            outfile = p.communicate()

            out = GetNEvent(postfolder, outfile[0].split())
            poststopdf = {k.split("/")[-1].split("_Skim")[0]:v for k, v in out.items()} 

            if len(out) != len(poststopdf):
                print("Found Duplicates outputs!")
                duplicates = defaultdict(list)
                for k, v in out.items():
                    duplicates[k.split("/")[-1].split("_Skim")[0] ].append(k)

                for k, v in duplicates.items():
                    if len(v) > 1:
                        for i in v:
                            print("%s :%s" %(out[i], i))

            resub = []

            for pk, pv in prestopdf.items():
                if pk not in poststopdf:
                    # print("Missing", filemap[pk])
                    resub.append(filemap[pk])
                    continue
                if pv != poststopdf[pk]:
                    # print("Mis match", filemap[pk])
                    resub.append(filemap[pk])
            if len(resub) !=  0:
                outname = pa[2].strip().replace(".txt", "_resubmit_%s.txt" % time.strftime('%d%H%M'))
                newfilename = pa[1].strip() + "/" + outname
                pa[2] = outname
                print(", ".join(pa))
                with open(newfilename, "w") as f:
                    f.write("\n".join(resub))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='NanoAOD postprocessing.')
    parser.add_argument('-c', '--config',
        default = None,
        help = 'Path to the input config file. Without cfg, it will check the current condor folder' )
    parser.add_argument('-p', '--prod',
        default = "v6",
        help = 'Postprocess version')
    args = parser.parse_args()

    if args.config is not None:
        ParseStopCfg(os.path.abspath(args.config), args.prod)
    else:
        files = glob.glob("condor*")
        for f in files:
            CheckProcess(f)
