#!/usr/bin/python
import ROOT  # needed
from   heppi import heppi
from   collections        import OrderedDict
import os, sys, glob, sys, json, re, logging, collections, math
from   termcolor    import colored
import numpy
from   progressbar  import ProgressBar, Bar, Percentage, ETA

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
        
def draw_point(x,y, size=0.01, color=121):
    point.Draw()

def draw_ROC(var ='dipho_dijet_MVA',
             label='VBF', title = 'variable', axistitle='',
             bkg = None, select='', categories=None):
    #c = ROOT.TCanvas("c_ROC","ROC's BDT",600,600)
    #c.cd()
    if bkg is None:
        bkg = []
    if categories is None:
        categories = []
    histos = []
    histfilename = ('plots/histogram_stack_'  +
                    var + '_' + label + '_'
                    + heppi.selection['name'])
    cutflow = heppi.variable_cutflow(var,'')
    if len(cutflow)!=0:
        cutflow = heppi.variable_cutflow(var,select)
    # === define the stack
    hbkg = ROOT.TH1F('hbkg','',400,-1,1)
    hsig = ROOT.TH1F('hsig','',400,-1,1)
    hbkg.SetTitle(";" + heppi.variables[var]['title']+";entries")
    hsig.SetTitle(";" + heppi.variables[var]['title']+";entries")
    # === cutflow
    if len(cutflow)!=0 :
        cutflow = 'weight*(' + cutflow + ')'
    else:
        cutflow = 'weight'
    
    # === loop over the samples
    ordsam = OrderedDict(sorted(heppi.samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        tree  = heppi.samples[proc].get('_root_tree_')#roof.Get(treename.replace('*',proc))
        histstr = '({0:d},{1:f},{2:f})'.format(int(400), -1, 1)
        if proc == 'Data':
            cutflow = cutflow.replace('weight*','').replace('weight','')
            
        tree.Project(
            'h_'+var + histstr,
            var,
            cutflow
        )
        if heppi.samples[proc]['label']!= 'Signal' and proc in bkg:
            print '--> have ', proc
            hbkg.Add(ROOT.gDirectory.Get('h_'+var))
        if heppi.samples[proc]['label']== 'signal':
            hsig.Add(ROOT.gDirectory.Get('h_'+var))
    
    hbkg.SetFillColorAlpha(122,0.6)
    hbkg.SetLineColor(1)
    hsig.SetLineColor(132)
    hsig.SetLineWidth(3)
    hbkg.GetYaxis().SetRangeUser(0,hbkg.GetMaximum() + hbkg.GetMaximum() * 0.5)
    
    roc   = ROOT.TGraph()
    roc.SetName ('fom_cat_'+label)
    roc.SetTitle( axistitle )
    catcut = []
    point = []
    cutpt = []
    roc.SetPoint (0,1,1)
    for ibin in range(0, hsig.GetNbinsX()+1):
        #print hbkg.Integral() 
        beff = hbkg.Integral(ibin,hsig.GetNbinsX())/hbkg.Integral() 
        seff = hsig.Integral(ibin,hsig.GetNbinsX())/hsig.Integral()
        #print beff, '  ', seff
        for cat in categories:
            if abs(hsig.GetBinCenter(int(ibin))-cat) < 0.005 :
                print 'diff :: val(', hsig.GetBinCenter(ibin),') ',abs(hsig.GetBinCenter(int(ibin))-cat)
                p = ROOT.TEllipse(beff,seff,0.013,0.013)
                p.SetFillColor(2)
                p.SetLineWidth(0)
                p.SetLineColor(2)
                point.append(p)
        roc.SetPoint (ibin+1,beff,seff)
    roc.SetPoint (hsig.GetNbinsX()+2,0,0)
    #roc.GetYaxis().SetLabelSize(25)
    roc.GetYaxis().SetTitleSize(25)
    roc.GetXaxis().SetTitleSize(25)
    roc.GetYaxis().SetTitleOffset (1)
    roc.GetXaxis().SetTitleOffset (1)
    roc.SetLineColor(129)
    roc.SetLineWidth(3)
    #roc.Draw('AL')
    roc.GetYaxis().SetRangeUser(0,1)
    roc.GetXaxis().SetRangeUser(0,1)
    #roc.Draw('AL')
    
    #c.Update()
    #
    #draw_labels("Integral = %1.3f" % (roc.Integral()+0.5),"bl",0.035)
    #for p in point[:-1]:
    #    p.Draw()
    ##raw_input()
    #c.SaveAs('plots/rocky_' + label + '.pdf')
    #c.SaveAs('plots/rocky_' + label + '.png')
    
    return roc
# ---- create a cut flow except the considered variables
def variable_cutflow(variable, select=''):
    cutflow = ''
    for var in heppi.variables:
        if (len(heppi.variables[var]['cut'])!=0) and (var!=variable):
            #logging.debug('-- %12s: %12s' % (variable, variables[var]['cut'] ) )
            if len(cutflow)==0:
                cutflow = '(' + heppi.variables[var]['cut'] + ')'
            else:
                cutflow = cutflow + '&&' + '(' + heppi.variables[var]['cut'] + ')'
                
    if select != '':
        cutflow = cutflow + '&&' + select
    
    return cutflow
#---------------------------------------------------------------
def GetBondaryBin(var    = 'dijet_BDT',
                  label  = 'VBF',
                  select = '',
                  fom    = '',
                  xmin   =-1,
                  xmax   = 1,
                  catidx = 0,
                  nbin = 10000):
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
    hbkg = ROOT.TH1F('hbkg','',nbin,-1,1)
    hsig = ROOT.TH1F('hsig','',nbin,-1,1)
    hbkg.SetTitle(";" + heppi.variables[var]['title']+";entries")
    hsig.SetTitle(";" + heppi.variables[var]['title']+";entries")
    # === cutflow
    if len(cutflow)!=0 :
        cutflow = 'weight*(' + cutflow + ('&& {0!s} > {1:f}'.format(var, xmin)) + ('&& {0!s} < {1:f}'.format(var, xmax)) + ')'
    else:
        cutflow = 'weight'
        
    # === loop over the samples
    ordsam = OrderedDict(sorted(heppi.samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        tree  = heppi.samples[proc].get('_root_tree_')#roof.Get(treename.replace('*',proc))
        histstr = '({0:d},{1:f},{2:f})'.format(int(nbin), -1, 1)
        tree.Project(
            'h_'+var + histstr,
            var,
            cutflow
        )
        if heppi.samples[proc]['label']== 'background':
            hbkg.Add(ROOT.gDirectory.Get('h_'+var))
        if heppi.samples[proc]['label']== 'signal':
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
    
    if len(cutflow)!=0 :
        cutflow = 'weight*(' + cutflow + ('&& {0!s} > {1:f}'.format(var, xmin)) + ('&& {0!s} < {1:f}'.format(var, xmax)) + ')'
    else:
        cutflow = 'weight'

    bar    = ProgressBar(widgets=[colored('-- variables:: {0:20!s}   '.format(variable), 'green'),
                                  Percentage(),'  ' ,Bar('>'), ' ', ETA()], term_width=100)
    for ibin in bar(range(0, hsig.GetNbinsX()+1)):
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
        catcut.append([float(hbkg.GetBinCenter(int(ibin))),Z])
        roc.SetPoint (ibin,hbkg.GetBinCenter(int(ibin)),Z)
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
    draw_labels(('Category VBF-{0:d}'.format(catidx))+ ' \\BDT > '+('{0:1.3f}'.format(catvalue[0])))
    c.SaveAs('plots/fom_cat'+ str(catidx) + '.pdf')
    c.SaveAs('plots/fom_cat'+ str(catidx) + '.png')
    return catvalue




def significance(hs, hb, bounds=None):
    if bounds is None:
        bounds = [0.5]
    bounds.append(hs.GetXaxis().GetXmax())
    bounds.sort()
    w  = (hs.GetXaxis().GetXmax() - hs.GetXaxis().GetXmin())/float(hs.GetNbinsX())
    Z  = 0
    for icat in range(0,len(bounds)-1):
        curr_bounds = int((bounds[icat  ] - hs.GetXaxis().GetXmin())/w)
        next_bounds = int((bounds[icat+1] - hs.GetXaxis().GetXmin())/w)
        b  = hb.Integral(curr_bounds,next_bounds)#/float(hb.Integral())
        s  = hs.Integral(curr_bounds,next_bounds)#/float(hs.Integral())
        if (b) !=0 and (s+b)>5:
            Z += (s*s)/b
            #Z += (s*s)/(b+s)
    return Z



def GetCategoryBounds(var    = 'dijet_BDT',
                      label  = 'VBF',
                      selection = '',
                      xmin   =-1,
                      xmax   = 1,
                      ncat   = 2,
                      smooth_index = 2,
                      nbin = 10000):
    histos = []
    legend  = ROOT.TLegend(0.55, 0.72,
                           (0.95 - ROOT.gStyle.GetPadRightMargin()),
                           (0.98 - ROOT.gStyle.GetPadTopMargin()))
    
    
    # === define the stack
    hbkg = ROOT.TH1F('hbkg','',nbin,-1,1)
    hsig = ROOT.TH1F('hsig','',nbin,-1,1)
    hbkg.SetTitle(";" + heppi.variables[var]['title']+";entries")
    hsig.SetTitle(";" + heppi.variables[var]['title']+";entries")
    # === cutflow
    cutflow = variable_cutflow(var,selection)
    if len(cutflow)!=0 :
        cutflow = 'weight*(' + cutflow + ')'
    else:
        cutflow = 'weight'
        
    # === fill hitograms
    ordsam = OrderedDict(sorted(heppi.samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        tree  = heppi.samples[proc].get('_root_tree_')#roof.Get(treename.replace('*',proc))
        histstr = '({0:d},{1:f},{2:f})'.format(int(nbin), -1, 1)
        tree.Project(
            'h_'+var + histstr,
            var,
            cutflow
        )
        if heppi.samples[proc]['label']== 'background':
            hbkg.Add(ROOT.gDirectory.Get('h_'+var))
        if heppi.samples[proc]['label']== 'signal':
            hsig.Add(ROOT.gDirectory.Get('h_'+var))
        
            
    hbkg.SetFillColorAlpha(122,0.6)
    hbkg.SetLineColor(1)
    hsig.SetLineColor(132)
    hsig.SetLineWidth(3)
    hbkg.GetYaxis().SetRangeUser(0,hbkg.GetMaximum() + hbkg.GetMaximum() * 0.5)
    
    catcut = []
    h_phaseSpace = ROOT.TH2F('h_phaseSpace',';C_{0};C_{1};z^{2}', nbin, -1,1, nbin,-1,1)
    bar    = ProgressBar(widgets=[colored('-- bounds scan :: ', 'red'),
                                  Percentage(),'  ' ,Bar('>'), ' ', ETA()], term_width=100)

    
    hsig.Smooth(smooth_index)
    hbkg.Smooth(smooth_index)
    h_roc_sig = ROOT.TH2F('h_roc_sig',';mva_{0};mva_{1};z^{2}', nbin, -1,1, nbin,-1,1)
    h_roc_bkg = ROOT.TH2F('h_roc_bkg',';mva_{0};mva_{1};z^{2}', nbin, -1,1, nbin,-1,1)
    for ibin in bar(range(0, hsig.GetNbinsX()+1)):
        for jbin in range(0, hsig.GetNbinsX()+1):
            if (jbin > ibin): continue
            z = significance(hsig, hbkg,
                             bounds = [
                                 hsig.GetBinCenter(ibin),
                                 hsig.GetBinCenter(jbin)
                             ])
            h_roc_sig.SetBinContent(ibin,jbin,hsig.Integral(ibin,hsig.GetNbinsX()+1)*hbkg.Integral(ibin,hbkg.GetNbinsX()+1))
            catcut.append([[float(hbkg.GetBinCenter(ibin)), float(hbkg.GetBinCenter(jbin))],z])
            h_phaseSpace.SetBinContent(ibin,jbin,z)
            
    opt_bounds = max(catcut, key=lambda item: (item[1]))
    maxfrom_h  = h_phaseSpace.GetMaximum()
    
    #opt_bounds = min(catcut, key=lambda item: (item[1]))
    #roc.GetYaxis().SetLabelSize(0.032)
    #roc.SetLineColor(132)
    
    c = ROOT.TCanvas('c_boundary_optimisation','MVA',600,600)
    c.cd()
    h_phaseSpace.GetYaxis().SetTitleSize(25)
    h_phaseSpace.GetXaxis().SetTitleSize(25)
    h_phaseSpace.GetYaxis().SetTitleOffset (1)
    h_phaseSpace.GetXaxis().SetTitleOffset (1)
    h_phaseSpace.GetXaxis().SetRangeUser(opt_bounds[0][0] - 0.1, opt_bounds[0][0] + 0.1)
    h_phaseSpace.GetYaxis().SetRangeUser(opt_bounds[0][1] - 0.1, opt_bounds[0][1] + 0.1)
    #h_phaseSpace.GetZaxis().SetRangeUser(opt_bounds[1] - 5, opt_bounds[1])
    p = ROOT.TEllipse(opt_bounds[0][0],opt_bounds[0][1],0.005,0.005)
    p.SetLineColor(0)
    p.SetFillColor(0)
    h_phaseSpace.Draw('colz,CONT3')
    p.Draw()
    
    print 'bounds == [',opt_bounds[0], ']'
    #draw_labels(('Category VBF-%i' % catidx)+ ' \\BDT > '+('%1.3f'%catvalue[0]))
    c.SaveAs('plots/fom_cat_bounds_scan_smooth_{0:d}.pdf'.format(smooth_index))
    c.SaveAs('plots/fom_cat_bounds_scan_smooth_{0:d}.png'.format(smooth_index))
    
    c2 = ROOT.TCanvas('c2_boundary_optimisation','MVA',1200,600)
    c2.Divide(2,1)
    
    h_roc_sig.GetYaxis().SetTitleSize(25)
    h_roc_sig.GetXaxis().SetTitleSize(25)
    h_roc_sig.GetYaxis().SetTitleOffset (1)
    h_roc_sig.GetXaxis().SetTitleOffset (1)
    
    c2.cd(1)
    h_roc_sig.Draw('colz')
    
    h_roc_bkg.GetYaxis().SetTitleSize(25)
    h_roc_bkg.GetXaxis().SetTitleSize(25)
    h_roc_bkg.GetYaxis().SetTitleOffset (1)
    h_roc_bkg.GetXaxis().SetTitleOffset (1)
    c2.cd(2)
    h_roc_bkg.Draw('colz')
    
    raw_input('.......')
    c2.SaveAs('plots/fom_cdt_bounds_scan_smooth_{0:d}.pdf'.format(smooth_index))
    c2.SaveAs('plots/fom_cdt_bounds_scan_smooth_{0:d}.png'.format(smooth_index))
    
    return opt_bounds

def fom(hs, hb, bounds=None, nsteps=1000):
    if bounds is None:
        bounds = [0.5]
    bounds.append(hs.GetXaxis().GetXmax())
    bounds.sort()
    w  = (hs.GetXaxis().GetXmax() - hs.GetXaxis().GetXmin())/float(hs.GetNbinsX())
    Z  = 0
    for icat in range(0,len(bounds)-1):
        
        b  = hb.Integral(curr_bounds,next_bounds)/float(hb.Integral())
        s  = hs.Integral(curr_bounds,next_bounds)/float(hs.Integral())
        
        if b !=0 :#and b > 0.005 and s > 0.005:
            Z += (s*s)/b
    return Z


def GetCategoryPDFBounds(var    = 'dijet_BDT',
                         label  = 'VBF',
                         selection = '',
                         xmin   =-1,
                         xmax   = 1,
                         ncat   = 2,
                         nbin = 10000):
    histos = []
    legend  = ROOT.TLegend(0.55, 0.72,
                           (0.95 - ROOT.gStyle.GetPadRightMargin()),
                           (0.98 - ROOT.gStyle.GetPadTopMargin()))
    
    
    # === define the stack
    hbkg = ROOT.TH1F('hbkg','',nbin,-1,1)
    hsig = ROOT.TH1F('hsig','',nbin,-1,1)
    hbkg.SetTitle(";" + heppi.variables[var]['title']+";entries")
    hsig.SetTitle(";" + heppi.variables[var]['title']+";entries")
    # === cutflow
    cutflow = variable_cutflow(var,selection)
    if len(cutflow)!=0 :
        cutflow = 'weight*(' + cutflow + ')'
    else:
        cutflow = 'weight'
        
    # === fill hitograms
    ordsam = OrderedDict(sorted(heppi.samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        tree  = heppi.samples[proc].get('_root_tree_')#roof.Get(treename.replace('*',proc))
        histstr = '({0:d},{1:f},{2:f})'.format(int(nbin), -1, 1)
        tree.Project(
            'h_'+var + histstr,
            var,
            cutflow
        )
        if heppi.samples[proc]['label']== 'background':
            hbkg.Add(ROOT.gDirectory.Get('h_'+var))
        if heppi.samples[proc]['label']== 'signal':
            hsig.Add(ROOT.gDirectory.Get('h_'+var))
        
    
    hbkg.SetFillColorAlpha(122,0.6)
    hbkg.SetLineColor(1)
    hsig.SetLineColor(132)
    hsig.SetLineWidth(3)
    hbkg.GetYaxis().SetRangeUser(0,hbkg.GetMaximum() + hbkg.GetMaximum() * 0.5)
    
    catcut = []
    h_phaseSpace = ROOT.TH2F('h_phaseSpace',';C_{0};C_{1};z^{2}', nbin, -1,1, nbin,-1,1)
    bar    = ProgressBar(widgets=[colored('-- bounds scan :: ', 'red'),
                                  Percentage(),'  ' ,Bar('>'), ' ', ETA()], term_width=100)

    hsig.Smooth(4)
    hbkg.Smooth(4)
    for ibin in bar(range(0, hsig.GetNbinsX()+1)):
        for jbin in range(0, hsig.GetNbinsX()+1):
            if (jbin > ibin): continue
            z = significance(hsig, hbkg,
                             bounds = [
                                 hsig.GetBinCenter(ibin),
                                 hsig.GetBinCenter(jbin)
                             ])
            catcut.append([[float(hbkg.GetBinCenter(ibin)), float(hbkg.GetBinCenter(jbin))],z])
            h_phaseSpace.SetBinContent(ibin,jbin,z)
                        
    
    opt_bounds = max(catcut, key=lambda item: (item[1]))
    maxfrom_h  = h_phaseSpace.GetMaximum()
    
    #opt_bounds = min(catcut, key=lambda item: (item[1]))
    #roc.GetYaxis().SetLabelSize(0.032)
    #roc.SetLineColor(132)
    
    c = ROOT.TCanvas('c_boundary_optimisation','MVA',600,700)
    c.cd()
    h_phaseSpace.GetYaxis().SetTitleSize(25)
    h_phaseSpace.GetXaxis().SetTitleSize(25)
    h_phaseSpace.GetYaxis().SetTitleOffset (1)
    h_phaseSpace.GetXaxis().SetTitleOffset (1)
    h_phaseSpace.GetXaxis().SetRangeUser(opt_bounds[0][0] - 0.1, opt_bounds[0][0] + 0.1)
    h_phaseSpace.GetYaxis().SetRangeUser(opt_bounds[0][1] - 0.1, opt_bounds[0][1] + 0.1)
    h_phaseSpace.GetZaxis().SetRangeUser(opt_bounds[1] - 5, opt_bounds[1])
    p = ROOT.TEllipse(opt_bounds[0][0],opt_bounds[0][1],0.013,0.013)
    h_phaseSpace.Draw('colz,CONT4')
    p.Draw()
    raw_input('.......')
    print 'bounds == [',opt_bounds[0], ']'
    #draw_labels(('Category VBF-%i' % catidx)+ ' \\BDT > '+('%1.3f'%catvalue[0]))


    c.SaveAs('plots/fom_cat_bounds_scan.pdf')
    c.SaveAs('plots/fom_cat_bounds_scan.png')
    return opt_bounds




def print_categories(var, categories = None, select=''):
    if categories is None:
        categories = []
    for cat in categories:
        heppi.variables.update(
            {
                "_entries_":{
                    "hist" : "(3,0,3)", 
	            "cut"  : "",
	            "blind": "",
	            "log"  : True, 
	            "norm" : False, 
	            "title": "entries"
                }
            }
        )
        cutflow = heppi.variable_cutflow('_entries_','')
        if len(cutflow)!=0:
            cutflow = heppi.variable_cutflow('_entries_',select)
        # === define the stack
        hbkg_sel = ROOT.TH1F('hbkg_sel','',3,0,3)
        hsig_sel = ROOT.TH1F('hsig_sel','',3,0,3)
        hspc_sel = ROOT.TH1F('hspc_sel','',3,0,3)

        hbkg_all = ROOT.TH1F('hbkg_all','',3,0,3)
        hsig_all = ROOT.TH1F('hsig_all','',3,0,3)
        hspc_all = ROOT.TH1F('hspc_all','',3,0,3)

        # === cutflow
        logger.info('\hline')
        logger.info('category( {0:d} ) &{1:12.3f} &&\\'.format(categories.index(cat), cat))
        logger.info('\hline')
        logger.info('{0:12!s} &{1:12!s} &{2:12!s} &{3:12!s} \\'.format('process', 'total event', 'selection', 'efficiency'))
        ordsam = OrderedDict(sorted(heppi.samples.items(), key=lambda x: x[1]['order']))
        for proc in ordsam:
            tree  = heppi.samples[proc].get('_root_tree_')
            cutflow_sel = ''
            cutflow_all = ''
            if len(cutflow)!=0 :
                cutflow_sel = 'weight*(' + cutflow + ('&& {0!s} > {1:f}'.format(var, cat)) +')'
                cutflow_all = 'weight*(' + cutflow + ')'
            else:
                cutflow_sel = 'weight*(' + ('{0!s} > {1:f}'.format(var, cat)) +')'
                cutflow_all = 'weight'

            if 'Data' != proc:
                cutflow_all = cutflow_all.replace('weight','weight*{0:f}'.format((heppi.treeinfo.get('kfactor',1.0))))
                cutflow_sel = cutflow_sel.replace('weight','weight*{0:f}'.format((heppi.treeinfo.get('kfactor',1.0))))
            else:
                cutflow_all = cutflow_all.replace('weight*','')
                cutflow_sel = cutflow_sel.replace('weight*','')
                
            tree.Project(
                'h_sel_entries_' + proc + heppi.variables['_entries_']['hist'],
                '1',
                cutflow_sel
            )
            tree.Project(
                'h_all_entries_' + proc + heppi.variables['_entries_']['hist'],
                '1',
                cutflow_all
            )
            h_sel = ROOT.gDirectory.Get('h_sel_entries_'+proc)
            h_all = ROOT.gDirectory.Get('h_all_entries_'+proc)
            logger.info('{0:12!s} &{1:12.3f} &{2:12.3f} &{3:12.3f} \\'.format(proc, h_all.Integral(),
                                                           h_sel.Integral(),
                                                           100*float(h_sel.Integral())/float(h_all.Integral())))
            if heppi.samples[proc]['label']== 'background':
                hbkg_sel.Add(h_sel)
                hbkg_all.Add(h_all)
            if heppi.samples[proc]['label']== 'signal':
                hsig_sel.Add(h_sel)
                hsig_all.Add(h_all)
            if heppi.samples[proc]['label']== 'spectator':
                hspc_sel.Add(h_sel)
                hspc_all.Add(h_all)
                
        # -------------------------------------------------------------------
        logger.info('\hline')
        logger.info('{0:12!s} &{1:12.3f} &{2:12.3f} &{3:12.3f} \\'.format('BKG ',
                                                         hbkg_all.Integral(),
                                                         hbkg_sel.Integral(),
                                                         100*float(hbkg_sel.Integral())/float(hbkg_all.Integral())))
        logger.info('{0:12!s} &{1:12.3f} &{2:12.3f} &{3:12.3f} \\'.format('SIG',
                                                         hsig_all.Integral(),
                                                         hsig_sel.Integral(),
                                                         100*float(hsig_sel.Integral())/float(hsig_all.Integral())))
        logger.info('\hline')
        logger.info('S/\sqrt(S+B) = {0:12.3f}'.format((
            float(hsig_sel.Integral())/math.sqrt(hsig_sel.Integral()+hbkg_sel.Integral()) )))
        logger.info('\hline')

#class 2DimBoundaryOpt:
#    def __init__(self, trees = {},
#                 sig_label = 'vbf_125',
#                 selection = '',
#                 samples={},
#                 mva_label =
#                 'combined_BDT'):
#        self._trees_   = trees
#        self.sig_label = sig_label
#        self.min       =  1
#        self.max       = -1
#        self.ncat      =  2
#        self.mva_var   = 'combined_BDT'
#        self.mass_var  = 'dipho_mass'
#        self.nbin      = 10000
#        self._hsig_    = ROOT.TH1F('_hsig_',';%s;%s'%(mva_var, mass_var),
#                                   self.nbin,self.min,self.max,
#                                   self.nbin,self.min,self.max)
#        self._hbkg_    = ROOT.TH1F('_hbkg_',';%s;%s'%(mva_var, mass_var),
#                                   self.nbin,self.min,self.max,
#                                   self.nbin,self.min,self.max)
#        self.samples   = heepi.samples
#        
#    def get_data(self):
#        cutflow = heppi.variable_cutflow(self.mva_label,select)
#        if len(cutflow)!=0:
#            cutflow = heppi.variable_cutflow(self.mva_label ,select)
#            cutflow = 'weight*(' + cutflow + ')'
#        ordsam = OrderedDict(sorted(heppi.samples.items(), key=lambda x: x[1]['order']))
#        for proc in ordsam:
#            tree  = heppi.samples[proc].get('_root_tree_')#roof.Get(treename.replace('*',proc))
#            histstr = '(%i,%f,%f)' %(int(nbin),-1, 1)
#            tree.Project(
#                'h_'+var + histstr,
#                self.mva_label,
#                cutflow
#            )
#            if heppi.samples[proc]['label']== 'background':
#                _hbkg_.Add(ROOT.gDirectory.Get('h_'+var))
#            if heppi.samples[proc]['label']== 'signal':
#                _hsig_.Add(ROOT.gDirectory.Get('h_'+var))
#            
#            
#    def optimise(ncat = 2):
#        self.ncat = ncat
#        
#    # === loop over the samples
#    
#    c = ROOT.TCanvas('c_Opt'+str(catidx),'MVA',600,700)
#    c.cd()
#    hbkg.SetFillColorAlpha(122,0.6)
#    hbkg.SetLineColor(1)
#    hsig.SetLineColor(132)
#    hsig.SetLineWidth(3)
#    hbkg.GetYaxis().SetRangeUser(0,hbkg.GetMaximum() + hbkg.GetMaximum() * 0.5)
#    #ROOT.gPad.SetLogy()
#    #hbkg.Draw('hist')
#    #hsig.Draw('hist,same')
#    roc   = ROOT.TGraph()
#    roc.SetName ('fom_cat_' + str(catidx)+label)
#    roc.SetTitle(';BDT_{output};Z(BDT_{output})')
#    catcut = []
#    
#    if len(cutflow)!=0 :
#        cutflow = 'weight*(' + cutflow + ('&& %s > %f' % (var, xmin)) + ('&& %s < %f' % (var, xmax)) + ')'
#    else:
#        cutflow = 'weight'
#        
#    for ibin in range(0, hsig.GetNbinsX()+1):
#        Z  = 0
#        if fom == 'signif':
#            beff = hbkg.Integral(ibin,hsig.GetNbinsX())#hbkg.Integral() 
#            seff = hsig.Integral(ibin,hsig.GetNbinsX())#/hsig.Integral()
#            if (beff+seff) !=0 :
#                Z = (seff*seff)/(beff+seff)
#            else:
#                Z = 0
#        if fom == 'signif2':
#            b = hbkg.Integral(ibin,hsig.GetNbinsX())#hbkg.Integral() 
#            s = hsig.Integral(ibin,hsig.GetNbinsX())#/hsig.Integral()
#            if (b+s) !=0 and b!=0:
#                Z = 2*((s+b)*math.log((b+s)/b)-s) 
#            else:
#                Z = 0
#        catcut.append([float(hbkg.GetBinCenter(ibin)),Z])
#        roc.SetPoint (ibin,hbkg.GetBinCenter(ibin),Z)
#    catvalue = max(catcut, key=lambda item: (item[1]))
#    roc.GetYaxis().SetLabelSize(0.032)
#    roc.SetLineColor(132)
#    roc.Draw('AL')
#    roc.GetYaxis().SetRangeUser(0,catvalue[1] + catvalue[1]*0.5)
#    roc.GetXaxis().SetRangeUser(-1,1)
#    roc.Draw('AL')
#    c.Update()
#    line = ROOT.TLine()
#    line.SetLineColor(134)
#    line.SetLineStyle(7)
#    line.DrawLine(catvalue[0],0,catvalue[0],catvalue[1])
#    
#    print 'category (',catidx,') boundary [',catvalue[0],'][',catvalue[1],']'
#    draw_labels(('Category VBF-%i' % catidx)+ ' \\BDT > '+('%1.3f'%catvalue[0]))
#    c.SaveAs('plots/fom_cat'+ str(catidx) + '.pdf')
#    c.SaveAs('plots/fom_cat'+ str(catidx) + '.png')
#    return catvalue
#

def customize_roc(roc):
    roc.GetYaxis().SetTitleSize(25)
    roc.GetXaxis().SetTitleSize(25)
    roc.GetYaxis().SetTitleOffset (1)
    roc.GetXaxis().SetTitleOffset (1)
    #roc.SetLineWidth(2)
    
if __name__ == "__main__":
    i = 3
    heppi.sampledir   = '../data/training/rms003/merged'
    ROOT.gROOT.ProcessLine(".x .root/rootlogon.C")
    
    heppi.read_plotcard('plotcards/plotcard_rereco_vbf.json')
    heppi.print_cutflow()
    
    heppi.book_trees('')
    heppi.test_tree_book()
    
    #GetCategoryBounds(var        = 'combined_BDT',
    #                  selection  = 'dipho_mass < 135 && dipho_mass > 115',
    #                  nbin = 500,
    #                  smooth_index = 2
    #)

    legend  = ROOT.TLegend(0.5, 0.2,
                           (1 - ROOT.gStyle.GetPadRightMargin()),
                           (0.4 - ROOT.gStyle.GetPadTopMargin()))
    legend.SetTextAlign( 12 )
    legend.SetTextFont ( 43 )
    legend.SetTextSize ( 18 )
    legend.SetLineColor( 0 )
    legend.SetFillColor( 0 )
    legend.SetFillStyle( 0 )
    legend.SetLineColorAlpha(0,0)
    legend.SetShadowColor(0)
    """
    dijet_roc_dijet = draw_ROC(var       =  'dijet_mva'     ,
                               label     =  'combined_with_cat' ,
                               axistitle =  ';#varepsilon_{ggH};#varepsilon_{VBF}',
                               bkg       = ['ggh_125'],
                               categories= [])
    dijet_roc_comb  = draw_ROC(var       =  'dipho_dijet_MVA'     ,
                               label     =  'combined_with_cat' ,
                               axistitle =  ';#varepsilon_{ggH};#varepsilon_{VBF}',
                               bkg       = ['ggh_125'],
                               categories= [])
    
    dijet_roc_dijet = draw_ROC(var       =  'dijet_mva'     ,
                               label     =  'combined_with_cat' ,
                               axistitle =  ';#varepsilon_{#gamma#gamma};#varepsilon_{VBF}',
                               bkg       = ['dipho'],
                               categories= [])
    dijet_roc_comb  = draw_ROC(var       =  'dipho_dijet_MVA'     ,
                               label     =  'combined_with_cat' ,
                               axistitle =  ';#varepsilon_{#gamma#gamma};#varepsilon_{VBF}',
                               bkg       = ['dipho'],
                               categories= [])
    """
    dijet_roc_dijet = draw_ROC(var       =  'dijet_mva'     ,
                               label     =  'combined_with_cat' ,
                               axistitle =  ';#varepsilon_{Data};#varepsilon_{VBF}',
                               bkg       = ['Data'],
                               categories= [])
    dijet_roc_comb  = draw_ROC(var       =  'dipho_dijet_MVA'     ,
                               label     =  'combined_with_cat' ,
                               axistitle =  ';#varepsilon_{Data};#varepsilon_{VBF}',
                               bkg       = ['Data'],
                               categories= [])
    
    #categories=[0.9449,0.5819])

    c =  ROOT.TCanvas("c","c",600,600)
    c.cd()
    ROOT.gPad.SetGridx()
    ROOT.gPad.SetGridy()
    customize_roc(dijet_roc_dijet)
    customize_roc(dijet_roc_comb )
    
    dijet_roc_dijet.SetLineColor(132)
    dijet_roc_comb.SetLineColor (122)
    #dijet_roc_dijet.SetLineWidth(2)
    #dijet_roc_comb.SetLineWidth (2)
    
    legend.AddEntry( dijet_roc_dijet , "dijet VBF MVA"   , "l" );
    legend.AddEntry( dijet_roc_comb  , "combined VBF MVA", "l" );

    gr = ROOT.TMultiGraph()
    #gr.SetTitle(";#varepsilon_{ggH};#varepsilon_{VBF}")
    #gr.SetTitle(";#varepsilon_{#gamma#gamma};#varepsilon_{VBF}")
    #gr.SetTitle(";#varepsilon_{gjet};#varepsilon_{VBF}")
    gr.SetTitle(";#varepsilon_{Data};#varepsilon_{VBF}") 
    gr.Add(dijet_roc_dijet)
    gr.Add(dijet_roc_comb )
    
    gr.Draw("AL")
    gr.GetYaxis().SetRangeUser(0,1)
    gr.GetXaxis().SetRangeUser(0,1)
    customize_roc(gr)
    gr.Draw("AL")
    c.Update()
    heppi.draw_cms_headlabel(label_right='')
    legend.Draw()
        
    raw_input()
    #dijet_roc_ggf = draw_ROC(var       =  'combined_BDT'     ,
    #                         label     =  'combined_with_cat_data' ,
    #                         axistitle =  ';#varepsilon_{Data};#varepsilon_{VBF}',
    #                         bkg       = ['Data'],
    #                         categories=[])
                             #categories=[0.9449,0.5819])
                             
    #print_categories('combined_BDT', categories = [0.9449,0.5819])
    
