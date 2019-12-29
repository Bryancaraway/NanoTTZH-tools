#!/bin/csh -v

set SCRAM  = DELSCR
set CMSSW  = DELDIR
set EXE    = DELEXE
set OUTPUT = OUTDIR

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

if ($? == 0) then
  #echo "Process finished. Listing current files: "
  echo "Process finished. Removing (unmerged) Skim files."
  #echo "Hadd file will be named: " $argv[1]
  foreach outfile (`ls *_Skim*.root`)
    rm $outfile
  end

  foreach outfile (`ls *_Mom*_LSP*.root`)
    #Cut off ".root" and append "_{ProcessNum}.root", passed as first argument
    set cutoffoutfile = `echo $outfile | rev | cut -c 6- | rev`
    echo "Copying " $outfile " to root://cmseos.fnal.gov/${OUTPUT}/$cutoffoutfile$argv[1]"
    xrdcp -f $outfile "root://cmseos.fnal.gov/${OUTPUT}/$cutoffoutfile$argv[1]"
    ## Remove output file once it is copied
    if ($? == 0) then
      rm $outfile
    endif
  end
endif
