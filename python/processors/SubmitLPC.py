#!/usr/bin/env python
# coding: utf-8

import os
import re
import time
import subprocess
import glob
import tarfile
import shutil
import getpass

# TODO: set OutDir (and ProjectName?) to be modified based on input filelist location
DelExe    = 'Stop0l_postproc.py'
OutDir = '/store/user/%s/StopStudy' %  getpass.getuser()
tempdir = '/uscms_data/d3/%s/condor_temp/' % getpass.getuser()
ProjectName = 'PostProcess'

def ConfigList(config):
    process = []
    #TODO: Split between sample set and sample collection configs
    lines = open(config).readlines()
    for line in lines:
        if(len(line) <= 0 or line[0] == '#'):
            continue
        entry = line.split(",")
        stripped_entry = []
        #print("Entry: " + entry[0] + entry[1] + entry[2])
        for i in entry:
            i = i.strip(' ')
            stripped_entry.append(i)
        #if len(entry) is 8, it's MC; if 6, data
        #print("Stripped: " + stripped_entry[0] + stripped_entry[1] + stripped_entry[2])
        process.append(stripped_entry)
    return process

# Name, File path, file name, tree location,...

# Process = {
    # "ProcessName" : ['Path to filelist', split lines]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SM ~~~~~

#Use SampleSet and SampleCollection configs to create a list instead.
#Then add to Process from there? How to determine the line split number? There does seem to be a default for that.

# }

Mergeblock = """#!/usr/bin/env python

# File        : merge.py
# Author      : Ben Wu
# Contact     : benwu@fnal.gov
# Date        : 2015 Jul 20
#
# Description : Code to merge output hists

import re
import glob
import os
import subprocess
import multiprocessing

def MergeFile(prod):
    print "Processing %s" % prod
    g = glob.glob("%s*.root" % prod)
    logfile = open("%s.log" % prod, 'w')
    sub = re.compile(r'^%s_\d+\.root$' % prod)
    allfile = set()
    goodfile = set()
    for f in g:
        if sub.match(f) is not None:
            allfile.add(f)
            if os.path.getsize(f) != 0:
                goodfile.add(f)
    run = "hadd -f merged/%s.root " % prod
    run += " ".join(goodfile)
    process = subprocess.Popen(run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    logfile.write(out)
    logfile.write(err)
    logfile.close()


if __name__ == "__main__":
    cmd_exists = lambda x: any(os.access(os.path.join(path, x), os.X_OK)
                               for path in os.environ["PATH"].split(os.pathsep))
    if cmd_exists('hadd'):
        if not os.path.isdir("merged"):
            os.mkdir("merged")
    else:
        HEADER = '[95m'
        OKBLUE = '[94m'
        OKGREEN = '[92m'
        WARNING = '[93m'
        FAIL = '[91m'
        ENDC = '[0m'
        BOLD = '[1m'
        UNDERLINE = '[4m'
        print(FAIL + "Warning: no hadd available! Please setup ROOT!!" + ENDC)
        exit()

    pattern = re.compile(r'^(.*)_\d+\.root$')
    g = glob.glob("*.root")

    ## Get all the process
    process = set()
    for files in g:
        match = pattern.match(files)
        if match is not None:
            process.add(match.group(1))
        else:
            print files
            cmd = "cp %s merged/" % files
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()

    print process
    ## Run with multiprocessing Pool
    pool = multiprocessing.Pool(processes = multiprocessing.cpu_count()/3)
    pool.map(MergeFile, process)
"""

def Condor_Sub(condor_file):
    curdir = os.path.abspath(os.path.curdir)
    os.chdir(os.path.dirname(condor_file))
    print "To submit condor with " + condor_file
    os.system("condor_submit " + condor_file)
    os.chdir(curdir)


def SplitPro(key, file, fraction):
    splitedfiles = []
    filelistdir = tempdir + '/' + "FileList"
    try:
        os.makedirs(filelistdir)
    except OSError:
        pass


    filename = os.path.abspath(file)
    if fraction == 1:
        splitedfiles.append(os.path.abspath(filename))
        shutil.copy2(os.path.abspath(filename), "%s/%s" % (filelistdir, os.path.basename(filename)))
        return splitedfiles

    f = open(filename, 'r')
    lines = f.readlines()
    if len(lines) <= fraction:
        lineperfile = 1
        fraction = len(lines)
    else:
        lineperfile = len(lines) / fraction
        if len(lines) % fraction > 0:
            lineperfile += 1


    for i in range(0, fraction):
        wlines = []
        if i == fraction - 1 :
            wlines = lines[lineperfile*i :]
        else:
            wlines = lines[lineperfile*i : lineperfile*(i+1)]
        if len(wlines) > 0:
            outf = open("%s/%s.%d.list" % (filelistdir, key, i), 'w')
            outf.writelines(wlines)
            splitedfiles.append(os.path.abspath("%s/%s.%d.list" % (filelistdir, key, i)))
        outf.close()

    return splitedfiles

def my_process():
    ## temp dir for submit
    global tempdir
    global Mergeblock
    global ProjectName
    ProjectName = time.strftime('%b%d') + ProjectName
    tempdir = tempdir + os.getlogin() + "/" + ProjectName +  "/"
    try:
        os.makedirs(tempdir)
    except OSError:
        pass

    ## Create the output directory
    outdir = OutDir +  "/" + ProjectName + "/"
    try:
        os.makedirs("/eos/uscms/%s" % outdir)
    except OSError:
        pass

    ##Read config file
    Process = ConfigList(os.path.abspath("sampleconfig.cfg"))

    ## Update RunHT.csh with DelDir and pileups
    RunHTFile = tempdir + "/" + "RunExe.csh"
    with open(RunHTFile, "wt") as outfile:
        for line in open("RunExe.csh", "r"):
            line = line.replace("DELSCR", os.environ['SCRAM_ARCH'])
            line = line.replace("DELDIR", os.environ['CMSSW_VERSION'])
            line = line.replace("DELEXE", DelExe.split('/')[-1])
            line = line.replace("OUTDIR", outdir)
            outfile.write(line)

    ## Script for merging output histograms
    MergeFile = tempdir + "/" + "merge.py"
    f = open("%s/merge.py" % tempdir, 'wt')
    f.writelines(Mergeblock)
    f.close()
    shutil.copy2("%s/merge.py" % tempdir, "/eos/uscms/%s/merge.py" % outdir)
    ### Keeping track of running script
    # shutil.copy2("../src/testMain.cc", "/eos/uscms/%s/testMain.cc" % outdir)

    ### Create Tarball
    NewNpro = {}
    Tarfiles = []

    """
    for key, value in Process.items():
        if value[0] == "":
            value[0] = "../FileList/"+key+".list"
            #value[0] = "../FileList/"+key
        if not os.path.isfile(value[0]):
            continue

        npro = GetProcess(key, value)
        Tarfiles+=npro
        NewNpro[key] = len(npro)
    """


    for sample in Process:
        print("Getting process: " + sample[0] + " " + sample[1] + sample[2])
        npro = GetProcess(sample[0],[sample[1]+sample[2], 10])
        Tarfiles+=npro
        NewNpro[sample[0]] = len(npro)


    Tarfiles.append(os.path.abspath(DelExe))
    tarballname ="%s/%s.tar.gz" % (tempdir, ProjectName)
    with tarfile.open(tarballname, "w:gz", dereference=True) as tar:
        [tar.add(f, arcname=f.split('/')[-1]) for f in Tarfiles]
        tar.close()

    ### Update condor files
    """
    for key, value in Process.items():
        if NewNpro[key] > 1:
            arg = "\nArguments = %s.$(Process).list %s_$(Process).root \nQueue %d \n" % (key, key, NewNpro[key])
        else:
            arg = "\nArguments = %s.list %s.root \n Queue\n" % (key, key)

        ## Prepare the condor file
        condorfile = tempdir + "/" + "condor_" + ProjectName + "_" + key
        with open(condorfile, "wt") as outfile:
            for line in open("condor_template", "r"):
                line = line.replace("EXECUTABLE", os.path.abspath(RunHTFile))
                line = line.replace("TARFILES", tarballname)
                line = line.replace("TEMPDIR", tempdir)
                line = line.replace("PROJECTNAME", ProjectName)
                line = line.replace("ARGUMENTS", arg)
                outfile.write(line)

    """
    for sample in Process:
        if NewNpro[sample[0]] > 1:
            #arg = "\nArguments = %s.$(Process).list %s_$(Process).root \nQueue %d \n" % (sample[0], sample[0], NewNpro[sample[0]])
            arg = "\nArguments = %s.$(Process).list \nQueue %d \n" % (sample[0], sample[0], NewNpro[sample[0]])
        else:
            #arg = "\nArguments = %s.list %s.root \n Queue\n" % (sample[0], sample[0])
            arg = "\nArguments = %s.list %s.root \n Queue\n" % (sample[0], sample[0])

        ## Prepare the condor file
        condorfile = tempdir + "/" + "condor_" + ProjectName + "_" + sample[0]
        with open(condorfile, "wt") as outfile:
            for line in open("condor_template", "r"):
                line = line.replace("EXECUTABLE", os.path.abspath(RunHTFile))
                line = line.replace("TARFILES", tarballname)
                line = line.replace("TEMPDIR", tempdir)
                line = line.replace("PROJECTNAME", ProjectName)
                #line = line.replace("OUTDIR", sample[1] + "_" + ProjectName)
                line = line.replace("ARGUMENTS", arg)
                outfile.write(line)

        Condor_Sub(condorfile)

def GetProcess(key, value):
    if len(value) == 1:
        return SplitPro(key, value[0], 1)
    else :
        return SplitPro(key, value[0], value[1])
"""
def GetNeededFileList(key):
    relist = []
    g = glob.glob("../FileList/*.tar.gz")
    relist += [os.path.abspath(h) for h in g]
    g = glob.glob("../*root")
    relist += [os.path.abspath(h) for h in g]
    g = glob.glob("../*csv")
    relist += [os.path.abspath(h) for h in g]
    g = glob.glob("../*cfg")
    relist += [os.path.abspath(h) for h in g]
    g = glob.glob("../*model")
    relist += [os.path.abspath(h) for h in g]
    process = subprocess.Popen( "ldd %s " % os.path.abspath(DelExe) , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for l in process.stdout:
        if os.getenv('USER') in l:
            relist.append(l.strip().split(' ')[2])
    return relist
"""
if __name__ == "__main__":
    my_process()
