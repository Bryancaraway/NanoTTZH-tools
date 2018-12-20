import os
import numpy as np
import ROOT, math
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoTrees.helpers.xgbHelper import XGBHelper
from PhysicsTools.NanoTrees.helpers.nnHelper import get_decorr_score
from PhysicsTools.NanoTrees.helpers.jetmetCorrector import JetMETCorrector

def get_softbCC(svCollection, ak4JetCollection):
    softbCCs = []
    for isv in svCollection:
        for ijet in ak4JetCollection:
            if (deltaR(isv,ijet)>0.4):
                continue
            else:
                if (isv.ntracks>2 and abs(isv.dxy)<3. and isv.dlenSig>4):
                    softbCCs.append(isv)
return softbCCs
