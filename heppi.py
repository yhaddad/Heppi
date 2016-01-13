import ROOT # needed
import os, sys, glob, sys, json, re, logging, collections
from   collections        import OrderedDict
# from   termcolor          import colored
from   jsmin              import jsmin

#logging.basicConfig(filename='plot_output.log', level=logging.INFO)
logging.basicConfig(level=logging.INFO)

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
treeinfo    = {}


# ---- plot card
def read_plotcard(plotcard):
    global plotlabels
    global selection
    global variables
    global samples
    global treeinfo
    global treesUpSys
    global treesDwSys
    global treename
    config = None
    with open(plotcard) as f:
        config = json.loads(jsmin(f.read()))
        #config = json.loads(f.read())
    
    for key in config:
        if 'variables' in key:
            logging.info(' ---- book variables ----')
            for var in config[key]:
                logging.info(' -- %17s  %12s ' % ( var ,config[key][var]['hist']))
                variables[var] = config[key][var]
        if 'processes' in key:
            logging.info(' ---- book processes ----')
            for proc in config[key]:
                samples[proc] = config[key][proc]
                logging.info(' -- %12s %12s' % (key, samples[proc].get('cut','')))
        if 'selection' in key:
            logging.info(' ---- book selections ---')
            selection = config[key]
            logging.info(' -- %12s %12s' % (selection['name'], selection['title']))
        if 'labels' in key:
            logging.info(' ------ book labels -----')
            plotlabels = config[key]
            logging.info(' -- %12s %12s' % (key, plotlabels.get('name','')))
        if 'tree' in key:
            treeinfo = config[key]
            treename = treeinfo.get('name','vbfTagDumper/trees/*_13TeV_VBFDiJet')
            logging.info(' -- %12s' % ( treename ))
        if 'systematics' in key:
            logging.info(' ---- book selections ---')
            treesUpSys = config[key].get('UpTrees',[])
            treesDwSys = config[key].get('DwTrees',[])
            logging.info(' -- %12s' % ( treesUpSys))
            logging.info(' -- %12s' % ( treesUpSys))
        
        logging.info(' -------------------')
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
            print ('-- %20s: %12s' % (var, variables[var]['cut'] ) )


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
            xcut = float(stmp[1])
            line = ROOT.TLine()
            line.SetLineColor(134)
            line.SetLineStyle(7)
            if xcut > hist.GetXaxis().GetXmin() or xcut < hist.GetXaxis().GetXmax(): 
                line.DrawLine(xcut,ymin,xcut,ymax)

#---------------------------------------------------------                

    

#---------------------------------------------------------                
def draw_labels(label):
    t = ROOT.TLatex()
    t.SetTextAlign(12);
    t.SetTextFont (43);
    t.SetTextSize (18);
    shift = 0;
    for s in label.split('\\'):
        t.DrawLatexNDC((0.04 + ROOT.gStyle.GetPadLeftMargin()),
                       (0.95 - shift - ROOT.gStyle.GetPadTopMargin()),s)
        shift = shift + 0.03
#def draw_labels(labels=[]):
#    print 'here ?? '
#    t = ROOT.TLatex()
#    t.SetTextAlign(12);
#    t.SetTextFont (43);
#    t.SetTextSize (18);
#    shift = 0;
#    print 'labels ::' , labels 
#    for s in labels:
#        t.DrawLatexNDC((0.04 + ROOT.gStyle.GetPadLeftMargin()),
#                       (0.95 - shift - ROOT.gStyle.GetPadTopMargin()),s)
#        shift = shift + 0.03
#---------------------------------------------------------
def draw_cms_headlabel(label_left ='CMS Preliminary',
                       label_right='#sqrt{s} = 13 TeV, L = 2.56 fb^{-1}'):
    t = ROOT.TLatex()
    t.SetTextAlign(12);
    t.SetTextFont (42);
    t.SetTextSize (0.035);
    shift = 0;
    t.DrawLatexNDC(ROOT.gStyle.GetPadLeftMargin(),
                   1.028 - ROOT.gStyle.GetPadTopMargin(),label_left)
    t.DrawLatexNDC(0.55,
                   1.028 - ROOT.gStyle.GetPadTopMargin(),label_right)
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
    #ROOT.SetOwnership(Rcanv,0)
    ROOT.SetOwnership(padup,0)
    ROOT.SetOwnership(paddw,0)
    #print "check stuff", canv.GetPad(1)
    return Rcanv


#---------------------------------------------------------
def MakeStatProgression(myHisto,histDwSys={},histUpSys={}, title=""):
    """This function returns a function with the statistical precision in each bin"""
    statPrecision = myHisto.Clone('_ratioErrors_')
    ##statPrecision.Reset()
    statPrecision.SetTitle(title)
    statPrecision.SetFillColorAlpha(2, 0.5)
    statPrecision.SetMarkerColorAlpha(0,0)
    
    for bin in range(myHisto.GetNbinsX()+1):
        y   = statPrecision.GetBinContent(bin);
        err = statPrecision.GetBinError  (bin);
        #sys_up = 0
        #sys_dw = 0
        #for sys in treesUpSys:
        #    er = statPrecision.GetBinContent(bin)-treesUpSys[sys].GetBinContent(bin);
        #    sys_up += er*er
        #for sys in treesDwSys:
        #    er = statPrecision.GetBinContent(bin)-treesDwSys[sys].GetBinContent(bin);
        #    sys_dw += er*er
        #
        #sys_up = math.sqrt(sys_up)
        #sys_dw = math.sqrt(sys_dw)
        
        if (y>0):
            statPrecision.SetBinContent(bin,1);
            statPrecision.SetBinError  (bin,err/y);
        else:
            statPrecision.SetBinContent(bin,1);
            statPrecision.SetBinError  (bin,0);
    statPrecision.GetYaxis().SetRangeUser(0.01,3.1)    

    #if i in range(len(histUpSys)):
    
    return statPrecision

#---------------------------------------------------------
def drawStatErrorBand(myHisto,histDwSys={},histUpSys={},actuallyDrawSystErrorBand=True):
    """
    Draw this histogram with the statistical
    precision error in each bin
    """
    statPrecision = myHisto.Clone('_statErrors_')
    ROOT.SetOwnership(statPrecision,0)
    statPrecision.SetFillColorAlpha(2, 0.5)
    statPrecision.SetMarkerColorAlpha(0,0)

    if actuallyDrawSystErrorBand:
        for ibin in range(myHisto.GetNbinsX()+1):
            y   = statPrecision.GetBinContent(ibin);
            err = statPrecision.GetBinError  (ibin);
            
            vals = [y]
            print "Central:",y
            for sys in histUpSys:
                val = histUpSys[sys].GetBinContent(ibin)
                vals += [val]
                print sys,val
            for sys in histDwSys:
                val= histDwSys[sys].GetBinContent(ibin)
                vals += [val]
                print sys,val
     
            largest_val  = max(vals)
            smallest_val = min(vals)

            statPrecision.SetBinContent(ibin,   (largest_val + smallest_val)/2.0);
            statPrecision.SetBinError  (ibin,   (largest_val - smallest_val)/2.0);
        
    return statPrecision
    #if norm:
    #myHisto.Draw(drawOpt)
    #statPrecision.Draw('e2,same')
    #else:
    #myHisto.DrawNormalized(drawOpt)
    #statPrecision.DrawNormalized('e2,same')

#---------------------------------------------------------
def makeRatioPlotCanvas(name=''):
    """
    returns a divided canvas for ratios
    
    """
    canv  = ROOT.TCanvas("c_" + name, name,  700, 700+150)
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
#---------------------------------------------------------
def DataMCratio(histMC,histData,
                log=False,
                xTitle="",
                yTitle="",
                drawMCOpt="",
                drawDataOpt="",
                norm=False,
                ratioMin=0.3,
                ratioMax=1.7):
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

def book_trees(select=''):
    ordsam = OrderedDict(sorted(samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        logging.debug(' -- %17s  %12s ' % (proc,  samples[proc]['name']))
        flist = glob.glob( sampledir + '/*'+ samples[proc]['name'] +'*.root')
        logging.info(' -- sample:%17s  tree:%12s ' % ( proc, treename.replace('*',proc) ))
        
        roof  = ROOT.TFile.Open(flist[0])
        tree  = roof.Get(treename.replace('*',proc))
        samples[proc].update({'_root_tree_': tree})
    #print samples
    for s in ordsam:
        print s, ':: ', samples[s].get('_root_tree_')
#---------------------------------------------------------
def draw_instack(variable, label='VBF', select=''):
    histos = []
    
    formula = variable
    varname = variable
    if ':=' in variable:
        varname  = variable.split(':=')[0]
        formula  = variable.split(':=')[1]

    #print colored('varname::'+ varname+ ' <-- ' + formula, 'red', attrs=['bold'])
    print 'varname::'+ varname+ ' <-- ' + formula

    histfilename = ('histogram_stack_' +
                    varname + '_' + label+ '_'
                    + selection['name'])
    legend  = ROOT.TLegend(0.45, 0.72,
                           (1 - ROOT.gStyle.GetPadRightMargin()),
                           (0.96 - ROOT.gStyle.GetPadTopMargin()))
    legend.SetNColumns(2)
    legend.SetColumnSeparation(0)

    cutflow = variable_cutflow(variable,'')
    if len(cutflow)!=0:
        cutflow = variable_cutflow(variable,select)

    hstack = ROOT.THStack('hs_' + varname,'')
    
    hstack.SetName('hs_'+ varname)
    hstack.SetTitle(";" + variables[variable]['title']+";entries")

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
    ordsam = OrderedDict(sorted(samples.items(), key=lambda x: x[1]['order']))
    for proc in ordsam:
        logging.debug(' -- %17s  %12s ' % (proc,  samples[proc]['name']))
        flist = glob.glob( sampledir + '/*'+ samples[proc]['name'] +'*.root')
        print 'treename.replace(\'*\',', proc, ')', treename.replace('*',proc),' :: ',flist  

        roof  = ROOT.TFile.Open(flist[0])
        tree  = roof.Get(treename.replace('*',proc))
        if samples[proc].get('cut','') != '':
            cutflow = cutflow[:-1] + '&&' +  samples[proc].get('cut','') + ')'
        if variables[variable]['blind'] != '' and proc == 'Data':
            cutflow = cutflow[:-1] + '&&' +  variables[variable]['blind']+ ')'
        if proc != 'Data':        
            tree.Project(
                'h_' + varname + variables[variable]['hist'],
                formula,
                cutflow.replace('weight','weight*%f' % treeinfo.get('kfactor',1.0) )
            )
        else:
            tree.Project(
                'h_' + varname + variables[variable]['hist'],
                formula,
                cutflow
            )
        
        for sys in treesUpSys:
            if proc != 'Data' and 'signal' != samples[proc].get('label',''):        
                treeUp    = roof.Get(sys.replace('*',proc))
                sysname   = sys.split('*')[1]
                treeUp.Project(
                    'h_UpSys_' + sysname +'_'+ varname + variables[variable]['hist'],
                    formula,
                    cutflow.replace('weight','weight*%f' % treeinfo.get('kfactor',1.0) )
                )
                histUp = ROOT.gDirectory.Get('h_UpSys_' + sysname +'_'+ varname )
                histUp.SetDirectory(0)
                if histUpSys[sysname] == None:
                    histUpSys[sysname] = histUp
                else:
                    histUpSys[sysname].Add(histUp)
        for sys in treesDwSys:
            if proc != 'Data' and 'signal' != samples[proc].get('label',''):        
                treeDw    = roof.Get(sys.replace('*',proc))
                sysname   = sys.split('*')[1]
                treeDw.Project(
                    'h_DwSys_' + sysname +'_'+ varname + variables[variable]['hist'],
                    formula,
                    cutflow.replace('weight','weight*%f' % treeinfo.get('kfactor',1.0) )
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
            legend.AddEntry( hist, samples[proc]["title"], "l" );
        if 'data' in samples[proc]['label']:
            hist.SetMarkerColor(ROOT.kBlack)
            hist.SetLineColor  (ROOT.kBlack)
            hist.SetMarkerStyle(20)
            hist.SetMarkerSize (1.0)
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
    htmp.SetTitle(';' + variables[variable]['title']+(';events/(%1.2f)'% ((bounds[2]-bounds[1])/bounds[0])))
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
    hdata = None
    for h in histos:
        if 'data' in h.GetName():
            h.Draw('E,same')
            hdata = h
        else:
            h.Draw('hist,same')
    herrstat = drawStatErrorBand(hstack.GetStack().Last(), histDwSys, histUpSys)
    herrstat.Draw('E2,same')
    legend.AddEntry(herrstat, "Stat Uncert.", "f" )
    # cosmetics
    draw_cut_line(htmp,variable)
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
    draw_cms_headlabel()
    
    c.cd()
    c.cd(2)
    errorHist = MakeStatProgression(hstack.GetStack().Last(),title="")
    ROOT.SetOwnership(errorHist,0)
    errorHist.GetXaxis().SetTitle(htmp.GetXaxis().GetTitle())
    errorHist.GetYaxis().SetTitle('Data/MC')
    errorHist.GetYaxis().CenterTitle(True)
    customizeHisto(errorHist)
    errorHist.Draw('E2')

    ratioHist = None
    if hdata==None:
        ratioHist = hstack.GetStack().Last().Clone('_temp_')
        ratioHist.Clear()
        ROOT.SetOwnership(ratioHist,0)
        ratioHist.GetXaxis().SetTitle(htmp.GetXaxis().GetTitle())
        ratioHist.GetYaxis().SetTitle(htmp.GetYaxis().GetTitle())
    else:    
        ratioHist = makeRatio(hdata,hstack.GetStack().Last())
        ROOT.SetOwnership(ratioHist,0)
        ratioHist.GetXaxis().SetTitle(htmp.GetXaxis().GetTitle())
        ratioHist.GetYaxis().SetTitle(htmp.GetYaxis().GetTitle())
        
    line = ROOT.TLine(ratioHist.GetXaxis().GetXmin(),1,ratioHist.GetXaxis().GetXmax(),1)
    line.SetLineColor(4)
    line.SetLineStyle(7)
    line.Draw()
    ROOT.SetOwnership(line,0)
    ratioHist.Draw('same')
    c.cd()
    
    if variables[variable]['norm']==True or allnormhist==True:
        histfilename = histfilename + '_norm'
    c.SaveAs( 'plots/' + histfilename + '.png')
    c.SaveAs( 'plots/' + histfilename + '.pdf')
    
