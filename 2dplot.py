#!/usr/bin/python

import ROOT # needed
import os, sys, glob, sys, json
import logging
from   rootpy.tree import Cut  # more robust
import colors 
from   rootpy.interactive import wait
import collections
from   collections import OrderedDict

samples     = collections.OrderedDict()
variables   = {}
rootfile    = {}
cutflow     = [] ## save all the cuts
selection   = {}
plotlabels  = {}
# delete me
sampledir   = './data/new' ## temp variable
treename    = 'vbfTagDumper/trees/*_13TeV_VBFDiJet'
#treename    = '*_13TeV_VBFDiJet'
options     = None   
allnormhist = False
treeinfo    = {}


# ---- plot card
def read_plotcard(plotcard):
    global plotlabels
    global selection
    global variables
    global samples
    global treeinfo
    
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
                samples[proc] = config[key][proc]
                logging.debug(' -- %12s %12s' % (key, samples[proc]['name']))
        if 'selection' in key:
            logging.debug(' ---- book selections ---')
            print selection
            selection = config[key]
            logging.debug(' -- %12s %12s' % (selection['name'], selection['title']))
            
        if 'labels' in key:
            logging.debug(' ------ book labels -----')
            print plotlabels
            plotlabels = config[key]
            logging.debug(' -- %12s %12s' % (key, plotlabels['name']))
        if 'tree' in key:
            treeinfo = config[key]
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
    print cutflow
    return cutflow

def print_cutflow():
    for var in variables:
        if (len(variables[var]['cut'])!=0):
            print ('-- %20s: %12s' % (var, variables[var]['cut'] ) )


def draw_cut_line(hist, variable=''):
    if variables[variable]['cut']!='':
        ymin = hist.GetMinimum()
        ymax = hist.GetMaximum()
        cuttt = variables[variable]['cut'].replace('(','').replace(')','')
        for cut in  cuttt.split('&&'):
            stmp = cut.split('>')
            if len(stmp) == 1:
                stmp = cut.split('<')
            xcut = float(stmp[1])
            line = ROOT.TLine()
            line.SetLineColor(134)
            line.SetLineStyle(7)
            if xcut > hist.GetXaxis().GetXmin() or xcut < hist.GetXaxis().GetXmax(): 
                line.DrawLine(xcut,ymin,xcut,ymax)

                
def draw_labels(label):
    t = ROOT.TLatex()
    t.SetTextAlign(12);
    t.SetTextFont(42);
    t.SetTextSize(0.025);
    shift = 0;
    print 'labels ::' , label 
    for s in label.split('\\'):
        t.DrawLatexNDC((0.1       + ROOT.gStyle.GetPadLeftMargin()),
                       (0.95 - shift - ROOT.gStyle.GetPadTopMargin()),s)
        shift = shift + 0.03
# ---- draw norm histograms
def draw_2d(variable, label='VBF', select=''):
    histos = []
    formula = variable
    varname = variable
    if ':=' in variable:
        varname  = variable.split(':=')[0]
        formula  = variable.split(':=')[1]
    print '\t formula::', formula
    print '\t varname::', varname

    histfilename = ('plots/histogram_stack_' +
                    varname + '_' + label+ '_'
                    + selection['name'])
    legend  = ROOT.TLegend(0.55, 0.72,
                           (0.95 - ROOT.gStyle.GetPadRightMargin()),
                           (0.98 - ROOT.gStyle.GetPadTopMargin()))
    cutflow = variable_cutflow(variable,'')
    if len(cutflow)!=0:
        cutflow = variable_cutflow(variable,select)
    # define the stack
    hstack = ROOT.THStack('hs_' + varname,'')
    hstack.SetName('hs_'+ varname)
    hstack.SetTitle(";" + variables[variable]['title']+";entries")
    # cutflow
            
    if len(cutflow)!=0 and options.nocuts==False:
        cutflow = ('weight*%f*('% treeinfo['lumifactor']) + cutflow + ')'
    else:
        cutflow = ('weight*%f'  % treeinfo['lumifactor'])
    if  options.nocuts:
        histfilename = histfilename + '_nocuts'
    # loop over the samples
    ordsam = OrderedDict(sorted(samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        logging.debug(' -- %17s  %12s ' % (proc,  samples[proc]['name']))
        flist = glob.glob( sampledir + '/*'+ samples[proc]['name'] +'*.root')
        print 'list of file::', flist
        roof  = ROOT.TFile.Open(flist[0])
        tree  = roof.Get(treename.replace('*',proc))
        print 'histo ::', samples[proc]['name']
        print '..tree::', tree.GetEntries()
        tree.Project(
            'h_' + varname + variables[variable]['hist'],
            formula,
            cutflow
        )
        hist = ROOT.gDirectory.Get('h_' + varname )
        hist.SetDirectory(0)
        # histogram color
        hist.SetTitle(";" + variables[variable]['title']+";entries")
        hcolor = 1
        print 'colors.usercolor::',colors.usercolor
        #for c in colors.usercolor:
        #    if c in samples[proc]['color']:
        hcolor = samples[proc]['color']
        if ('signal'==samples[proc]['label']) or ('spectator'==samples[proc]['label']):
            hist.SetLineColor(hcolor)
            hist.SetLineStyle(1)
            hist.SetLineWidth(2)
            hist.SetFillStyle(0)
            histos.append(hist)
            legend.AddEntry( hist, samples[proc]["title"], "l" );
        else:
            hist.SetLineColor(ROOT.kBlack)
            hist.SetFillColor(hcolor)
            hist.SetLineWidth(2)
            hstack.Add(hist)
            legend.AddEntry( hist, samples[proc]["title"], "f" );
    # drawing
    c = ROOT.TCanvas('c_'+varname,variable,600,700)
    c.cd()
    htmp = histos[0].Clone('htmp')
    htmp.SetTitle(";" + variables[variable]['title']+";entries")
    htmp.Clear()
    if  options.allloghist:
        ymin = 0.001
        ymax = hstack.GetMaximum()*1000
        htmp.GetYaxis().SetRangeUser(ymin,ymax)
        histfilename = histfilename + '_log'
        ROOT.gPad.SetLogy()
    else:
        ymin = 0
        ymax = hstack.GetMaximum() + hstack.GetMaximum()*0.5
        htmp.GetYaxis().SetRangeUser(ymin,ymax)
    htmp.Draw()
    hstack.Draw('hist,same')
    for h in histos:
        h.Draw('hist,same')
    # cosmetics
    draw_cut_line(htmp,variable)
    ROOT.gPad.RedrawAxis();
    # this is for the legend
    legend.SetTextAlign( 12 )
    legend.SetTextFont ( 42 )
    legend.SetTextSize ( 0.025 )
    legend.SetLineColor( 0 )
    legend.SetFillColor( 0 )
    legend.SetFillStyle( 0 )
    legend.SetLineColorAlpha(0,0)
    legend.SetShadowColor(0)
    legend.Draw()
    # draw a line
    
    # draw labels
    if  options.nocuts:
        draw_labels('w/o cuts')
    else:
        draw_labels(plotlabels['name'])
    if variables[variable]['norm']==True or allnormhist==True:
        histfilename = histfilename + '_norm'
    c.SaveAs( histfilename + '.png')
    c.SaveAs( histfilename + '.pdf')
    
    #htmp.Delete()
#------------------------------------
#         main function 
#------------------------------------
from optparse import OptionParser

def get_options():
    parser = OptionParser()
    parser.add_option("-r", "--load", dest="plotcard",default='plotcard.json',
                      help="""
                      Load the plot card in json format, 
                      please use ./makeplotcard.py to create one
                      """,
                      metavar="FILE")
    
    parser.add_option("-s", "--sampledir", dest="sampledir",default='./data/',
                      help="""
                      specify the detrectory where the trees are. 
                      example: --filedir /data/trees
                      """,
                      metavar="FILE")
    
    parser.add_option("-t", "--tree", dest="treename",default='vbfTagDumper/trees/*VBFDiJet',
                      help="dumper tree that you want to use", metavar="FILE")
    parser.add_option("-a", "--all", 
                      action="store_true", dest="draw_all", default=False,
                      help="draw all the variables specified in the plotcard")
    parser.add_option("-d", "--display", 
                      action="store_true", dest="display", default=False,
                      help="draw all the variables specified in the plotcard")
    parser.add_option("-v", "--variable",
                      dest="variable",default="dijet_leadPt",
                      help="name of the variable you want to draw")
    parser.add_option("-n", "--allnorm",
                      action="store_true",dest="allnormhist",default=False,
                      help="all the histogram will be normilised")
    parser.add_option("-l", "--alllog",
                      action="store_true",dest="allloghist",default=False,
                      help="all the histogram will be in log scale")
    parser.add_option("--nocuts",
                      action="store_true",dest="nocuts",default=False,
                      help="all the histogram will be in log scale")
    parser.add_option("--label", dest="label",default='VBF',
                      help="label to the produced plots")

    return parser.parse_args()

if __name__ == "__main__":
    (opt, args) = get_options()
    options  = opt
    if opt.display :
        ROOT.gROOT.SetBatch(ROOT.kTRUE) 
    # reading the plotcard from json
    # logging.basicConfig(level=options.loglevel
    allnormhist = options.allnormhist
    allloghist  = options.allloghist
    sampledir   = options.sampledir
    #treename    = options.treename
    ROOT.gROOT.ProcessLine(".x ~/.rootsys/rootlogon.C")
    read_plotcard(options.plotcard)
    if not options.display:
        ROOT.gROOT.SetBatch(ROOT.kTRUE)
    #colors.declar_color()
    #ROOT.gROOT.ProcessLine(".x .color-for-root.C")
    print_cutflow()
    
    print 'test::', selection
    for var in variables:
        draw_instack(var,options.label,selection['title'])
        
    #hist = produce_histos('jet1_pt','',['norm'],'')
    #print 'voila ::',hist
