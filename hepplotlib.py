import ROOT # needed
import os, sys, glob, sys, json
import logging
from   rootpy.tree import Cut  # more robust
import colors 
from rootpy.interactive import wait

#-----------------------------------
class options:
    def __init__(self):
        self.samples     = {}
        self.variables   = {}
        self.rootfile    = {}
        self.cutflow     = [] ## save all the cuts
        self.selections  = {}
        self.sampledir   = './data/' ## temp variable
        self.treename    = 'VBFMVADumper/trees/*_13TeV_VBFDiJet'
        self.allnormhist = False
        self.args        = None
        
#-----------------------------------
def draw2Legend(histo1,
                histo2,
                label1,
                label2):
    legend = ROOT.TLegend(0.5, 0.75,
                          (1.00 - ROOT.gStyle.GetPadRightMargin()),
                          (0.99 - ROOT.gStyle.GetPadTopMargin()))
    legend.SetTextAlign( 12 )
    legend.SetTextFont ( 42 )
    legend.SetTextSize ( 0.04 )
    legend.SetLineColor( 0 )
    legend.SetLineColorAlpha(0,0)
    legend.SetShadowColor(0)
    
    entry1 = legend.AddEntry( histo1, label1, "f" );
    entry2 = legend.AddEntry( histo2, label2, "f" );
    
    legend.SetFillColor( 0 );
    legend.SetFillStyle( 0 );
    legend.Draw();
#-----------------------------------
def read_plotcard(plotcard):
    config = json.loads(open(plotcard).read())
    for key in config:
        if 'variables' in key:
            logging.debug(' ---- book variables ----')
            for var in config[key]:
                logging.debug(' -- %17s  %12s ' % ( var ,config[key][var]['hist']))
                variables[var] = config[key][var]
        if 'processes' in key:
            logging.debug(' ---- book processes ----')
            for proc in config[key]:
                logging.debug(' -- %17s  %12s ' % (proc,  config[key][proc]))
                samples[proc] = config[key][proc]
                
        if 'selections' in key:
            logging.debug(' ---- book selections ---')
            for sel in config[key]:
                print
                logging.debug(' -- %17s  %12s ' % (sel , config[key][sel]))
                selections[sel] = config[key][sel]
            logging.debug(' -------------------')

#-----------------------------------
def produce_histos(variable, selection='', options=[''] ,mode=''):
    """
    mode:
    [1] none : produce a list of histogram with with the corresponding collors. only the samples labeled 
    'signal' or 'spectator' will non-color filled
    the sample label 'data' will be drawn as doted points with error bars
    [2] stack :  this will produce a histogram (signal) and hstack with all the backround stacked, 
    as a third element a list of histogram with same order as in the hstack 
    [3] bkgadd : this add all the backgrounds in a same histogram, the function will then retrieve:
    the signal the spectator and background histogram
    
    options :
    options can be entred as a list:
    the list of options are : ['norm', '', ... ]
    """
    
    histos = {}
    hstack = ROOT.THStack()
    for proc in samples:
        flist = glob.glob( sampledir + '/*'+ samples[proc]['name'] +'*.root')
        roof  = ROOT.TFile.Open(flist[0])
        tree  = roof.Get(treename.replace('*',proc))
        tree.Project(
            'h_' + variable + variables[variable]['hist'],
            variable,
            selection
        )
        
        h = ROOT.gDirectory.Get('h_' + variable )
        h.SetDirectory(0)
        eventperbin = float(h.GetXaxis().GetXmax() - h.GetXaxis().GetXmin())/h.GetNbinsX()
        if 'signal' or 'spectator' in samples[proc]['label']:
            h.SetLineColor(samples[proc]['rootcolor'])
        else:
            h.SetFillColor(samples[proc]['rootcolor'])
            h.SetLineColor(ROOT.kBlack)
            h.SetTitle(";" + variables[variable]['title']+(";Entries/%1.1f"% eventperbin ))
        if 'norm' in options:
            integral = h.Integral()
            h.Scale(1.0/integral)
            h.GetYaxis().SetTitle("1/n dn/d"+variables[variable]['title'] +("/%1.1f" % eventperbin))

        if mode=='stack':
            if 'background' in samples[proc]['label']:
                hstack.Add(h);
            else:
                histos[variable].apprend(h)
            histos[variable].append(hstack)
        else :    
            histos[variable].append(h)        
        
    return histos;
