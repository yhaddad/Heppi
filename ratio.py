import ROOT
from   rootpy.interactive import wait
import math

ROOT.gROOT.ProcessLine(".x ~/.rootsys/rootlogon.C")


h_mc   = ROOT.TH1F('h_mc'   ,';p_{t}[GeV]',20,0,100);
h_data = ROOT.TH1F('h_data' ,';p_{t}[GeV]',20,0,100);

h_mc.FillRandom("landau",10000)
h_data.FillRandom("landau",8000)

h_mc.Scale(8/10.0)
h_mc.Sumw2()

h_mc.SetFillColor(41)
h_mc.SetLineColor(1)

h_data.SetMarkerColor(1)
h_data.SetLineColor(1)
h_data.SetMarkerSize(1.3)
h_data.SetMarkerStyle(20)
h_data.SetLineColor(1)

def makeDivCan():
    """returns a divided canvas for ratios"""
    Rcanv = ROOT.TCanvas("Rcanv","Rcanv",1024,768)
    Rcanv.cd()
    pad1 = ROOT.TPad("pad1","pad1",0,0.3,1,1)
    pad1.SetNumber(1)
    pad2 = ROOT.TPad("pad2","pad2",0,0,1,0.3)
    pad2.SetNumber(2)

    pad1.Draw()
    pad2.Draw()
    Rcanv.cd()
    #ROOT.SetOwnership(Rcanv,0)
    ROOT.SetOwnership(padup,0)
    ROOT.SetOwnership(paddw,0)
    #print "check stuff", canv.GetPad(1)
    return Rcanv



def MakeStatProgression(myHisto,title=""):
    """This function returns a function with the statistical precision in each bin"""
    statPrecision = myHisto.Clone('_ratioErrors_')
    ##statPrecision.Reset()
    statPrecision.SetTitle(title)
    statPrecision.SetFillColorAlpha(ROOT.kAzure+1, 0.5)
    statPrecision.SetMarkerColorAlpha(0,0)
    for bin in range(myHisto.GetNbinsX()+1):
        y   = statPrecision.GetBinContent(bin);
        err = statPrecision.GetBinError  (bin);
        if (y>0):
            statPrecision.SetBinContent(bin,1);
            statPrecision.SetBinError  (bin,err/y);
        else:
            statPrecision.SetBinContent(bin,1);
            statPrecision.SetBinError  (bin,0);
    statPrecision.GetYaxis().SetRangeUser(0.5,1.6)
    return statPrecision


def drawStatErrBand(myHisto, drawOpt ='', norm=False):
    """
    Draw this histogram with the statistical
    precision error in each bin
    """
    statPrecision = myHisto.Clone('_statErrors_')
    ROOT.SetOwnership(statPrecision,0)
    statPrecision.SetFillColorAlpha(ROOT.kAzure+1, 0.5)
    statPrecision.SetMarkerColorAlpha(0,0)
    if norm:
        myHisto.Draw(drawOpt)
        statPrecision.Draw('E2,same')
    else:
        myHisto.DrawNormalized(drawOpt)
        statPrecision.DrawNormalized('E2,same')

#
def makeRatioPlotCanvas(style=''):
    """
    returns a divided canvas for ratios
    
    """
    canv  = ROOT.TCanvas("canv", "ratio_plot",  700, 850 )
    canv.cd()
    #padup = ROOT.TPad("padup", "padup", 0, 0.4, 1, 1.0)
    padup = ROOT.TPad("padup", "padup", 0, 0.3, 1, 1.0)
    padup.SetNumber(1)
    #paddw = ROOT.TPad("paddw", "paddw", 0, 0.0, 1, 0.4)
    paddw = ROOT.TPad("paddw", "paddw", 0, 0.0, 1, 0.3)
    paddw.SetNumber(2)
    padup.Draw()
    padup.SetTopMargin(0.08) 
    padup.SetBottomMargin(0.00) 
    padup.SetLeftMargin(0.14)
    padup.SetRightMargin(0.05)
    padup.SetFrameBorderMode(0)
    padup.SetFrameBorderMode(0)
    paddw.Draw()
    paddw.SetTopMargin(0.00)
    paddw.SetBottomMargin(0.37)
    paddw.SetLeftMargin(0.14)
    paddw.SetRightMargin(0.05)
    paddw.SetFrameBorderMode(0)
    canv.cd()
    ROOT.SetOwnership(padup,0)
    ROOT.SetOwnership(paddw,0)
    return canv

def makeRatio(hist1,hist2,ymax=False,ymin=False,norm=False):
    """returns the ratio plot hist2/hist1
    if one of the histograms is a stack put it in as argument 2!"""

    if norm:
        print 'scaling!'
        try:
            print 'scale 1: ',1/hist1.Integral()
            print 'scale 2: ',1/hist2.Integral()
            hist1.Scale(1/hist1.Integral())
            hist2.Scale(1/hist2.Integral())
        except(ZeroDivisionError):
            pass
    retH = hist1.Clone()
    try:
        retH.Divide(hist2)
    except(TypeError):
        #this is the error you get if hist2 is a stack
        hList = hist2.GetHists()
        sumHist = hist1.Clone("sumHist")
        sumHist.Reset()
        for h in hList:
            sumHist.Add(h)
        retH.Divide(sumHist)
    except(AttributeError):
        #this is the error you get if hist1 is a stack
        print "Did you use a stack as argument 1? please use stack as argument 2!"
        raise AttributeError
    if ymax or ymin:
        retH.GetYaxis().SetRangeUser(0,2.1)
        retH.SetLineColor(hist1.GetLineColor())
        retH.SetMarkerColor(hist1.GetMarkerColor())
    ROOT.SetOwnership(retH,0)
    return retH

def tworatios(histMC,histData,
              log=False,
              xTitle="",
              yTitle="",
              drawMCOpt="",
              drawDataOpt="",
              norm=False,
              ratioMin=0.5,
              ratioMax=1.5):
    """Takes two histograms as inputs and returns a canvas with a ratio plot of the two.
    The two optional arguments are for the x Axis and y Axis titles"""

    c = makeRatioPlotCanvas()#makeDivCan()
    pad1 = c.cd(1)
    pad2 = c.cd(2)
    c.cd(1)
    
    if log: pad1.SetLogy()
    yMax = max(histData.GetMaximum(),histMC.GetMaximum())
    yMin = 0
    
    if log: yMin = min(histData.GetMinimum(),histMC.GetMinimum())
    else  : yMin = 0
    if log: yMax = 100*yMax
    else  : yMax = 1.2*yMax

    try:
        histData.GetYaxis().SetRangeUser(0,1.2*yMax)
    except(ReferenceError):
        h = pad1.DrawFrame(histMC.GetXaxis().GetXmin(),yMin,histMC.GetXaxis().GetXmax(),yMax)
        ROOT.SetOwnership(h,0)
    if not norm:
        drawStatErrBand(histMC,drawMCOpt)
        histData.Draw  ('same,'+drawDataOpt)
    else:
        histMC   = histMC.DrawNormalized(drawMCOpt)
        histData = histData.DrawNormalized("same"+ drawDataOpt)
                
    histData.GetYaxis().SetRangeUser(yMin,yMax)
    c.cd()
    c.cd(2)
    
    errorHist = MakeStatProgression(histMC,title="")
    ROOT.SetOwnership(errorHist,0)
    errorHist.GetXaxis().SetTitle(xTitle)
    errorHist.GetYaxis().SetTitle(yTitle)
    errorHist.Draw('E2')
    
    ratioHist = makeRatio(histData,histMC,ymax= ratioMax,ymin=ratioMin,norm=norm)
    ROOT.SetOwnership(ratioHist,0)
    ratioHist.GetXaxis().SetTitle(xTitle)
    ratioHist.GetYaxis().SetTitle(yTitle)

    line = ROOT.TLine(ratioHist.GetXaxis().GetXmin(),1,ratioHist.GetXaxis().GetXmax(),1)
    line.SetLineColor(2)
    line.Draw()
    ROOT.SetOwnership(line,0)
    ratioHist.Draw('same')
    c.cd()
    return c


#

c = tworatios(h_mc,h_data,log=True,
              drawMCOpt="hist",
              drawDataOpt="e",)
#c.SaveAs('test.png')
#c.SaveAs('test.pdf')

wait()

#def ratio_plot(h_mc, h_data=None):
#    
#    h_mc_error = h_mc.Clone("h_mc_error")
#    h_mc_error.SetFillColorAlpha(2,0.5)
#    h_mc_error.SetMarkerColorAlpha(0,0)
#    
#    h_ratio = h_mc.Clone("h_ratio")
#    h_ratio.Divide(h_mc,h_data)
#    
#    h_ratio.SetMarkerColor(1)
#    h_ratio.SetLineColor(1)
#    h_ratio.SetMarkerSize(1.2)
#    h_ratio.SetMarkerStyle(20)
#    
#    h_ratio_error = h_mc.Clone("h_ratio")
#    h_ratio_error.Divide(h_mc,h_mc)
#    h_ratio_error.SetFillColorAlpha(2,0.5)
#    thecanvas    = ROOT.TCanvas("thecanvas", "thecanvas",  600, 700 )
#    thetoppad    = ROOT.TPad("toppad",    "toppad",    0.0, 0.4, 1., 1., 0, 0, 0 )
#    thebottompad = ROOT.TPad("bottompad", "bottompad", 0.0, 0., 1., 0.4, 0, 0, 0)
#    thecanvas.cd()
#    thetoppad.Draw()
#    thetoppad.cd()
#    thetoppad.SetTopMargin(0.05) ###margin goes to the top of the pad
#    thetoppad.SetBottomMargin(0.00) ###low margin goes to the bottom
#    #if noratio : thetoppad.SetBottomMargin(0.10) ###low margin goes to the bottom
#    thetoppad.SetLeftMargin(0.14)
#    thetoppad.SetRightMargin(0.05)
#    thetoppad.SetFrameBorderMode(0)
#    thetoppad.SetFrameBorderMode(0)
#    
#    ROOT.gPad.SetLogy()
#    h_mc.Draw('hist')
#    
#    h_mc_error.Draw('E2,same')
#    h_data.Draw('e,same')
#    
#    thecanvas.cd()
#    thebottompad.Draw()
#    thebottompad.cd()
#    thebottompad.SetTopMargin(0.00) ###margin goes to the top of the pad
#    thebottompad.SetBottomMargin(0.37)
#    thebottompad.SetLeftMargin(0.14)
#    #if variables == "PRplot" : thebottompad.SetLeftMargin(0.1)
#    thebottompad.SetRightMargin(0.05)
#    thebottompad.SetFrameBorderMode(0)
#    h_ratio.GetYaxis().SetLabelSize(0.08)
#    h_ratio.GetXaxis().SetLabelSize(0.08)
#    h_ratio.GetYaxis().SetRangeUser(0,2.1)
#    
#    h_ratio.Draw('e')
#    h_ratio_error.Draw('E2,same')
#    h_ratio.Draw('e,same')
#    
#
#    thecanvas.SaveAs('plot_ratio.pdf')
#
#
#ratio_plot(h_mc, h_data)

