#!/usr/bin/python

import ROOT # needed
import os, sys, glob, sys, json
import logging
from   rootpy.interactive import wait
from   collections import OrderedDict
import collections

samples     = collections.OrderedDict()
cutflow     = []
selection   = {}
plotlabels  = {}
variables   = {}

treename    = 'vbfTagDumper/trees/*_13TeV_VBFDiJet'
sampledir   = '../../data/output_vbfDumper_cfg_standard_dijet/merged/' ## temp variable
def draw_labels(label, position='tl', size=0.035):    
    t = ROOT.TLatex()
    t.SetTextAlign(12);
    t.SetTextFont(42);
    t.SetTextSize(size);
    shift = 0;
    xpos  = 0;
    ypos  = 0;
    if position == 'tl': # top-left
        xpos = (0.1  + ROOT.gStyle.GetPadLeftMargin())
        ypos = (0.95 - ROOT.gStyle.GetPadTopMargin())
    if position == 'tr': # top-left
        xpos = (0.7  - ROOT.gStyle.GetPadRightMargin())
        ypos = (0.95 - ROOT.gStyle.GetPadTopMargin())
    if position == 'bl': # top-left
        xpos = (0.1  + ROOT.gStyle.GetPadLeftMargin())
        ypos = (0.2  + ROOT.gStyle.GetPadBottomMargin())
    if position == 'br': # top-left
        xpos = (0.7  - ROOT.gStyle.GetPadLeftMargin())
        ypos = (0.2  + ROOT.gStyle.GetPadBottomMargin())

    print 'labels ::' , label 
    for s in label.split('\\'):
        t.DrawLatexNDC(xpos,ypos - shift,s)
        print 'shift', shift
        shift = shift + 1.2*size

def read_plotcard(plotcard):
    global plotlabels
    global selection
    global variables
    global samples
    config = json.loads(open(plotcard).read())
    for key in config:
        if 'selection' in key:
            logging.debug(' ---- book selections ---')
            print selection
            selection = config[key]
            logging.debug(' -- %12s %12s' % (key , selection['name']))
        if 'variables' in key:
            for var in config[key]:
                variables[var] = config[key][var]
        if 'processes' in key:
            logging.debug(' ---- book processes ----')
            for proc in config[key]:
                samples[proc] = config[key][proc]
                logging.debug(' -- %12s %12s' % (key, samples[proc]['name']))
        if 'labels' in key:
            logging.debug(' ------ book labels -----')
            print plotlabels
            plotlabels = config[key]
            logging.debug(' -- %12s %12s' % (key, plotlabels['name']))
        logging.debug(' -------------------')
# ---- create a cut flow except the considered variables
def variable_cutflow(variable, select=''):
    cutflow = ''
    for var in variables:
        if (len(variables[var]['cut'])!=0) and (var!=variable):
            #logging.debug('-- %12s: %12s' % (variable, variables[var]['cut'] ) )
            if len(cutflow)==0:
                cutflow = '(' + variables[var]['cut'] + ')'
            else:
                cutflow = cutflow + '&&' + '(' + variables[var]['cut'] + ')'
                
    if select != '':
        cutflow = cutflow + '&&' + select
    
    return cutflow
#---------------------------------------------------------------
def print_cutflow():
    for var in variables:
        if (len(variables[var]['cut'])!=0):
            print ('-- %20s: %12s' % (var, variables[var]['cut'] ) )

#---------------------------------------------------------------
def GetBondaryBin(label='VBF', select='', fom='', xmin=-1, xmax=1,catidx=0):
    histos = []
    histfilename = ('plots/histogram_stack_'  +
                    'dijet_MVA' + '_' + label + '_'
                    + selection['name'])
    legend  = ROOT.TLegend(0.55, 0.72,
                           (0.95 - ROOT.gStyle.GetPadRightMargin()),
                           (0.98 - ROOT.gStyle.GetPadTopMargin()))
    cutflow = variable_cutflow('dijet_MVA','')
    if len(cutflow)!=0:
        cutflow = variable_cutflow('dijet_MVA',select)
    # === define the stack
    hbkg = ROOT.TH1F('hbkg','',200,xmin,xmax)
    hsig = ROOT.TH1F('hsig','',200,xmin,xmax)
    hbkg.SetTitle(";" + variables['dijet_MVA']['title']+";entries")
    hsig.SetTitle(";" + variables['dijet_MVA']['title']+";entries")
    # === cutflow
    if len(cutflow)!=0 :
        cutflow = 'weight*(' + cutflow + ')'
    else:
        cutflow = 'weight'
        
    # === loop over the samples
    ordsam = OrderedDict(sorted(samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        flist = glob.glob( sampledir + '/*'+ samples[proc]['name'] +'*.root')
        roof  = ROOT.TFile.Open(flist[0])
        tree  = roof.Get(treename.replace('*',proc))
        histstr = '(%i,%f,%f)' %(int(200),xmin, xmax)
        tree.Project(
            'h_dijet_MVA' + histstr,
            'dijet_MVA',
            cutflow
        )
        if samples[proc]['label']== 'background':
            hbkg.Add(ROOT.gDirectory.Get('h_dijet_MVA'))
        if samples[proc]['label']== 'signal':
            hsig.Add(ROOT.gDirectory.Get('h_dijet_MVA'))
            
            
    c = ROOT.TCanvas('c_Opt'+str(catidx),'MVA',600,700)
    c.cd()
    hbkg.SetFillColorAlpha(122,0.6)
    hbkg.SetLineColor(1)
    hsig.SetLineColor(132)
    hsig.SetLineWidth(3)
    hbkg.GetYaxis().SetRangeUser(0,hbkg.GetMaximum() + hbkg.GetMaximum() * 0.5)
    #ROOT.gPad.SetLogy()
    #hbkg.Draw('hist')
    #hsig.Draw('hist,same')
    roc   = ROOT.TGraph()
    roc.SetName ('fom_cat_' + str(catidx)+label)
    roc.SetTitle(';BDT_{output};fom')
    catcut = []
    for ibin in range(0, hsig.GetNbinsX()+1):
        if fom == 'signif':
            beff = hbkg.Integral(ibin,hsig.GetNbinsX())#/hbkg.Integral() 
            seff = hsig.Integral(ibin,hsig.GetNbinsX())#/hsig.Integral()
            Z  = 0
            if (beff+seff) !=0 :
                Z = 2.11*(seff*seff)/(beff+seff)/10.0 
            catcut.append([float(hbkg.GetBinCenter(ibin)),Z])
            roc.SetPoint (ibin,hbkg.GetBinCenter(ibin),Z)
    
    catvalue = max(catcut, key=lambda item: (item[1]))
    roc.GetYaxis().SetLabelSize(0.032)
    roc.SetLineColor(132)
    roc.Draw('AL')
    roc.GetYaxis().SetRangeUser(0,catvalue[1] + catvalue[1]*0.5)
    roc.GetXaxis().SetRangeUser(-1,1)
    roc.Draw('AL')
    c.Update()
    line = ROOT.TLine()
    line.SetLineColor(134)
    line.SetLineStyle(7)
    line.DrawLine(catvalue[0],0,catvalue[0],catvalue[1])
    
    print 'category (',catidx,') boundary [',catvalue[0],']'
    draw_labels(('fom = s^{2}/(s+b)\\  \\Category VBF-%i' % catidx)+ ' \\BDT > '+('%1.3f'%catvalue[0]))
    c.SaveAs('plots/fom_cat'+ str(catidx) + '.pdf')
    c.SaveAs('plots/fom_cat'+ str(catidx) + '.png')
    #raw_input("Press ENTER to continue ... ")
    return catvalue[0]

if __name__ == "__main__":
    ROOT.gROOT.ProcessLine(".x ~/.rootsys/rootlogon.C")
    read_plotcard('config/vbf_plotcard_allbkg_just_for_catopt.json')
    #ROOT.gROOT.SetBatch(ROOT.kTRUE)
    
    print_cutflow()
    cat1 = GetBondaryBin('VBF', '','signif',-1,1    ,0)
    cat2 = GetBondaryBin('VBF', '','signif',-1,cat1 ,1)
    #cat3 = GetBondaryBin('VBF', '','signif',-1,cat2 ,2)
    #cat3 = GetBondaryBin('VBF', '','signif',-1,cat2 ,2)
    
