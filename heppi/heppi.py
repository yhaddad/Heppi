# -*- coding: utf-8 -*-
#from __future__ import print_function

try:
    import ROOT
except ImportError:
    raise ImportError(
        """
        ROOT is not in your environement, or not intsalled. 
        Please check!
        """)
try:
    from   termcolor    import colored
    from   jsmin        import jsmin
    from   progressbar  import ProgressBar, Bar, Percentage, ETA
    from   jsonmerge    import merge
    
except ImportError:
    raise ImportError(
        """
        please install termcolor and jsmin, and try again.
        Suggestion: pip install --user jsmin termcolor progressbar
        """)
import  os, sys, glob, sys, json, re, logging, collections, math, parser
from    collections        import OrderedDict
import  settings #as settings 

logging.basicConfig(format=colored('%(levelname)s:',attrs = ['bold'])
                    + colored('%(name)s:','blue') + ' %(message)s')
logger = logging.getLogger('heppi')
logger.setLevel(level=logging.DEBUG)

# 'application' code
samples     = collections.OrderedDict()
variables   = {}
rootfile    = {}
cutflow     = [] ## save all the cuts
selection   = {}
plotlabels  = {}
# delete me
sampledir   = './data/new' ## temp variable
treename    = 'vbfTagDumper/trees/*_13TeV_VBFDiJet'
treesUpSys  = []
treesDwSys  = []
#treename    = '*_13TeV_VBFDiJet'
options     = None   
allnormhist = False
treeinfo      = {}
title_on_plot = []
globalOptions = {}
# ---- plot card
def read_plotcard(plotcard, cut_card=''):
    global plotlabels
    global selection
    global variables
    global samples
    global treeinfo
    global treesUpSys
    global treesDwSys
    global treename
    global globalOptions
    config = None
    with open(plotcard) as f:
        config = json.loads(jsmin(f.read()), object_pairs_hook=collections.OrderedDict)
    if cut_card != '':
        logger.info(' ---- cut card is specified ----')
        logger.info(' -- %20s ' % ( cut_card )        )
        with open(cut_card) as f:
            cuts   = json.loads(jsmin(f.read()))
            config = merge(config, cuts)
    for key in config:
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
                if variables[varname].get('unit','')=='':
                    s = variables[varname].get('title','')
                    if '[' and ']' in s:
                        variables[varname].update({'unit':(find_between( s, "[", "]" ))})
                        
        if 'processes' in key:
            logger.info(' ---- book processes ----------')
            for proc in config[key]:
                samples[proc] = config[key][proc]
                logger.info(' -- %12s %12s' % (proc, samples[proc].get('cut','')))
        if 'selection' in key:
            logger.info(' ---- book selections ---------')
            selection = config[key]
            logger.info(' -- %12s' % (selection['title']))
        if 'labels' in key:
            plotlabels = config[key]
            if title_on_plot != []:
                plotlabels['name'] = title_on_plot
        if 'tree' in key:
            treeinfo = config[key]
            treename = treeinfo.get('name','vbfTagDumper/trees/*_13TeV_VBFDiJet')
        if 'systematics' in key:
            logger.info(' ---- book selections ---------')
            treesUpSys = config[key].get('UpTrees',[])
            treesDwSys = config[key].get('DwTrees',[])
            logger.info(' -- %12s' % ( treesUpSys) )
            logger.info(' -- %12s' % ( treesUpSys) )
        if 'globalOptions' in key:
            logger.info(' ---- book selections ---------')
            globalOptions = config[key]

            logger.info(' -- %12s' % ( globalOptions.get("ratio_range",[])) )
    logger.info(' ------------------------------')
    
# ---- create a cut flow except the considered variables
def variable_cutflow(variable, select=''):
    cutflow = ''
    for var in variables:
        if (len(variables[var].get('cut',''))!= 0) and (var!=variable):
            if len(cutflow)==0: cutflow    = '(' + variables[var].get('cut','') + ')'
            else: cutflow = cutflow + '&&' + '(' + variables[var].get('cut','') + ')'
            
    if select != '':
        cutflow = cutflow + '&&' + select
    return cutflow
#---------------------------------------------------------
def print_cutflow():
    for var in variables:
        if (len(variables[var]['cut'])!=0):
            logger.info('-- %20s: %12s' % (var, variables[var]['cut'] ))
    
    logger.info(' ------------------------------')
#---------------------------------------------------------
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
#---------------------------------------------------------
def draw_cut_line(hist, variable=''):
    if variables[variable].get('cut','')!='':
        ymin = hist.GetMinimum()
        ymax = hist.GetMaximum()
        cuttt = variables[variable].get('cut','').replace('(','').replace(')','')
        for cut in  cuttt.split('&&'):
            stmp = cut.split('>')
            if len(stmp) == 1:
                stmp = cut.split('<')
            xcut = eval(parser.expr(stmp[1]).compile())
            line = ROOT.TLine()
            line.SetLineColor(settings.cut_line_color)
            line.SetLineStyle(settings.cut_line_style)
            if xcut > hist.GetXaxis().GetXmin() or xcut < hist.GetXaxis().GetXmax(): 
                line.DrawLine(xcut,ymin,xcut,ymax)

#---------------------------------------------------------                
def draw_labels(label):
    t = ROOT.TLatex()
    t.SetTextAlign(12)
    t.SetTextFont (settings.text_font)
    t.SetTextSize (settings.text_size)
    shift = 0
    lines = []
    if type(label) == type(''):
        lines = label.split('\\')
    elif type(label) == type([]):
        lines = label
    else:
        raise ImportError("Label format is not supported: please enter a string or a table of strings!")
    for s in lines:
        t.DrawLatexNDC((0.04 + ROOT.gStyle.GetPadLeftMargin()),
                       (0.95 - shift - ROOT.gStyle.GetPadTopMargin()),s)
        shift = shift + settings.label_shift

#---------------------------------------------------------
def fformat(num):
    """
    Formating the float number to string
    1.0     --> ''
    2.0     --> 2
    0.21    --> 0.21
    0.32112 --> 0.32
    """
    if num != 1:
        s = ('%g'% (num)).rstrip('0').rstrip('.')
    else:
        s = ''
    return s#('%1.2f' % float(s) ) 
#---------------------------------------------------------
def draw_cms_headlabel(label_left  ='#scale[1.2]{#bf{CMS}} #it{Preliminary}',
                       label_right ='#sqrt{s} = 13 TeV, L = 2.56 fb^{-1}'):
    tex_left  = ROOT.TLatex()
    tex_left.SetTextAlign (11);
    tex_left.SetTextFont  (42);
    tex_left.SetTextSize  (0.036);
    tex_right = ROOT.TLatex()
    tex_right.SetTextAlign(31);
    tex_right.SetTextFont (42);
    tex_right.SetTextSize (0.036);
    tex_left.DrawLatexNDC (0.14,
                           1.01 - ROOT.gStyle.GetPadTopMargin(),label_left)
    tex_right.DrawLatexNDC(1-0.05,
                           1.01 - ROOT.gStyle.GetPadTopMargin(),label_right)
#---------------------------------------------------------
def makeRatioCanvas(name='_ratio_'):
    """returns a divided canvas for ratios"""
    Rcanv = ROOT.TCanvas("Rcanv","Rcanv",650,750+210)
    Rcanv.cd()
    padup = ROOT.TPad("pad1","pad1",0,0.3,1,1)
    padup.SetNumber(1)
    paddw = ROOT.TPad("pad2","pad2",0,0,1,0.3)
    paddw.SetNumber(2)
    
    padup.Draw()
    paddw.Draw()
    Rcanv.cd()
    ROOT.SetOwnership(padup,0)
    ROOT.SetOwnership(paddw,0)
    return Rcanv
#---------------------------------------------------------
def draw_categories(categories = [], miny=0, maxy=100):
    for cat in categories:
        line = ROOT.TLine()
        line.SetLineColor(129)
        line.SetLineStyle(7)
        line.SetLineWidth(2)
        line.DrawLine(cat,miny,cat,maxy)
#---------------------------------------------------------
def MakeStatProgression(myHisto,histDwSys={},histUpSys={},
                        title="", systematic_only=True, combine_with_systematic=True):
    """This function returns a function with the statistical precision in each bin"""
    statPrecision = myHisto.Clone('_ratioErrors_')
    systPrecision = myHisto.Clone('_ratioSysErrors_')
    statPrecision.SetTitle(title)
    statPrecision.SetFillColorAlpha(settings.ratio_error_band_color,settings.ratio_error_band_opacity)
    statPrecision.SetFillStyle(settings.ratio_error_band_style)
    statPrecision.SetMarkerColorAlpha(0,0)
    
    systPrecision.SetTitle(title + "_Sys_")
    systPrecision.SetFillColorAlpha(settings.ratio_syst_band_color,settings.ratio_error_band_opacity)
    systPrecision.SetFillStyle(settings.ratio_syst_band_style)
    systPrecision.SetMarkerColorAlpha(0,0)
    
    if len(histUpSys)==0 or len(histDwSys)==0 :
        systematic_only = False
    if systematic_only:
        for ibin in range(myHisto.GetNbinsX()+1):
            y    = statPrecision.GetBinContent(ibin);
            stat = statPrecision.GetBinError  (ibin);
            
            
            valup = {}
            valdw = {}
            #vals  = [y]
            #print "--> Nm[",ibin,"]::  (", y ,")"
            for sys in histUpSys:
                val   = histUpSys[sys].GetBinContent(ibin)
                #vals += [val]
                valup[sys] = val
                #print "--> Up[",ibin,"]:: ", sys, " (", val ,")"
            for sys in histDwSys:
                val   = histDwSys[sys].GetBinContent(ibin)
                #vals += [val]
                valdw[sys] = val
                #print "--> Dw[",ibin,"]:: ", sys, " (", val ,")"
                
            #largest_val  = max(vals)
            #smallest_val = min(vals)

            systError2   = 0
            for up in valup:
                dw = up.replace("Up","Down")
                e = 0.5*(valup[up] - valdw[dw])
                #print "--> error[",ibin,"]:: ", up, " (", e ,")"
                systError2 += e*e 
                            
            error  = 0
            if combine_with_systematic:
                #math.sqrt(syst*syst + stat*stat) 
                error = math.sqrt(systError2 + stat*stat)
            else:
                #error = 0.5*(largest_val - smallest_val)
                error = math.sqrt(systError2)
            #print "--> stat error[",ibin,"]:: (", stat ,")"
            #print "--> syst error[",ibin,"]:: (", math.sqrt(systError2) ,")"
            #print "--> combined error[",ibin,"]:: (", error ,")"
            if (y>0):
                statPrecision.SetBinContent(ibin,   1)#0.5*(largest_val + smallest_val)/y);
                statPrecision.SetBinError  (ibin,   error/y );
                
            else:
                statPrecision.SetBinContent(ibin,   1);
                statPrecision.SetBinError  (ibin,   0);
    else:
        for bin in range(myHisto.GetNbinsX()+1):
            y   = statPrecision.GetBinContent(bin);
            err = statPrecision.GetBinError  (bin);
            if (y>0):
                statPrecision.SetBinContent(bin,1);
                statPrecision.SetBinError  (bin,err/y);
            else:
                statPrecision.SetBinContent(bin,1);
                statPrecision.SetBinError  (bin,0);
                
    range_ = globalOptions.get("ratio_range",settings.ratio_precision_range)
    statPrecision.GetYaxis().SetRangeUser(range_[0], range_[1])
    return statPrecision

#---------------------------------------------------------
def drawStatErrorBand(myHisto,histDwSys={},histUpSys={},systematic_only=True, combine_with_systematic=True):
    """
    Draw this histogram with the statistical
    precision error in each bin
    """
    statPrecision = myHisto.Clone('_statErrors_')
    ROOT.SetOwnership(statPrecision,0)
    statPrecision.SetFillColorAlpha(settings.error_band_color,settings.error_band_opacity)
    statPrecision.SetFillStyle(settings.error_band_style)
    statPrecision.SetMarkerColorAlpha(0,0)

    #print '-->', histUpSys
    #print '-->', histDwSys
        
    if combine_with_systematic : systematic_only = True
    if systematic_only:
        for ibin in range(myHisto.GetNbinsX()+1):
            y    = statPrecision.GetBinContent(ibin);
            stat = statPrecision.GetBinError  (ibin);
            
            vals = [y]
            for sys in histUpSys:
                val = histUpSys[sys].GetBinContent(ibin)
                vals += [val]
            for sys in histDwSys:
                val= histDwSys[sys].GetBinContent(ibin)
                vals += [val]
            largest_val  = max(vals)
            smallest_val = min(vals)
            
            error  = 0
            if combine_with_systematic:
                syst  = 0.5*(largest_val - smallest_val)
                error = math.sqrt(syst*syst + stat*stat) 
            else:
                error = 0.5*(largest_val - smallest_val)
                
            statPrecision.SetBinContent(ibin,   (largest_val + smallest_val)/2.0);
            statPrecision.SetBinError  (ibin,   error);      
    return statPrecision

#---------------------------------------------------------
def makeRatioPlotCanvas(name=''):
    """
    returns a divided canvas for ratios
    
    """
    canv  = ROOT.TCanvas("c_" + name, name,settings.canvas_width,settings.canvas_height)
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
#---------------------------------------------------------
def makeRatio(hist1,hist2,ymax=2.1,ymin=0,norm=False, isdata =False):
    """returns the ratio plot hist2/hist1
    if one of the histograms is a stack put it in as argument 2!"""
    if norm:
        try:
            hist1.Scale(1/hist1.Integral())
            hist2.Scale(1/hist2.Integral())
        except(ZeroDivisionError):
            pass
    retH = hist1.Clone()
    retH.Divide(hist2)
    if isdata:
        for ibin in range(hist2.GetNbinsX()+1):
            ymc  = hist2.GetBinContent(ibin);
            stat = hist1.GetBinError  (ibin);
            #print "ibin ", ibin , " :: ymc ", ymc, " :: data error ", stat, " :: err/ymc ", stat/ymc
            if (ymc>0):
                retH.SetBinError  (ibin,stat/ymc);
            else:
                retH.SetBinError  (ibin,0);
    #if ymax or ymin:
    #    retH.GetYaxis().SetRangeUser(ymin,ymax)
    #    retH.SetLineColor(hist1.GetLineColor())
    #    retH.SetMarkerColor(hist1.GetMarkerColor())
    ROOT.SetOwnership(retH,0)
    return retH
#---------------------------------------------------------
def DataMCratio(histMC,histData,
                log=False,
                xTitle="",
                yTitle="",
                drawMCOpt="",
                drawDataOpt="",
                norm=False,
                ratioMin=0.7,
                ratioMax=1.3):
                #ratioMin=0.3,
                #ratioMax=1.7):
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
    line.SetLineColor(4)
    line.Draw()
    ROOT.SetOwnership(line,0)
    ratioHist.Draw('same')
    c.cd()
    return c
#---------------------------------------------------------
def customizeHisto(hist):
    hist.GetYaxis().SetTitleSize  (21)
    hist.GetYaxis().SetTitleFont  (43)
    hist.GetYaxis().SetTitleOffset(2.1)
    hist.GetYaxis().SetLabelFont  (43)
    hist.GetYaxis().SetLabelSize  (18)
    
    hist.GetXaxis().SetTitleSize  (23)
    hist.GetXaxis().SetTitleFont  (43)
    hist.GetXaxis().SetTitleOffset( 4)
    hist.GetXaxis().SetLabelFont  (43)
    hist.GetXaxis().SetLabelSize  (18)

def book_trees(select = ''):
    ordsam = OrderedDict(sorted(samples.items(), key=lambda x: x[1]['order']))

    sig_chain  = ROOT.TChain('sig_data')
    bkg_chain  = ROOT.TChain('bkg_data')
    
    for proc in ordsam:
        chainName = treename.replace('*',proc)
        if ordsam[proc].get("tree","") != "":
            chainName =  treename.replace('*',ordsam[proc].get("tree",""))
        chain      = ROOT.TChain(chainName)
        chainSysUp = []
        chainSysDw = []
        if type(samples[proc].get('name')) == type([]):
            for sam in samples[proc].get('name',[]):
                for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
                    chain.Add(f)
                    
                    if 'signal' in str(samples[proc].get('label','')).lower():
                        print 'sig -->', f+'/'+treename.replace('*',proc)
                        sig_chain.Add(f+'/'+treename.replace('*',proc))
                    elif 'data' not in str(samples[proc].get('label','')).lower():
                        print 'bkg -->', f+'/'+treename.replace('*',proc)
                        bkg_chain.Add(f+'/'+treename.replace('*',proc))
            if proc != 'Data':
                for sys in treesUpSys:
                    print "debug::(",proc,")", sys, " == ", samples[proc].get('label')
                    chainUp = ROOT.TChain(sys.replace('*',proc))
                    for sam in samples[proc].get('name',[]):
                        for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
                            chainUp.Add(f)
                        chainSysUp.append(chainUp)
                for sys in treesDwSys:
                    chainDw = ROOT.TChain(sys.replace('*',proc))
                    for sam in samples[proc].get('name',[]):
                        for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
                            chainDw.Add(f)
                        chainSysDw.append(chainDw)
        else:
            sam = samples[proc].get('name')
            for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
                chain.Add(f)
                if 'signal' in str(samples[proc].get('label','')).lower():
                    print 'sig -->', f+'/'+treename.replace('*',proc)
                    sig_chain.Add(f+'/'+treename.replace('*',proc))
                elif 'data' not in str(samples[proc].get('label','')).lower():
                    print 'bkg -->', f+'/'+treename.replace('*',proc)
                    bkg_chain.Add(f+'/'+treename.replace('*',proc))
            if samples[proc].get('label') != 'Data':
                for sys in treesUpSys:
                    chainUp = ROOT.TChain(sys.replace('*',proc))
                    for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
                        chainUp.Add(f)
                    chainSysUp.append(chainUp)
                for sys in treesDwSys:
                    chainDw = ROOT.TChain(sys.replace('*',proc))
                    for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
                        chainDw.Add(f)
                    chainSysDw.append(chainDw)
        # read systematic trees
        samples[proc].update({'_root_tree_'       : chain})
        samples[proc].update({'_root_tree_sysDw_' : chainSysDw})
        samples[proc].update({'_root_tree_sysUp_' : chainSysUp})
        
    logger.info('-- sig_chain.GetEntries() = %i' % sig_chain.GetEntries())
    logger.info('-- bkg_chain.GetEntries() = %i' % bkg_chain.GetEntries())
    return (sig_chain, bkg_chain)
        
        

def test_tree_book():
    for sam in samples:
        logger.info('nominal::'+ sam +' tree: '+ samples[sam].get('_root_tree_',ROOT.TChain()).GetName()
                    + ' nEvent:' + str(samples[sam].get('_root_tree_',ROOT.TChain()).GetEntries()))
        #logger.info('syst up tree: '+ samples[sam].get('_root_tree_sysUp_'))
        #logger.info('syst dw tree: '+ samples[sam].get('_root_tree_sysDw_'))

#---------------------------------------------------------
def draw_instack(variable, label='VBF', select=''):
    histos = []
    varname = variable
    formula = variables[varname].get('formula',varname)
    if ':=' in variable:
        varname  = variable.split(':=')[0]
        formula  = variable.split(':=')[1]
        
    histfilename = ('histogram_stack_' +
                    varname + '_' + label+ '_'
                    + selection['name'])
    
    legend  = None
    if settings.two_colomn_legend:
        legend  = ROOT.TLegend(0.45, 0.72,
                               (1 - ROOT.gStyle.GetPadRightMargin()),
                               (0.96 - ROOT.gStyle.GetPadTopMargin()))
        legend.SetNColumns(2)
        legend.SetColumnSeparation(0)
    else:
        legend  = ROOT.TLegend(0.6, 0.62,
                               (1 - ROOT.gStyle.GetPadRightMargin()),
                               (0.96 - ROOT.gStyle.GetPadTopMargin()))

    cutflow = variable_cutflow(variable,'')
    if len(cutflow)!=0:
        cutflow = variable_cutflow(variable,select)

    hstack = ROOT.THStack('hs_' + varname,'')
    
    hstack.SetName('hs_'+ varname)
    hstack.SetTitle(";" + variables[varname]['title']+";entries")

    histUpSys = {}
    histDwSys = {}

    for sys in treesUpSys:
        sysname   = sys.split('*')[1]
        histUpSys.update({sysname : None })
    for sys in treesDwSys:
        sysname   = sys.split('*')[1]
        histDwSys.update({sysname : None })
    
    if len(cutflow)!=0 and options.nocuts==False:
        cutflow = 'weight*(' + cutflow + ')'
    else:
        cutflow = 'weight*(1)'
    if  options.nocuts:
        histfilename = histfilename + '_nocuts'
    # loop over the samples
    bar    = ProgressBar(widgets=[colored('-- variables:: %20s   ' % variable, 'green'),
                                  Percentage(),'  ' ,Bar('>'), ' ', ETA()], term_width=100)
    ordsam = OrderedDict(sorted(samples.items(), key=lambda x: x[1]['order']))
    for proc in bar(ordsam):
        logger.debug(' -- %17s  %12s ' % (proc,  samples[proc].get('name')))
        
        tree       = samples[proc].get('_root_tree_')
        sample_cut = samples[proc].get('cut','')
        _cutflow_  = cutflow

        if samples[proc].get('cut','') != '':
            _cutflow_ = cutflow[:-1] + '&&' +  samples[proc].get('cut','') + ')'
        if variables[variable]['blind'] != '' and proc == 'Data':
            _cutflow_ = cutflow[:-1] + '&&' +  variables[variable]['blind']+ ')'
            
        if proc != 'Data':        
            tree.Project(
                'h_' + varname + variables[variable]['hist'],
                formula,
                _cutflow_.replace('weight','weight*%f*%f*%f' % ( treeinfo.get('kfactor',1.0),
                                                                 treeinfo.get('lumi'   ,1.0),
                                                                 samples[proc].get('kfactor',1.0)))
                )
        else:
            tree.Project(
                'h_' + varname + variables[variable]['hist'],
                formula,
                _cutflow_
            )
        #=== systematics 
        for sys in treesUpSys:
            if proc != 'Data' and 'signal' != samples[proc].get('label',''):        
                sysname = sys.split('*')[1]
                treeUp  = [x for x in samples[proc].get('_root_tree_sysUp_') if sysname in x.GetName()][0]
                treeUp.Project(
                    'h_UpSys_' + sysname +'_'+ varname + variables[variable]['hist'],
                    formula,
                    _cutflow_.replace('weight','weight*%f*%f*%f' % ( treeinfo.get('kfactor',1.0),
                                                                     treeinfo.get('lumi'   ,1.0),
                                                                     samples[proc].get('kfactor',1.0)))
                )
                histUp = ROOT.gDirectory.Get('h_UpSys_' + sysname +'_'+ varname )
                histUp.SetDirectory(0)
                if histUpSys[sysname] == None:
                    histUpSys[sysname] = histUp
                else:
                    histUpSys[sysname].Add(histUp)
        for sys in treesDwSys:
            if proc != 'Data' and 'signal' != samples[proc].get('label',''):        
                #treeDw    = samples[proc].get('_root_tree_sysDw_')[0]
                sysname   = sys.split('*')[1]
                treeDw  = [x for x in samples[proc].get('_root_tree_sysDw_') if sysname in x.GetName()][0]
                treeDw.Project(
                    'h_DwSys_' + sysname +'_'+ varname + variables[variable]['hist'],
                    formula,
                    _cutflow_.replace('weight','weight*%f*%f*%f' % ( treeinfo.get('kfactor',1.0),
                                                                     treeinfo.get('lumi'   ,1.0),
                                                                     samples[proc].get('kfactor',1.0)))
                )
                histDw = ROOT.gDirectory.Get('h_DwSys_' + sysname +'_'+ varname )
                histDw.SetDirectory(0)
                if histDwSys[sysname] == None:
                    histDwSys[sysname] = histDw
                else:
                    histDwSys[sysname].Add(histDw)
                    
        # ----------------------------------------------    
        hist = ROOT.gDirectory.Get('h_' + varname )
        hist.SetDirectory(0)

        hist.SetTitle(";" + variables[variable]['title']+";entries")
        hcolor = 1

        hcolor = samples[proc]['color']
        if ('signal'==samples[proc]['label']) or ('spectator'==samples[proc]['label']):
            hist.SetLineColor(hcolor)
            hist.SetLineStyle(1)
            hist.SetLineWidth(2)
            hist.SetFillStyle(0)
            histos.append(hist)
            if samples[proc].get('kfactor',1) !=1:
                legend.AddEntry(hist,
                                samples[proc]["title"] + ("#times%i"%samples[proc].get('kfactor',1)),
                                "l" );
            else:
                legend.AddEntry( hist, samples[proc]["title"], "l" );
        if 'data' in samples[proc]['label']:
            hist.SetMarkerColor(ROOT.kBlack)
            hist.SetLineColor  (ROOT.kBlack)
            hist.SetMarkerStyle(20)
            hist.SetMarkerSize (0.8) # fixme
            hist.SetFillColorAlpha(0,0)
            hist.SetLineWidth(2)
            hist.SetBinErrorOption(ROOT.TH1.kPoisson)
            hist.SetName(hist.GetName() + 'data')
            legend.AddEntry( hist, samples[proc]["title"], "lep" );
            histos.append(hist)
        if 'background' in samples[proc]['label']:
            hist.SetLineColor(ROOT.kBlack)
            hist.SetFillColor(hcolor)
            hist.SetLineWidth(2)
            hstack.Add(hist)
            legend.AddEntry( hist, samples[proc]["title"], "f" );
    # drawing
    c = makeRatioPlotCanvas(name = varname)
    c.cd(1)
    htmp   = histos[0].Clone('__htmp__')
    bounds = [float(s) for s in re.findall('[-+]?\d*\.\d+|\d+',variables[variable]['hist'])]
    htmp.SetTitle(';' + variables[variable]['title']
                  + (';events %s %s '% ( fformat((bounds[2]-bounds[1])/bounds[0]),
                                            variables[variable].get('unit',''))    ))
    htmp.Reset()
    if  options.allloghist or variables[variable]['log']:
        ymin = 0.01 - 0.003
        ymax = hstack.GetMaximum()*1000
        htmp.GetYaxis().SetRangeUser(ymin,ymax)
        histfilename = histfilename + '_log'
        ROOT.gPad.SetLogy()
    else:
        ymin = 0
        ymax = hstack.GetMaximum() + hstack.GetMaximum()*0.5
        htmp.GetYaxis().SetRangeUser(ymin,ymax)
    customizeHisto(htmp)
    htmp.Draw('')
    hstack.Draw('hist,same')
    herrstat = drawStatErrorBand(hstack.GetStack().Last(), histDwSys, histUpSys)
    herrstat.Draw('E2,same')
    hdata = None
    for h in histos:
        if 'data' not in h.GetName():
            h.Draw('hist,same')
        else:
            h.Draw('E,same')
            hdata = h

    if len(histUpSys)>0 and len(histDwSys)>0:
        legend.AddEntry(herrstat, "Stat #oplus Syst", "f" )
    else:
        legend.AddEntry(herrstat, "Stat Uncert", "f" )
        # cosmetics
    draw_cut_line(htmp,variable)
    draw_categories(variables[varname].get('boudaries',[]),
                    miny=htmp.GetMinimum(),
                    maxy=htmp.GetMaximum())
    ROOT.gPad.RedrawAxis();
    # this is for the legend
    legend.SetTextAlign( 12 )
    legend.SetTextFont ( 43 )
    legend.SetTextSize ( 18 )
    legend.SetLineColor( 0 )
    legend.SetFillColor( 0 )
    legend.SetFillStyle( 0 )
    legend.SetLineColorAlpha(0,0)
    legend.SetShadowColor(0)
    legend.Draw()
    # draw labels
    if  options.nocuts:
        draw_labels('w/o cuts')
    else:
        draw_labels(plotlabels['name'])
    draw_cms_headlabel(label_right='#sqrt{s} = 13 TeV, L = %1.2f fb^{-1}' % treeinfo.get('lumi',2.63))
    
    c.cd()
    c.cd(2)
    errorHist = MakeStatProgression(hstack.GetStack().Last(),histDwSys, histUpSys)
    ROOT.SetOwnership(errorHist,0)
    errorHist.GetXaxis().SetTitle(htmp.GetXaxis().GetTitle())
    errorHist.GetYaxis().SetTitle('Data/MC')
    errorHist.GetYaxis().CenterTitle(True)
    customizeHisto(errorHist)
    errorHist.Draw('E2')
    ratioHist = None
    sig_and_bkg_ratio = []
    if hdata==None:
        ratioHist = hstack.GetStack().Last().Clone('_temp_')
        ratioHist.Clear()
        ratioHist.SetLineColorAlpha(0,0)
        ratioHist.SetMarkerColorAlpha(0,0)
        ROOT.SetOwnership(ratioHist,0)
        ratioHist.GetXaxis().SetTitle(htmp.GetXaxis().GetTitle())
        ratioHist.GetYaxis().SetTitle(htmp.GetYaxis().GetTitle())
        if settings.ratio_draw_signal:
            for sig in histos:
                sig_and_bkg = hstack.GetStack().Last().Clone('_temp_bkg_' + sig.GetName())
                sig_and_bkg.Add(sig)
                sig_and_bkg_ratio_ = makeRatio(sig_and_bkg,hstack.GetStack().Last())
                ROOT.SetOwnership(sig_and_bkg_ratio_,0)
                sig_and_bkg_ratio_.GetXaxis().SetTitle(htmp.GetXaxis().GetTitle())
                sig_and_bkg_ratio_.GetYaxis().SetTitle(htmp.GetYaxis().GetTitle())
                sig_and_bkg_ratio_.SetFillColorAlpha(0,0)
                sig_and_bkg_ratio_.SetLineColor(sig.GetLineColor())
                sig_and_bkg_ratio.append(sig_and_bkg_ratio_)
    else:
        ratioHist = makeRatio(hist1 = hdata, hist2 = hstack.GetStack().Last(), isdata = True)
        ROOT.SetOwnership(ratioHist,0)
        ratioHist.GetXaxis().SetTitle(htmp.GetXaxis().GetTitle())
        ratioHist.GetYaxis().SetTitle(htmp.GetYaxis().GetTitle())
        if settings.ratio_draw_signal:
            for sig in histos:
                sig_and_bkg = hstack.GetStack().Last().Clone('_temp_bkg_' + sig.GetName())
                sig_and_bkg.Add(sig)
                sig_and_bkg_ratio_ = makeRatio(sig_and_bkg,hstack.GetStack().Last())
                ROOT.SetOwnership(sig_and_bkg_ratio_,0)
                sig_and_bkg_ratio_.GetXaxis().SetTitle(htmp.GetXaxis().GetTitle())
                sig_and_bkg_ratio_.GetYaxis().SetTitle(htmp.GetYaxis().GetTitle())
                sig_and_bkg_ratio_.SetFillColorAlpha(0,0)
                sig_and_bkg_ratio_.SetLineColor(sig.GetLineColor())
                sig_and_bkg_ratio.append(sig_and_bkg_ratio_)
                
    for o in sig_and_bkg_ratio:
        o.Draw('same,hist')
    draw_cut_line(errorHist,variable)
    line = ROOT.TLine(ratioHist.GetXaxis().GetXmin(),1,ratioHist.GetXaxis().GetXmax(),1)
    line.SetLineColor(4)
    line.SetLineStyle(7)
    line.Draw()
    draw_categories(variables[varname].get('boudaries',[]),
                    miny=htmp.GetMinimum(),
                    maxy=htmp.GetMaximum())
    ROOT.SetOwnership(line,0)
    ratioHist.Draw('same')

    c.cd()
    
    if variables[variable]['norm']==True or allnormhist==True:
        histfilename = histfilename + '_norm'
    c.SaveAs( 'plots/' + histfilename + '.png')
    c.SaveAs( 'plots/' + histfilename + '.pdf')
    
