#!/usr/bin/python

import ROOT # needed
import os, sys, glob, sys, json, math 
import logging
from   rootpy.interactive import wait
from   collections import OrderedDict
import collections
from   jsmin              import jsmin
from   termcolor    import colored

samples     = collections.OrderedDict()
cutflow     = []
selection   = {}
plotlabels  = {}
variables   = {}

treename    = '*_13TeV_VBFDiJet'
sampledir   = '../data/output_data_rms_002/new/new/'

logging.basicConfig(format=colored('%(levelname)s:',attrs = ['bold'])
                    + colored('%(name)s:','blue') + ' %(message)s')
logger = logging.getLogger('heppi')
logger.setLevel(level=logging.DEBUG)


def draw_labels(label, position='tl', size=0.03):
    t = ROOT.TLatex()
    t.SetTextAlign(12);
    t.SetTextFont(42);
    t.SetTextSize(size);
    shift = 0;
    xpos  = 0;
    ypos  = 0;
    if position == 'tl': # top-left
        xpos = (0.10 + ROOT.gStyle.GetPadLeftMargin())
        ypos = (0.95 - ROOT.gStyle.GetPadTopMargin())
    if position == 'tr': # top-left
        xpos = (0.7  - ROOT.gStyle.GetPadRightMargin())
        ypos = (0.95 - ROOT.gStyle.GetPadTopMargin())
    if position == 'bl': # top-left
        xpos = (0.1  + ROOT.gStyle.GetPadLeftMargin())
        ypos = (0.2  + ROOT.gStyle.GetPadBottomMargin())
    if position == 'br': # top-left
        xpos = (0.65  - ROOT.gStyle.GetPadLeftMargin())
        ypos = (0.2   + ROOT.gStyle.GetPadBottomMargin())

    print 'labels ::' , label
    for s in label.split('\\'):
        t.DrawLatexNDC(xpos,ypos - shift,s)
        print 'shift', shift
        shift = shift + (size+0.005)

def draw2hist(hsig, hbkg, option ):
    if hsig.GetMaximum() > hbkg.GetMaximum():
        hsig.Draw(option )
        hbkg.Draw(option + ' same')
    else:
        hsig.Draw(option )
        hbkg.Draw(option + ' same')

def draw_point(x,y, size=0.01, color=121):

    point.Draw()

def draw_ROC(var ='dipho_dijet_MVA',
             label='VBF', title = 'variable',
             bkg = [], select='', categories=[]):
    #c = ROOT.TCanvas("c_ROC","ROC's BDT",600,600)
    #c.cd()
    histos = []
    histfilename = ('plots/histogram_stack_'  +
                    var + '_' + label + '_'
                    + selection['name'])
    cutflow = variable_cutflow(var,'')
    if len(cutflow)!=0:
        cutflow = variable_cutflow(var,select)
    # === define the stack
    hbkg = ROOT.TH1F('hbkg','',400,-1,1)
    hsig = ROOT.TH1F('hsig','',400,-1,1)
    hbkg.SetTitle(";" + variables[var]['title']+";entries")
    hsig.SetTitle(";" + variables[var]['title']+";entries")
    # === cutflow
    if len(cutflow)!=0 :
        cutflow = 'weight*(' + cutflow + ')'
    else:
        cutflow = 'weight'
        
    # === loop over the samples
    ordsam = OrderedDict(sorted(samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        #flist = glob.glob( sampledir + '/*'+ samples[proc]['name'] +'*.root')
        #roof  = ROOT.TFile.Open(flist[0])
        tree  = samples[proc].get('_root_tree_')#roof.Get(treename.replace('*',proc))
        histstr = '(%i,%f,%f)' %(int(400),-1, 1)
        tree.Project(
            'h_'+var + histstr,
            var,
            cutflow
        )
        if (samples[proc]['label']== 'background' or samples[proc]['label']== 'spectator' or samples[proc]['label']== 'Data') and proc in bkg:
            hbkg.Add(ROOT.gDirectory.Get('h_'+var))
        if samples[proc]['label']== 'signal':
            hsig.Add(ROOT.gDirectory.Get('h_'+var))
    
    hbkg.SetFillColorAlpha(122,0.6)
    hbkg.SetLineColor(1)
    hsig.SetLineColor(132)
    hsig.SetLineWidth(3)
    hbkg.GetYaxis().SetRangeUser(0,hbkg.GetMaximum() + hbkg.GetMaximum() * 0.5)
    
    roc   = ROOT.TGraph()
    roc.SetName ('fom_cat_'+label)
    roc.SetTitle(';#varepsilon_{bkg};#varepsilon_{sig}')
    catcut = []
    point = []
    cutpt = []
    roc.SetPoint (0,1,1)
    for ibin in range(0, hsig.GetNbinsX()+1):
        print hbkg.Integral() 
        beff = hbkg.Integral(ibin,hsig.GetNbinsX())/hbkg.Integral() 
        seff = hsig.Integral(ibin,hsig.GetNbinsX())/hsig.Integral()
        #print beff, '  ', seff
        for cat in categories:
            if abs(hsig.GetBinCenter(ibin)-cat) < 0.005 :
                print 'diff :: val(', hsig.GetBinCenter(ibin),') ',abs(hsig.GetBinCenter(ibin)-cat)
                p = ROOT.TEllipse(beff,seff,0.013,0.013)
                p.SetFillColor(2)
                p.SetLineWidth(0)
                p.SetLineColor(2)
                point.append(p)
        roc.SetPoint (ibin+1,beff,seff)
    roc.SetPoint (hsig.GetNbinsX()+2,0,0)
    roc.GetYaxis().SetLabelSize(0.032)
    roc.SetLineColor(132)
    roc.Draw('AL')
    roc.GetYaxis().SetRangeUser(0,1)
    roc.GetXaxis().SetRangeUser(0,1)
    roc.Draw('AL')
    c.Update()
    draw_labels("Integral = %1.3f" % (roc.Integral()+0.5),"bl",0.035)
    for p in point[:-1]:
        p.Draw()
    #c.SaveAs('plots/rocky_' + label + '.pdf')
    #c.SaveAs('plots/rocky_' + label + '.png')
    
    return roc

def read_plotcard(plotcard):
    global plotlabels
    global selection
    global variables
    global samples

    config = None
    with open(plotcard) as f:
        config = json.loads(jsmin(f.read()))
    for key in config:
        if 'selection' in key:
            logging.debug(' ---- book selections ---')
            print selection
            selection = config[key]
            logging.debug(' -- %12s %12s' % (key , selection['name']))
        if 'variables' in key:
            logger.info(' ---- book variables ----------')
            for var in config[key]:
                formula = var
                varname = var
                if ':=' in var:
                    varname  = var.split(':=')[0]
                    formula  = var.split(':=')[1]
                logger.info(' -- %20s  %15s' % (
                    varname ,
                    config[key][var]['hist']))
                variables[varname] = config[key][var]
                variables[varname].update({"formula":formula})
        if 'processes' in key:
            logger.info(' ---- book processes ----------')
            for proc in config[key]:
                samples[proc] = config[key][proc]
                logger.info(' -- %12s %12s' % (proc, samples[proc].get('cut','')))
        if 'labels' in key:
            logging.debug(' ------ book labels -----')
            print plotlabels
            plotlabels = config[key]
            logging.debug(' -- %12s %12s' % (key, plotlabels['name']))
        logging.debug(' -------------------')

def book_trees(select = ''):
    ordsam = OrderedDict(sorted(samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        chain      = ROOT.TChain(treename.replace('*',proc))
        if type(samples[proc].get('name')) == type([]):
            for sam in samples[proc].get('name',[]):
                for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
                    chain.Add(f)
        else:
            sam = samples[proc].get('name')
            for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
                chain.Add(f)
            
        # read systematic trees
        samples[proc].update({'_root_tree_'       : chain})
       
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
def GetBondaryBin(var ='dijet_BDT', label='VBF', select='', fom='', xmin=-1, xmax=1,catidx=0, nbin = 10000):
    histos = []
    histfilename = ('plots/histogram_stack_'  +
                    var + '_' + label + '_'
                    + selection['name'])
    legend  = ROOT.TLegend(0.55, 0.72,
                           (0.95 - ROOT.gStyle.GetPadRightMargin()),
                           (0.98 - ROOT.gStyle.GetPadTopMargin()))
    cutflow = variable_cutflow(var,'')
    if len(cutflow)!=0:
        cutflow = variable_cutflow(var,select)
    # === define the stack
    
    #hbkg = ROOT.TH1F('hbkg','',nbin,xmin,xmax)
    #hsig = ROOT.TH1F('hsig','',nbin,xmin,xmax)
    hbkg = ROOT.TH1F('hbkg','',nbin,-1,1)
    hsig = ROOT.TH1F('hsig','',nbin,-1,1)
    hbkg.SetTitle(";" + variables[var]['title']+";entries")
    hsig.SetTitle(";" + variables[var]['title']+";entries")
    # === cutflow
    if len(cutflow)!=0 :
        cutflow = 'weight*(' + cutflow + ('&& %s > %f' % (var, xmin)) + ('&& %s < %f' % (var, xmax)) + ')'
    else:
        cutflow = 'weight'
        
    # === loop over the samples
    ordsam = OrderedDict(sorted(samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        #flist = glob.glob( sampledir + '/*'+ samples[proc]['name'] +'*.root')
        #roof  = ROOT.TFile.Open(flist[0])
        tree  = samples[proc].get('_root_tree_')#roof.Get(treename.replace('*',proc))
        histstr = '(%i,%f,%f)' %(int(nbin),-1, 1)
        tree.Project(
            'h_'+var + histstr,
            var,
            cutflow
        )
        if samples[proc]['label']== 'background':
            hbkg.Add(ROOT.gDirectory.Get('h_'+var))
        if samples[proc]['label']== 'signal':
            hsig.Add(ROOT.gDirectory.Get('h_'+var))
            
            
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
    roc.SetTitle(';BDT_{output};Z(BDT_{output})')
    catcut = []
    for ibin in range(0, hsig.GetNbinsX()+1):
        Z  = 0
        if fom == 'signif':
            beff = hbkg.Integral(ibin,hsig.GetNbinsX())#hbkg.Integral() 
            seff = hsig.Integral(ibin,hsig.GetNbinsX())#/hsig.Integral()
            if (beff+seff) !=0 :
                Z = (seff*seff)/(beff+seff)
            else:
                Z = 0
        if fom == 'signif2':
            b = hbkg.Integral(ibin,hsig.GetNbinsX())#hbkg.Integral() 
            s = hsig.Integral(ibin,hsig.GetNbinsX())#/hsig.Integral()
            if (b+s) !=0 and b!=0:
                Z = 2*((s+b)*math.log((b+s)/b)-s) 
            else:
                Z = 0
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
    
    print 'category (',catidx,') boundary [',catvalue[0],'][',catvalue[1],']'
    draw_labels(('Category VBF-%i' % catidx)+ ' \\BDT > '+('%1.3f'%catvalue[0]))
    c.SaveAs('plots/fom_cat'+ str(catidx) + '.pdf')
    c.SaveAs('plots/fom_cat'+ str(catidx) + '.png')
    #raw_input("Press ENTER to continue ... ")
    return catvalue

if __name__ == "__main__":
    #for sam in ['gjet','qcd','dipho','ggh_125','Data','qcd+dipho+gjet']:
    #i in range(2,5):
    i = 3
    sampledir   = '../data/output_data_rms_00%i/new/new/'%i
    ROOT.gROOT.ProcessLine(".x .root/rootlogon.C")
    read_plotcard('config/plotcard_data_vbf.json')
    book_trees()
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    
    print_cutflow()
    
    #cat3 = GetBondaryBin('VBF', '','signif',-1,cat2 ,2)
    #cat3 = GetBondaryBin('VBF', '','signif',-1,cat2 ,2)
    cat1 = GetBondaryBin('combined_BDT', 'combined_BDT_cat', select='dipho_mass>123 && dipho_mass>127', fom='signif2', xmin=-1, xmax=1     ,catidx=0)
    cat2 = GetBondaryBin('combined_BDT', 'combined_BDT_cat', select='dipho_mass>123 && dipho_mass>127', fom='signif2', xmin=-1, xmax=cat1[0]  ,catidx=1)
    cat3 = GetBondaryBin('combined_BDT', 'combined_BDT_cat', select='dipho_mass>123 && dipho_mass>127', fom='signif2', xmin=-1, xmax=cat2[0]  ,catidx=2)
    #dijet_roc_ggf = draw_ROC(var   =  'dijet_BDT'     ,
    #                         label =  'dijetVBFMVA_ggf' ,
    #                         bkg   = ['ggf_m125'], categories=[])
    #
    #dijet_roc_ggf = draw_ROC(var   =  'dijet_BDT'     ,
    #                         label =  'dijetVBFMVA_allbkg' ,
    #                         bkg   = ['gamgamjetbox','gamJet','qcd','ggf_m125'], categories=[])
    
    
    #label = 'VBFMVA_%s_rmscut_00%i'%(sam, i)
    ##label = 'VBFMVA_qcd'
    ##label = 'VBFMVA_ggf'
    ##label = 'VBFMVA_gamgamjetbox'
    #
    ##label = 'dijetMVA_sm'
    #c = ROOT.TCanvas('c_Opt_'+label,'MVA',600,600)
    #c.cd()
    ##
    #legend  = ROOT.TLegend(0.55, 0.5,
    #                       (0.9 - ROOT.gStyle.GetPadRightMargin()),
    #                       (0.7 - ROOT.gStyle.GetPadTopMargin()))
    #legend.SetTextAlign( 12 )
    #legend.SetTextFont ( 42 )
    #legend.SetTextSize ( 0.03 )
    #legend.SetLineColor( 0 )
    #legend.SetFillColor( 0 )
    #legend.SetFillStyle( 0 )
    #legend.SetLineColorAlpha(0,0)
    #legend.SetShadowColor(0)
    #
    #
    #dijet_roc_ggf = draw_ROC(var   = 'dijet_BDT'     ,
    #                         label = 'dijetMVA_%s_rmscut_00%i' % (sam,i) , 
    #                         bkg   = [sam])
    ##combi_roc_ggf = draw_ROC(var   = 'combined_BDT'   ,
    ##                         label = 'dijetVBFMVA_gamjet' ,
    ##                         bkg   = ['gamJet'])
    ##                         #bkg   = ['gamgamjetbox'])
    ##                         #bkg   = ['ggf_m125'])
    ##                         #bkg   = ['qcd'])
    #
    #gmul = ROOT.TMultiGraph()
    #dijet_roc_ggf.SetLineColor(132)
    ##combi_roc_ggf.SetLineColor(121)
    #gmul.Add(dijet_roc_ggf)
    ##gmul.Add(combi_roc_ggf)
    #legend.AddEntry(dijet_roc_ggf,'dijet VBF MVA','l')
    ##legend.AddEntry(combi_roc_ggf,'combined VBF MVA','l')
    #gmul.SetTitle(';#varepsilon_{%s};#varepsilon_{VBF}'%sam)
    ##gmul.SetTitle(';#varepsilon_{#gamma#gamma};#varepsilon_{VBF}')
    ##gmul.SetTitle(';#varepsilon_{GGF};#varepsilon_{VBF}')
    ##gmul.SetTitle(';#varepsilon_{jet-jet};#varepsilon_{VBF}')
    #
    #gmul.Draw('AL')
    #gmul.GetYaxis().SetRangeUser(0,1)
    #gmul.GetXaxis().SetRangeUser(0,1)
    #gmul.GetYaxis().SetTitleOffset(1.25)
    #gmul.GetXaxis().SetTitleOffset(1.25)
    #gmul.Draw('AL')
    #c.Update()
    #legend.Draw()
    ##draw_labels("dijet-MVA : Integral = %1.3f\\com-MVA : Integral = %1.3f" % (dijet_roc_ggf.Integral()+0.5,combi_roc_ggf.Integral()+0.5),"br",0.035)
    #draw_labels("dijet-MVA : Integral = %1.3f\\RMS( |#eta|>2.5 ) < 0.0%i"% (dijet_roc_ggf.Integral()+0.5,i),"br",0.035)
    #c.SaveAs('plots/rocky_' + label + '.pdf')
    #c.SaveAs('plots/rocky_' + label + '.png')
    #raw_input()
            #
            #c.cd()
            #label = 'VBFMVA_JetJet'
            #legend  = ROOT.TLegend(0.55, 0.5,
            #                       (0.9 - ROOT.gStyle.GetPadRightMargin()),
            #                       (0.7 - ROOT.gStyle.GetPadTopMargin()))
            #legend.SetTextAlign( 12 )
            #legend.SetTextFont ( 42 )
            #legend.SetTextSize ( 0.03 )
            #legend.SetLineColor( 0 )
            #legend.SetFillColor( 0 )
            #legend.SetFillStyle( 0 )
            #legend.SetLineColorAlpha(0,0)
            #legend.SetShadowColor(0)
            #dijet_roc_smb = draw_ROC(var   = 'dijet_mva'       ,
            #                         label = 'dijetVBFMVA_smb' , 
            #                         bkg   = ['qcd'   ])#['gamgamjetbox'   ])
    #combi_roc_smb = draw_ROC(var   = 'dipho_dijet_MVA' ,
    #                         label = 'dijetVBFMVA_smb' ,
    #                         bkg   = ['qcd'])
    #gmul = ROOT.TMultiGraph()
    #dijet_roc_smb.SetLineColor(132)
    #combi_roc_smb.SetLineColor(121)
    #gmul.Add(dijet_roc_smb)
    #gmul.Add(combi_roc_smb)
    #legend.AddEntry(dijet_roc_smb,'dijet VBF MVA','l')
    #legend.AddEntry(combi_roc_smb,'combined VBF MVA','l')
    #gmul.SetTitle(';#varepsilon_{QCD};#varepsilon_{VBF}')
    #gmul.Draw('AL')
    #gmul.GetYaxis().SetRangeUser(0,1)
    #gmul.GetXaxis().SetRangeUser(0,1)
    #gmul.Draw('AL')
    #c.Update()
    #legend.Draw()
    #draw_labels("dijet-MVA : Integral = %1.3f\\com-MVA : Integral = %1.3f" % (dijet_roc_smb.Integral()+0.5,combi_roc_smb.Integral()+0.5),"br",0.035)
    #c.SaveAs('plots/rocky_' + label + '.pdf')
    #c.SaveAs('plots/rocky_' + label + '.png')
    #
    #label = 'VBFMVA_gamJet'
    #legend  = ROOT.TLegend(0.55, 0.5,
    #                       (0.9 - ROOT.gStyle.GetPadRightMargin()),
    #                       (0.7 - ROOT.gStyle.GetPadTopMargin()))
    #legend.SetTextAlign( 12 )
    #legend.SetTextFont ( 42 )
    #legend.SetTextSize ( 0.03 )
    #legend.SetLineColor( 0 )
    #legend.SetFillColor( 0 )
    #legend.SetFillStyle( 0 )
    #legend.SetLineColorAlpha(0,0)
    #legend.SetShadowColor(0)
    #dijet_roc_smb = draw_ROC(var   = 'dijet_mva'       ,
    #                         label = 'dijetVBFMVA_smb' , 
    #                         bkg   = ['gamJet'   ])#['gamgamjetbox'   ])
    #combi_roc_smb = draw_ROC(var   = 'dipho_dijet_MVA' ,
    #                         label = 'dijetVBFMVA_smb' ,
    #                         bkg   = ['gamJet'])
    #gmul = ROOT.TMultiGraph()
    #dijet_roc_smb.SetLineColor(132)
    #combi_roc_smb.SetLineColor(121)
    #gmul.Add(dijet_roc_smb)
    #gmul.Add(combi_roc_smb)
    #legend.AddEntry(dijet_roc_smb,'dijet VBF MVA','l')
    #legend.AddEntry(combi_roc_smb,'combined VBF MVA','l')
    #gmul.SetTitle(';#varepsilon_{#gamma-jet};#varepsilon_{VBF}')
    #gmul.Draw('AL')
    #gmul.GetYaxis().SetRangeUser(0,1)
    #gmul.GetXaxis().SetRangeUser(0,1)
    #gmul.Draw('AL')
    #c.Update()
    #legend.Draw()
    #draw_labels("dijet-MVA : Integral = %1.3f\\com-MVA : Integral = %1.3f" % (dijet_roc_smb.Integral()+0.5,combi_roc_smb.Integral()+0.5),"br",0.035)
    #c.SaveAs('plots/rocky_' + label + '.pdf')
    #c.SaveAs('plots/rocky_' + label + '.png')
    #
    #label = 'VBFMVA_gamgam'
    #legend  = ROOT.TLegend(0.55, 0.5,
    #                       (0.9 - ROOT.gStyle.GetPadRightMargin()),
    #                       (0.7 - ROOT.gStyle.GetPadTopMargin()))
    #legend.SetTextAlign( 12 )
    #legend.SetTextFont ( 42 )
    #legend.SetTextSize ( 0.03 )
    #legend.SetLineColor( 0 )
    #legend.SetFillColor( 0 )
    #legend.SetFillStyle( 0 )
    #legend.SetLineColorAlpha(0,0)
    #legend.SetShadowColor(0)
    #dijet_roc_smb = draw_ROC(var   = 'dijet_mva'       ,
    #                         label = 'dijetVBFMVA_smb' , 
    #                         bkg   = ['gamgamjetbox'   ])
    #combi_roc_smb = draw_ROC(var   = 'dipho_dijet_MVA' ,
    #                         label = 'dijetVBFMVA_smb' ,
    #                         bkg   = ['gamgamjetbox'   ])
    #gmul = ROOT.TMultiGraph()
    #dijet_roc_smb.SetLineColor(132)
    #combi_roc_smb.SetLineColor(121)
    #gmul.Add(dijet_roc_smb)
    #gmul.Add(combi_roc_smb)
    #legend.AddEntry(dijet_roc_smb,'dijet VBF MVA','l')
    #legend.AddEntry(combi_roc_smb,'combined VBF MVA','l')
    #gmul.SetTitle(';#varepsilon_{#gamma-#gamma};#varepsilon_{VBF}')
    #gmul.Draw('AL')
    #gmul.GetYaxis().SetRangeUser(0,1)
    #gmul.GetXaxis().SetRangeUser(0,1)
    #gmul.Draw('AL')
    #c.Update()
    #legend.Draw()
    #draw_labels("dijet-MVA : Integral = %1.3f\\com-MVA : Integral = %1.3f" % (dijet_roc_smb.Integral()+0.5,combi_roc_smb.Integral()+0.5),"br",0.035)
    #c.SaveAs('plots/rocky_' + label + '.pdf')
    #c.SaveAs('plots/rocky_' + label + '.png')
    ##draw_ROC(var = 'dipho_dijet_MVA' , label = 'combinedVBFMVA', title = 'combined MVA', select = '')
    #
    #
    #label = 'VBFMVA_dy'
    #legend  = ROOT.TLegend(0.55, 0.5,
    #                       (0.9 - ROOT.gStyle.GetPadRightMargin()),
    #                       (0.7 - ROOT.gStyle.GetPadTopMargin()))
    #legend.SetTextAlign( 12 )
    #legend.SetTextFont ( 42 )
    #legend.SetTextSize ( 0.03 )
    #legend.SetLineColor( 0 )
    #legend.SetFillColor( 0 )
    #legend.SetFillStyle( 0 )
    #legend.SetLineColorAlpha(0,0)
    #legend.SetShadowColor(0)
    #dijet_roc_smb = draw_ROC(var   = 'dijet_mva'       ,
    #                         label = 'dijetVBFMVA_smb' , 
    #                         bkg   = ['dy_toll_m50'   ])
    #combi_roc_smb = draw_ROC(var   = 'dipho_dijet_MVA' ,
    #                         label = 'dijetVBFMVA_smb' ,
    #                         bkg   = ['dy_toll_m50'   ])
    #gmul = ROOT.TMultiGraph()
    #dijet_roc_smb.SetLineColor(132)
    #combi_roc_smb.SetLineColor(121)
    #gmul.Add(dijet_roc_smb)
    #gmul.Add(combi_roc_smb)
    #legend.AddEntry(dijet_roc_smb,'dijet VBF MVA','l')
    #legend.AddEntry(combi_roc_smb,'combined VBF MVA','l')
    #gmul.SetTitle(';#varepsilon_{Drell-Yann};#varepsilon_{VBF}')
    #gmul.Draw('AL')
    #gmul.GetYaxis().SetRangeUser(0,1)
    #gmul.GetXaxis().SetRangeUser(0,1)
    #gmul.Draw('AL')
    #c.Update()
    #legend.Draw()
    #draw_labels("dijet-MVA : Integral = %1.3f\\com-MVA : Integral = %1.3f" % (dijet_roc_smb.Integral()+0.5,combi_roc_smb.Integral()+0.5),"br",0.035)
    #c.SaveAs('plots/rocky_' + label + '.pdf')
    #c.SaveAs('plots/rocky_' + label + '.png')
    #draw_ROC(var = 'dipho_dijet_MVA' , label = 'combinedVBFMVA', title = 'combined MVA', select = '')


    
