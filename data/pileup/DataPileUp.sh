#!/bin/bash

# Source info: http://ecalelfs.github.io/ECALELF/PUFILES_.html
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJSONFileforData#Pileup_JSON_Files_For_Run_II
# 13 TeV Min Bias cross section :
# https://cms-service-lumi.web.cern.ch/cms-service-lumi/brilwsdoc.html
#
# The pileupCalc.py comes with CMSSW Release, but has a bug in line 253
# You need to copy it locally and correct it

# Suggested minBiasXsec is set as 68.6+- 1.7 mb
# https://hypernews.cern.ch/HyperNews/CMS/get/luminosity/613/2/1/1/1/1/1/1.html
# declare -A sys=( [pileup]=68600 [pileup_plus]=70300 [pileup_minus]=66900 )

# Updated to the offical recommendation from LUMI POG
# https://twiki.cern.ch/twiki/bin/view/CMS/PileupJSONFileforData#Recommended_cross_section
# The recommended cross-section for Run 2 is 69.2 mb; The uncertainty in this measurement is 4.6%
declare -A sys=( [pileup]=69200 [pileup_plus]=72383 [pileup_minus]=66017 )


GeneratorPileUp()
{
  for key in ${!sys[@]}; do
      echo ${key} ${sys[${key}]}
      ./pileupCalc.py -i $JSONFILE --inputLumiJSON $PileUpJSON  --calcMode true --minBiasXsec ${sys[${key}]} \
        --pileupHistName ${key}  --maxPileupBin 100 --numPileupBins 100 ${OUTPUTFILE}_${key}.root
  done
  hadd ${OUTPUTFILE}.root ${OUTPUTFILE}_*.root
  rm ${OUTPUTFILE}_*.root
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2016 ~~~~~
JSONFILE=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt
PileUpJSON=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt
OUTPUTFILE=Cert271036_284044_23Sep2016ReReco_Collisions16
GeneratorPileUp

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2017 ~~~~~
JSONFILE=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt
PileUpJSON=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PileUp/pileup_latest.txt
OUTPUTFILE=Cert294927_306462_EOY2017ReReco_Collisions17
GeneratorPileUp

JSONFILE=./Collisions17_BtoE_JSON.txt
PileUpJSON=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PileUp/pileup_latest.txt
OUTPUTFILE=Collisions17_BtoE
GeneratorPileUp

JSONFILE=./Collisions17_F_JSON.txt
PileUpJSON=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PileUp/pileup_latest.txt
OUTPUTFILE=Collisions17_F
GeneratorPileUp
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 2018 ~~~~~
JSONFILE=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/ReReco/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt
PileUpJSON=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PileUp/pileup_latest.txt
OUTPUTFILE=ReReco2018ABC_PromptEraD_Collisions18
GeneratorPileUp

JSONFILE=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt 
PileUpJSON=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PileUp/pileup_latest.txt
OUTPUTFILE=Cert314472_325175_PromptReco_Collisions18
GeneratorPileUp
