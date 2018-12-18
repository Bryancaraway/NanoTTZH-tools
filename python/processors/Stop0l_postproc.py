#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoSUSYTools.modules.eleMiniCutIDProducer import *
from PhysicsTools.NanoSUSYTools.modules.Stop0lObjectsProducer import *
from PhysicsTools.NanoSUSYTools.modules.Stop0lBaselineProducer import *
from PhysicsTools.NanoSUSYTools.modules.DeepTopProducer import *


era = "2016"
isFastSim = False
mods = [
    eleMiniCutID(),
    Stop0lObjectsProducer(era),
    DeepTopProducer(era),
    Stop0lBaselineProducer(era, isFastSim),
]

files=["/uscms_data/d3/lpcsusyhad/benwu/Moriond2019/TestNanoAOD/CMSSW_10_2_6/src/PhysicsTools/NanoSUSY/test/test94X_NANO.root"]

p=PostProcessor(".",files,cut=None, branchsel=None, outputbranchsel=None, modules=mods,provenance=False)
p.run()
