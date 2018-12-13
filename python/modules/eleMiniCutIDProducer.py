import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import re

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class eleMiniCutIDProducer(Module):
    def __init__(self):
        self.eleCuts = []
        self.nbit = 0

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Electron_cutBasedNoIso",  "I", lenVar="nElectron")

        ## Get cutbase bit
        eleID =inputTree.GetBranch("Electron_cutBased").GetTitle()
        mats = re.search(r'\((.*?)\)',eleID).groups()
        self.dict_eleID = {}
        for item in mats[0].split(","):
            bit = int(item.split(":")[0])
            ID = item.split(":")[1]
            self.dict_eleID[ID] = bit
        self.sorted_eleID = {v : k for k, v in self.dict_eleID.items()}
        ## Get NestedWP bit
        eledoc =inputTree.GetBranch("Electron_vidNestedWPBitmap").GetTitle()
        mats = re.search(r'\((.*?)\)',eledoc).groups()
        self.eleCuts = mats[0].split(",")
        self.nbit = int(re.findall(r'(\d+) bits',eledoc)[0])
        self.testbit = (1<<self.nbit)-1


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def GetIDnoIso(self, ele):
        looseID = False
        elebits = []
        newID = { k:False for k ,v in  self.dict_eleID.items() }
        ## Get bit except Iso
        for i, c in enumerate(self.eleCuts):
            if c == 'GsfEleRelPFIsoScaledCut':
                continue
            ibit = ele.vidNestedWPBitmap  >> (self.nbit * i) & self.testbit
            elebits.append(ibit)
        ## Pass the new ID
        for k in newID.keys():
            v = self.dict_eleID[k]
            newID[k]= all([i >= v for  i in elebits ])
        ## Store the output
        for v in sorted(self.sorted_eleID.keys(), reverse=True):
            k = self.sorted_eleID[v]
            if newID[k]:
                return v
        return False


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        electrons = Collection(event, "Electron")
        cutBasedNoIso = [ self.GetIDnoIso(ele) for ele in electrons]
        self.out.fillBranch("Electron_cutBasedNoIso", cutBasedNoIso)
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

eleMiniCutID= lambda : eleMiniCutIDProducer()

