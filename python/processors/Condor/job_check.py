import os
import subprocess as sb
#check my jobs
print("== Checking Bryans 2016 jobs ==")
os.system("grep -l 'Error in processing' /uscmst1b_scratch/lpc1/3DayLifetime/bcaraway/TestCondor/bcaraway/Jan09PostProcess_v7_2016/*.stderr")
print("checking gfal timeout")
os.system("grep -l 'Command timed out after' /uscmst1b_scratch/lpc1/3DayLifetime/bcaraway/TestCondor/bcaraway/Jan09PostProcess_v7_2016/*.stderr | wc -l")
os.system("grep -l 'Connection timed out' /uscmst1b_scratch/lpc1/3DayLifetime/bcaraway/TestCondor/bcaraway/Jan09PostProcess_v7_2016/*.stderr | wc -l ")
print("== Checking Bryans 2017 jobs ==")
os.system("grep -l 'Error in processing' /uscmst1b_scratch/lpc1/3DayLifetime/bcaraway/TestCondor/bcaraway/Jan09PostProcess_v7_2017/*.stderr")
print("checking gfal timeout")
os.system("grep -l 'Command timed out after' /uscmst1b_scratch/lpc1/3DayLifetime/bcaraway/TestCondor/bcaraway/Jan09PostProcess_v7_2017/*.stderr | wc -l")
os.system("grep -l 'Connection timed out' /uscmst1b_scratch/lpc1/3DayLifetime/bcaraway/TestCondor/bcaraway/Jan09PostProcess_v7_2017/*.stderr | wc -l ")
print("== Checking Bryans 2018 jobs ==")
os.system("grep -l 'Error in processing' /uscmst1b_scratch/lpc1/3DayLifetime/bcaraway/TestCondor/bcaraway/Jan09PostProcess_v7_2018/*.stderr")
print("checking gfal timeout")
os.system("grep -l 'Command timed out after' /uscmst1b_scratch/lpc1/3DayLifetime/bcaraway/TestCondor/bcaraway/Jan09PostProcess_v7_2018/*.stderr | wc -l")
os.system("grep -l 'Connection timed out' /uscmst1b_scratch/lpc1/3DayLifetime/bcaraway/TestCondor/bcaraway/Jan09PostProcess_v7_2018/*.stderr | wc -l")

#print("Checking expired grid cert")
#os.system("grep -l 'Permission denied' /uscmst1b_scratch/lpc1/3DayLifetime/bcaraway/TestCondor/bcaraway/Dec29PostProcess_v7_2018/*.stderr")
# check Kens 2017 jobs
#print("== Checking Kens 2017 jobs ==")
##check Kens 2016 jobs
#print("== Checking Kens 2016 jobs ==")
#os.system("grep Error /uscmst1b_scratch/lpc1/3DayLifetime/hatake/TestCondor/hatake/Jan04PostProcess_v7_2016/*.stdout | grep processing")
#os.system("grep -l 'Error in processing' /uscmst1b_scratch/lpc1/3DayLifetime/hatake/TestCondor/hatake/Jan04PostProcess_v7_2016/*.stderr")
#print("Checking expired grid cert")
#os.system("grep -l 'Permission denied' /uscmst1b_scratch/lpc1/3DayLifetime/hatake/TestCondor/hatake/Jan04PostProcess_v7_2016/*.stderr")
#print("== Checking Kens 2018 jobs ==")
#os.system("grep Error /uscmst1b_scratch/lpc1/3DayLifetime/hatake/TestCondor/hatake/Jan05PostProcess_v7_2018/*.stdout | grep processing")
#os.system("grep -l 'Error in processing' /uscmst1b_scratch/lpc1/3DayLifetime/hatake/TestCondor/hatake/Jan05PostProcess_v7_2018/*.stderr")
#print("Checking expired grid cert")
#os.system("grep -l 'Permission denied' /uscmst1b_scratch/lpc1/3DayLifetime/hatake/TestCondor/hatake/Jan05PostProcess_v7_2018/*.stderr")
#print("== Checking Joes 2016 jobs ==")
##os.system("grep Error /uscmst1b_scratch/lpc1/3DayLifetime/hatake/TestCondor/hatake/Dec29PostProcess_v7_2016/*.stdout | grep processing")
#os.system("grep -l 'Error in processing' /uscmst1b_scratch/lpc1/3DayLifetime/pastika/TestCondor/pastika/Dec30PostProcess_v7_2016/*.stderr")
#print("Checking expired grid cert")
#os.system("grep -l 'Permission denied' /uscmst1b_scratch/lpc1/3DayLifetime/pastika/TestCondor/pastika/Dec30PostProcess_v7_2016/*.stderr")


# check Zhenbins 2017 jobs
#print("== Checking Zhenbins 2016 jobs ==")
#os.system("grep Error /uscmst1b_scratch/lpc1/3DayLifetime/benwu/TestCondor/benwu/Dec29PostProcess_v7_2016/*.stdout | grep processing | wc -l")
#print("Checking expired grid cert")
#os.system("grep -l 'Permission denied' /uscmst1b_scratch/lpc1/3DayLifetime/benwu/TestCondor/benwu/Dec29PostProcess_v7_2016/*.stderr | wc -l")
#zhj = sb.Popen("grep Error /uscmst1b_scratch/lpc1/3DayLifetime/benwu/TestCondor/benwu/Dec29PostProcess_v7_2016/*.stdout | grep processing ", shell=True, stdout=sb.PIPE, stderr=sb.PIPE)
#out, err = zhj.communicate()
#kens_2016_jobs = {
#    'Data_SingleElectron_2016_PeriodE',
#    'Data_SingleElectron_2016_PeriodH',
#    'Data_SingleMuon_2016_PeriodD',
#    'Data_SingleMuon_2016_PeriodG',
#    'ST_tW_antitop_2016',
#    'TTGJets_2016',
#    'TTTT_2016',
#    'TTTo2L2Nu_2016',
#    'TTTo2L2Nu_hdampDown_2016',
#    'TTTo2L2Nu_hdampUp_2016',
#    'TTToHadronic_2016',
#    'TTZToBB_2016',
#    'TTbb_2L2Nu_hdampUp_2016',
#    'WJetsToLNu_HT_100to200_2016',
#}
#bad_jobs = []
#for job in out.splitlines():
#    one_of_kens2016 = False
#    for kjob in kens_2016_jobs:
#        if kjob in job:
#            one_of_kens2016 = True
#    if one_of_kens2016: continue
#    bad_jobs.append(job)
#print(len(bad_jobs))
#print('\n'.join(bad_jobs))
