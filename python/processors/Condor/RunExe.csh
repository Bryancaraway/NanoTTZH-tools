#!/bin/csh -v

set SCRAM = DELSCR
set CMSSW = DELDIR
set EXE   = DELEXE
set OUTPUT = OUTDIR

#============================================================================#
#-----------------------------   Setup the env   ----------------------------#
#============================================================================#
echo "============  Running on" $HOST " ============"
cd ${_CONDOR_SCRATCH_DIR}
source /cvmfs/cms.cern.ch/cmsset_default.csh
setenv SCRAM_ARCH ${SCRAM}
eval `scramv1 project CMSSW ${CMSSW}`
cd ${CMSSW}
eval `scramv1 runtime -csh` # cmsenv is an alias not on the workers
echo "CMSSW: "$CMSSW_BASE
tar -xzvf ${_CONDOR_SCRATCH_DIR}/CMSSW.tar.gz

cd ${_CONDOR_SCRATCH_DIR}
foreach tarfile (`ls *gz FileList/*gz`)
  echo $tarfile
  tar -xzf $tarfile 
end

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
  echo "Process finished. Listing current files: "
  ls
  echo "Hadd file will be named: " $argv[1]
  python $CMSSW_BASE/src/PhysicsTools/NanoAODTools/scripts/haddnano.py $argv[1] `ls *_Skim.root`
  #foreach tarfile (`ls *gz FileList/*gz`)
  #  tar -tf $tarfile  | xargs rm -r
  #end
  xrdcp $argv[1] "root://cmseos.fnal.gov/${OUTPUT}/$argv[1]"
  foreach outfile (`ls *_Skim.root`)
    #echo "Copying ${outfile} to ${OUTPUT}"
    #xrdcp $outfile "root://cmseos.fnal.gov/${OUTPUT}"
    #if ($? == 0) then
    #  rm $outfile
    #endif
    rm $outfile
  end
endif
