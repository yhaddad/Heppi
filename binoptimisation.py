#!/usr/bin/python
import ROOT  # needed
from   heppi import heppi
from   collections        import OrderedDict
import os, sys, glob, sys, json, re, logging, collections, math
from   termcolor    import colored

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
             bkg = [], select='', categories=[]):
    c = ROOT.TCanvas("c_ROC","ROC's BDT",600,600)
    c.cd()
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
        histstr = '(%i,%f,%f)' %(int(400),-1, 1)
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
            if abs(hsig.GetBinCenter(ibin)-cat) < 0.005 :
                print 'diff :: val(', hsig.GetBinCenter(ibin),') ',abs(hsig.GetBinCenter(ibin)-cat)
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
    roc.Draw('AL')
    roc.GetYaxis().SetRangeUser(0,1)
    roc.GetXaxis().SetRangeUser(0,1)
    roc.Draw('AL')
    
    c.Update()
    
    draw_labels("Integral = %1.3f" % (roc.Integral()+0.5),"bl",0.035)
    for p in point[:-1]:
        p.Draw()
    #raw_input()
    c.SaveAs('plots/rocky_' + label + '.pdf')
    c.SaveAs('plots/rocky_' + label + '.png')
    
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
        cutflow = 'weight*(' + cutflow + ('&& %s > %f' % (var, xmin)) + ('&& %s < %f' % (var, xmax)) + ')'
    else:
        cutflow = 'weight'
        
    # === loop over the samples
    ordsam = OrderedDict(sorted(heppi.samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        #flist = glob.glob( sampledir + '/*'+ samples[proc]['name'] +'*.root')
        #roof  = ROOT.TFile.Open(flist[0])
        tree  = heppi.samples[proc].get('_root_tree_')#roof.Get(treename.replace('*',proc))
        histstr = '(%i,%f,%f)' %(int(nbin),-1, 1)
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
        cutflow = 'weight*(' + cutflow + ('&& %s > %f' % (var, xmin)) + ('&& %s < %f' % (var, xmax)) + ')'
    else:
        cutflow = 'weight'
        
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
    return catvalue

def print_categories(var, categories = [], select=''):
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
        logger.info('category( %i ) &%12.3f &&\\' % (categories.index(cat),cat))
        logger.info('\hline')
        logger.info('%12s &%12s &%12s &%12s \\' % ('process', 'total event', 'selection', 'efficiency'))
        ordsam = OrderedDict(sorted(heppi.samples.items(), key=lambda x: x[1]['order']))
        for proc in ordsam:
            tree  = heppi.samples[proc].get('_root_tree_')
            cutflow_sel = ''
            cutflow_all = ''
            if len(cutflow)!=0 :
                cutflow_sel = 'weight*(' + cutflow + ('&& %s > %f' % (var, cat)) +')'
                cutflow_all = 'weight*(' + cutflow + ')'
            else:
                cutflow_sel = 'weight*(' + ('%s > %f' % (var, cat)) +')'
                cutflow_all = 'weight'

            if 'Data' != proc:
                cutflow_all = cutflow_all.replace('weight','weight*%f' % (heppi.treeinfo.get('kfactor',1.0)))
                cutflow_sel = cutflow_sel.replace('weight','weight*%f' % (heppi.treeinfo.get('kfactor',1.0)))
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
            logger.info('%12s &%12.3f &%12.3f &%12.3f \\' % (proc,h_all.Integral(),
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
        logger.info('%12s &%12.3f &%12.3f &%12.3f \\' % ('BKG ',
                                                         hbkg_all.Integral(),
                                                         hbkg_sel.Integral(),
                                                         100*float(hbkg_sel.Integral())/float(hbkg_all.Integral())))
        logger.info('%12s &%12.3f &%12.3f &%12.3f \\' % ('SIG',
                                                         hsig_all.Integral(),
                                                         hsig_sel.Integral(),
                                                         100*float(hsig_sel.Integral())/float(hsig_all.Integral())))
        logger.info('\hline')
        logger.info('S/\sqrt(S+B) = %12.3f' % (
            float(hsig_sel.Integral())/math.sqrt(hsig_sel.Integral()+hbkg_sel.Integral()) ))
        logger.info('\hline')

class 2DimBoundaryOpt:
    def __init__(self, trees = {},
                 sig_label = 'vbf_125',
                 selection = '',
                 samples={},
                 mva_label =
                 'combined_BDT'):
        self._trees_   = trees
        self.sig_label = sig_label
        self.min       =  1
        self.max       = -1
        self.ncat      =  2
        self.mva_var   = 'combined_BDT'
        self.mass_var  = 'dipho_mass'
        self.nbin      = 10000
        self._hsig_    = ROOT.TH1F('_hsig_',';%s;%s'%(mva_var, mass_var),
                                   self.nbin,self.min,self.max,
                                   self.nbin,self.min,self.max)
        self._hbkg_    = ROOT.TH1F('_hbkg_',';%s;%s'%(mva_var, mass_var),
                                   self.nbin,self.min,self.max,
                                   self.nbin,self.min,self.max)
        self.samples   = heepi.samples
        
    def get_data(self):
        cutflow = heppi.variable_cutflow(self.mva_label,select)
        if len(cutflow)!=0:
            cutflow = heppi.variable_cutflow(self.mva_label ,select)
            cutflow = 'weight*(' + cutflow + ')'
        ordsam = OrderedDict(sorted(heppi.samples.items(), key=lambda x: x[1]['order']))
        for proc in ordsam:
            tree  = heppi.samples[proc].get('_root_tree_')#roof.Get(treename.replace('*',proc))
            histstr = '(%i,%f,%f)' %(int(nbin),-1, 1)
            tree.Project(
                'h_'+var + histstr,
                self.mva_label,
                cutflow
            )
            if heppi.samples[proc]['label']== 'background':
                _hbkg_.Add(ROOT.gDirectory.Get('h_'+var))
            if heppi.samples[proc]['label']== 'signal':
                _hsig_.Add(ROOT.gDirectory.Get('h_'+var))
            
            
    def optimise(ncat = 2):
        self.ncat = ncat
        
    # === loop over the samples
    
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
        cutflow = 'weight*(' + cutflow + ('&& %s > %f' % (var, xmin)) + ('&& %s < %f' % (var, xmax)) + ')'
    else:
        cutflow = 'weight'
        
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
    return catvalue


if __name__ == "__main__":
    i = 3
    heppi.sampledir   = '../data/output_data_rms_00%i/new/new/'%i
    ROOT.gROOT.ProcessLine(".x .root/rootlogon.C")
    #heppi.read_plotcard('config/plotcard_data_vbf.json')
    #heppi.book_trees()
    #heppi.test_tree_book()    
    #ROOT.gROOT.SetBatch(ROOT.kTRUE)
    heppi.read_plotcard('config/plotcard_data_vbf.json')
    heppi.print_cutflow()
    
    heppi.book_trees('')
    heppi.test_tree_book()
    
    dijet_roc_ggf = draw_ROC(var       =  'combined_BDT'     ,
                             label     =  'combined_with_cat' ,
                             axistitle =  ';#varepsilon_{SM-bkg};#varepsilon_{VBF}',
                             bkg       = ['gjet','qcd','dipho'],
                             categories= [])
                             #categories=[0.9449,0.5819])
    
    #dijet_roc_ggf = draw_ROC(var       =  'combined_BDT'     ,
    #                         label     =  'combined_with_cat_data' ,
    #                         axistitle =  ';#varepsilon_{Data};#varepsilon_{VBF}',
    #                         bkg       = ['Data'],
    #                         categories=[])
    #                         #categories=[0.9449,0.5819])
                             
    #print_categories('combined_BDT', categories = [0.9449,0.5819])
    
