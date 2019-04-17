import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import math
import numpy as np

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class PDFUncertiantyProducer(Module):
    def __init__(self, isData, isSUSY):
        self.isData = isData
        self.isSUSY = isSUSY
        self.pset = None
        self.pdfs = None

    def beginJob(self):
        pass
    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        # For reading in type ROOT.TTreeReaderArray<float>, the postprocessor
        # can't read in the value properly for the first event in the root file
        # So we use below boolean to read it twice
        self.isFirstEventOfFile = True
        self.out = wrappedOutputTree
        self.out.branch("pdfWeight_Up",   "F", title="PDF weight uncertainty up, scaled to central value")
        self.out.branch("pdfWeight_Down", "F", title="PDF weight uncertainty down,, scaled to central value")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def SetupLHAPDF(self):
        if self.pset is not None:
            return True
        # Get LHAPDF from CMSSW
        import os
        cwd = os.getcwd()
        os.chdir(os.environ['CMSSW_BASE'] )
        c= os.popen("scram tool info LHAPDF" ).read()
        os.chdir(cwd)
        path = None
        for l in c.split("\n"):
            if "LIBDIR" in l:
                path = l.split("=")[-1] +"/python2.7/site-packages/"
        import sys
        sys.path.insert(1, path)
        try:
            global lhapdf
            import lhapdf
        except:
            print("Cannot import LHAPDF, please setup CMSSW!")
            return False
        return True

    def GetfromLHAPDF(self, gen):
        if not self.SetupLHAPDF():
            return 0, None
        ## Default PDF used for 2017 and 2018 production
        if self.pset is None:
            self.pset = lhapdf.getPDFSet("NNPDF31_nnlo_as_0118") # ErrorType: replicas
            self.pdfs = self.pset.mkPDFs()

        npar = self.pset.errorType.count("+") # number of parameter variations (alphaS, etc.)
        if npar > 0:
            print("Last %d members are parameter variations\n" % (2*npar))

        ## Fill vectors xgAll and xuAll using all PDF members.
        pdfweights = [0.0 for i in range(self.pset.size)]

        x1_cen = self.pdfs[0].xfxQ(gen.id1, gen.x1, gen.scalePDF)
        x2_cen = self.pdfs[0].xfxQ(gen.id2, gen.x2, gen.scalePDF)
        normweight = x1_cen * x2_cen
        for imem in range(self.pset.size):
            x1_imem = self.pdfs[imem].xfxQ(gen.id1, gen.x1, gen.scalePDF)
            x2_imem = self.pdfs[imem].xfxQ(gen.id2, gen.x2, gen.scalePDF)
            pdfweights[imem] =  x1_imem * x2_imem / normweight
        return self.pset.size, pdfweights
    
    def getattr_safe(self, event, name):
        out = None
        try:
            out = getattr(event, name)
        except RuntimeError:
            pass
        return out
            


    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        if self.isData:
            return True
        PdfWs = self.getattr_safe(event, "LHEPdfWeight")
        nPdfW = self.getattr_safe(event, "nLHEPdfWeight")
        mean  = 1
        err   = 0

        if self.isFirstEventOfFile:
            PdfWs = self.getattr_safe(event, "LHEPdfWeight")
            nPdfW = self.getattr_safe(event, "nLHEPdfWeight")
            self.isFirstEventOfFile = False

        if not self.isSUSY and (nPdfW == 0 or nPdfW is None):
            nPdfW, PdfWs = self.GetfromLHAPDF(Object(event,     "Generator"))

        if nPdfW is not None and nPdfW != 0:
            if isinstance(PdfWs, np.ndarray):
                lPdfWs = PdfWs
            else:
                lPdfWs = np.asarray([ PdfWs[i] for i in range(nPdfW)])
            if nPdfW == 101: #NNPDF
                ## Following the PDF uncertainties for MC sets recommendation from
                ## Sec 6.2 from PDF4LHC (https://arxiv.org/pdf/1510.03865.pdf)
                ## Use Mean value and standard deviation method for Gassian 
                ## Or 16th and 84th elements for non-Gassian distribution
                newpdf = np.sort(lPdfWs[1:])
                w84 = newpdf[84]
                w16 = newpdf[16]
                mean = (w84+w16)/2
                err = (w84-w16)/2
            else:
                mean = np.mean(lPdfWs[1:])
                err  = np.std(lPdfWs[1:])

        if self.isSUSY:
            ## The PDF uncertainty is recommended to ignore 
            ## https://twiki.cern.ch/twiki/bin/view/CMS/SUSYSignalSystematicsRun2#Post_Jamboree_recommendation_abo
            mean = 1
            err = 0

        ### Store output
        self.out.fillBranch("pdfWeight_Up",   1+err/mean)
        self.out.fillBranch("pdfWeight_Down", 1-err/mean)
        return True
