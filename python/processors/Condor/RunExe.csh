#!/bin/csh -v

set SCRAM  = DELSCR
set CMSSW  = DELDIR
set EXE    = DELEXE
set OUTPUT = OUTDIR
set Hadd   = HADDFILES

#============================================================================#
#-----------------------------   Setup the env   ----------------------------#
#============================================================================#
echo "============  Running on" $HOST " ============"
cd ${_CONDOR_SCRATCH_DIR}
source /cvmfs/cms.cern.ch/cmsset_default.csh
setenv SCRAM_ARCH ${SCRAM}
eval `scramv1 project CMSSW ${CMSSW}`
tar -xzf ${_CONDOR_SCRATCH_DIR}/CMSSW.tar.gz
cd ${CMSSW}
eval `scramv1 runtime -csh` # cmsenv is an alias not on the workers
echo "CMSSW: "$CMSSW_BASE

cd ${_CONDOR_SCRATCH_DIR}
foreach tarfile (`ls *gz FileList/*gz`)
  echo $tarfile
  tar -xzf $tarfile 
end

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Setup for rootpy ~~~~~
setenv PYTHONPATH  ${_CONDOR_SCRATCH_DIR}
setenv XDG_CONFIG_HOME ${_CONDOR_SCRATCH_DIR}/.config
setenv XDG_CACHE_HOME ${_CONDOR_SCRATCH_DIR}/.cache

if ! $?LD_LIBRARY_PATH then
    setenv LD_LIBRARY_PATH ./
else
    setenv LD_LIBRARY_PATH ./:${LD_LIBRARY_PATH}
endif

#============================================================================#
#--------------------------   To Run the Process   --------------------------#
#============================================================================#

#argv[1] is the hadd file name that will be copied over. Other arguments are for the postprocessor.
echo $EXE $argv[2-]
python $EXE $argv[2-]

if ($? != 0) then
    echo "Error in processing! Please double check"
    if (! $argv[2] =~ *fastsim* ) then
        echo "Not running fastsim sample, exiting this job. Please resumbit"
        exit 1
    endif
endif

## Special treat me
#
if ($argv[2] =~ *fastsim*  || $Hadd != true ) then
    echo "Process finished." 
    set newpost = `echo $argv[1] | rev | cut -f 1 -d _ | rev`
    foreach outfile (`ls *.root`)
        #Cut off ".root" and append "_{ProcessNum}.root", passed as first argument
        set pre = `echo $outfile | cut -f 1 -d .`
        echo "Copying " $outfile " to ${OUTPUT}/${pre}_${newpost}"
	if ($OUTPUT =~ *gsiftp*) then
	    # for gfal to work, turn off cmsenv
	    #setenv PYTHONHOME /cvmfs/cms.cern.ch/slc7_amd64_gcc700/external/python/2.7.14/
	    eval `scram unsetenv -csh`; gfal-copy -fp $outfile "${OUTPUT}/${pre}_${newpost}"
	else
	    xrdcp -f $outfile "${OUTPUT}/${pre}_${newpost}"
	endif
        # Remove output file once it is copied
        if ($? == 0) then
            rm $outfile
        endif
    end
else
    echo "Process finished. Listing current files: "
    echo "Hadd file will be named: " $argv[1]
    python $CMSSW_BASE/src/PhysicsTools/NanoAODTools/scripts/haddnano.py $argv[1] `ls *_Skim*.root`
    ## Remove skim files once they are merged
    if ($? == 0) then
        foreach outfile (`ls *_Skim*.root`)
            rm $outfile
        end
    endif
    foreach i (1 2 3)
	if ($OUTPUT =~ *gsiftp*) then
	    # for gfal to work, turn off cmsenv
	    #setenv PYTHONHOME /cvmfs/cms.cern.ch/slc7_amd64_gcc700/external/python/2.7.14/
	    eval `scram unsetenv -csh`; gfal-copy -fp $argv[1] "${OUTPUT}/${pre}_${newpost}"
	else
	    xrdcp -f $argv[1] "${OUTPUT}/${pre}_${newpost}"
	endif
        #xrdcp -f $argv[1] "root://cmseos.fnal.gov/${OUTPUT}/$argv[1]"
        ## Remove output file once it is copied
        if ($? == 0) then
            rm $argv[1] 
            break
        endif
    end
endif
