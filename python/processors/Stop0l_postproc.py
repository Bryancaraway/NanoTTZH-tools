#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoSUSYTools.modules.exampleModule import *
from PhysicsTools.NanoSUSYTools.modules.eleMiniCutIDProducer import *

p=PostProcessor(".",["root://cmseos.fnal.gov//store/user/benwu/Stop18/NtupleSyncMiniAOD/NanoSUSY/test94X_NANO.root"],"Jet_pt>150","keep_and_drop.txt",[eleMiniCutID()],provenance=False)
p.run()
