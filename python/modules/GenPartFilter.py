import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import numpy as np

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class GenPartFilter(Module):
    def __init__(self, statusFlags = None, statuses = None, pdgIds = None):
        statFlagLen = len(statusFlags) if statusFlags else 0
        statusLen   = len(statuses)    if statuses    else 0
        pdgIdLen    = len(pdgIds)      if pdgIds      else 0

        length = max(statFlagLen, statusLen, pdgIdLen)

        if statFlagLen == length:
            self.statusFlags = np.array(statusFlags)
        else:
            if statusFlags: print "statusFlags length does not match, ignoring statusFlags"
            self.statusFlags = np.array([0]*length)

        if statusLen == length:
            self.statuses = np.array(statuses)
        else:
            if statuses: print "status length does not match, ignoring status"
            self.statuses = np.array([0]*length)

        if pdgIdLen == length:
            self.parentPdgIds = np.array(pdgIds)
        else:
            if pdgIds: print "pdgId length does not match, ignoring pdgId"
            self.parentPdgIds = np.array([0]*length)

        self.vector_recursiveMotherSearch = np.vectorize(self.recursiveMotherSearch, excluded=(1,2))

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree

        self.out.branch("GenPart_eta",              "F", lenVar = "nGenPart", title=inputTree.GetBranch("GenPart_eta").GetTitle() )
        self.out.branch("GenPart_mass",             "F", lenVar = "nGenPart", title=inputTree.GetBranch("GenPart_mass").GetTitle())
        self.out.branch("GenPart_phi",              "F", lenVar = "nGenPart", title=inputTree.GetBranch("GenPart_phi").GetTitle())
        self.out.branch("GenPart_pt",               "F", lenVar = "nGenPart", title=inputTree.GetBranch("GenPart_pt").GetTitle())
        self.out.branch("GenPart_genPartIdxMother", "I", lenVar = "nGenPart", title=inputTree.GetBranch("GenPart_genPartIdxMother").GetTitle())
        self.out.branch("GenPart_pdgId",            "I", lenVar = "nGenPart", title=inputTree.GetBranch("GenPart_pdgId").GetTitle())
        self.out.branch("GenPart_status",           "I", lenVar = "nGenPart", title=inputTree.GetBranch("GenPart_status").GetTitle())
        self.out.branch("GenPart_statusFlags",      "I", lenVar = "nGenPart", title=inputTree.GetBranch("GenPart_statusFlags").GetTitle())

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def recursiveMotherSearch(self, startIdx, GenPartCut_genPartIdxMother, filterArray):
        if startIdx < 0 or filterArray[startIdx]: 
            return startIdx

        mom = GenPartCut_genPartIdxMother[startIdx]

        if mom < 0 or filterArray[mom]:
            return mom
        else:
            return self.recursiveMotherSearch(mom, GenPartCut_genPartIdxMother, filterArray)
        

    class TTreeReaderArrayWrapper:
        def __init__(self, ttarray):
            self.ttarray = ttarray

        def __iter__(self):
            for i in xrange(len(self.ttarray)):
                yield self.ttarray[i]
            return

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        ## Getting objects

        GenPartCut_eta              = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_eta),              dtype=float)
        GenPartCut_mass             = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_mass),             dtype=float)
        GenPartCut_phi              = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_phi),              dtype=float)
        GenPartCut_pt               = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_pt),               dtype=float)
        GenPartCut_genPartIdxMother = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_genPartIdxMother), dtype=int)
        GenPartCut_pdgId            = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_pdgId),            dtype=int)
        GenPartCut_status           = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_status),           dtype=int)
        GenPartCut_statusFlags      = np.fromiter(self.TTreeReaderArrayWrapper(event.GenPart_statusFlags),      dtype=int)

        #calculate filter array 
        flagStatIDReq = (self.statusFlags, self.statuses, self.parentPdgIds)
        filterArrays = [ np.logical_and.reduce( ( (GenPartCut_statusFlags & statusFlag) == statusFlag if statusFlag else np.ones(len(GenPartCut_eta), dtype=bool),
                                                   GenPartCut_status                    == status     if status     else np.ones(len(GenPartCut_eta), dtype=bool),
                                                   abs(GenPartCut_pdgId)                == pdgId      if pdgId      else np.ones(len(GenPartCut_eta), dtype=bool) ) )
                         for statusFlag, status, pdgId in zip(*flagStatIDReq) ]

        #if a gen particle passed any of the filters we to keep it 
        if len(filterArrays) == 1:
            filterArray = filterArrays[0]
        else:
            filterArray = np.logical_or.reduce(filterArrays)

        #revise mother history to fill in the gaps left by the filtering 
        GenPartCut_genPartIdxMother = self.vector_recursiveMotherSearch(GenPartCut_genPartIdxMother, GenPartCut_genPartIdxMother, filterArray)
        #calculate new Idx in filtered list
        oldIdx = np.where(filterArray)
        mapDict = dict(zip(oldIdx[0], np.arange(len(oldIdx[0]))))
        mapDict[-1] = -1
        vMapDict = np.vectorize(mapDict.__getitem__)
        GenPartCut_genPartIdxMother_filtered = vMapDict(GenPartCut_genPartIdxMother[filterArray])

        self.out.fillBranch("GenPart_pt",               GenPartCut_pt[filterArray])
        self.out.fillBranch("GenPart_eta",              GenPartCut_eta[filterArray])
        self.out.fillBranch("GenPart_phi",              GenPartCut_phi[filterArray])
        self.out.fillBranch("GenPart_mass",             GenPartCut_mass[filterArray])

        self.out.fillBranch("GenPart_genPartIdxMother", GenPartCut_genPartIdxMother_filtered)
        self.out.fillBranch("GenPart_pdgId",            GenPartCut_pdgId[filterArray])
        self.out.fillBranch("GenPart_status",           GenPartCut_status[filterArray])
        self.out.fillBranch("GenPart_statusFlags",      GenPartCut_statusFlags[filterArray])

        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
