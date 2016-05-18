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
    from   tabulate     import tabulate

except ImportError:
    raise ImportError(
        """
        please install termcolor and jsmin, and try again.
        Suggestion: pip install --user jsmin termcolor progressbar jsonmerge tabulate
        """)
import  os, sys, glob, sys, json, re, logging, collections, math, parser
from    collections        import OrderedDict

import  settings

logging.basicConfig(format=colored('%(levelname)s:',attrs = ['bold'])
                    + colored('%(name)s:','blue') + ' %(message)s')
logger = logging.getLogger('heppi')
#logger.setLevel(level=logging.DEBUG)
logger.setLevel(level=logging.INFO)

class utils:
    @staticmethod
    def find_between( s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""
    @staticmethod
    def fformat(num):
        """
        Formating the float number to string :
            1.0     --> ''
            2.0     --> 2
            0.21    --> 0.21
            0.32112 --> 0.32
        """
        if num != 1:
            s = ('%g'% (num)).rstrip('0').rstrip('.')
        else:
            s = ''
        return s
    @staticmethod
    def draw_cut_line(hist, variable):
        if len(variable.cut) != 0:
            ymin  = hist.GetMinimum()
            ymax  = hist.GetMaximum()
            cuttt = variable.cut.replace('(','').replace(')','')
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
    @staticmethod
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
    @staticmethod
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

class variable(object):
    """
    variable class contains all the infmation
    and options related to the desired plot :
    * name :
    * hist : definition of the histogram
        * Example:
            ```"hist" :[100,0,100]```
    * cut :
    * blind :
    * formula :
    * log :
    * norm :
    * title :
    * unit :
    * boundaries :
    """
    def __init__(self, name="", options = {}):
        self.__template__ = {
            "name"    : "",
            "hist"    : "(100,0,100)",
            "cut"     : "",
            "blind"   : "",
            "formula" : "",
            "log"     : False,
            "norm"    : False,
            "title"   : "",
            "unit"    : "",
            "boundaries" : [],
            # internal methods
            "root_legend"  : None,
            "root_cutflow" : ''
        }
        self.__dict__ = self.__template__
        self.__dict__.update(options)
        self.name     = name
        self.formula  = self.name
        if ':=' in self.formula:
            self.name     = self.formula.split(':=')[0]
            self.formula  = self.formula.split(':=')[1]
        if type(self.hist) == type([]) or type(self.hist) == type(()):
            self.hist = '(%s)' % (', '.join(map(str, self.hist)))
        if (self.unit == '') and ('[' and ']' in self.title):
                self.unit = utils.find_between( self.title , "[", "]" )
        self.histograms = []
    def __str__(self):
        return " -- variable :: %18s %12s" % (self.name, self.hist)
# ------------------------------
class sample  (object):
    """
    object type for sample and options :
    * files : represents the name of the input files you can give a string or a combination
              of string to match the files name.
              You can declare a single string or an array if you want to combine many files all together.
    * cut   : string cut appied only on this sample
    * tree  : tree string name of the sample. The tree name can be specified also in the for each input file by putting ':' after the file name followed by the tree name
    * color : the color that will be displayed on the rendered plot for this sample
    * order : stacking order
    * title : string title that will be displayed in the plot legend
    * label : tree type of labling are supported by `Heppi` :
        * signal    : this sample will be not stacked in final plot.
        * spectator : not stacked in the final plots
        * background: will be stacked in the final plot
        * data      : will be drawn on top of the stacked and, signal and spectator histograms
    """
    def __init__(self, name="", options = {}):
        self.__template__ = {
            "color"  : 0 ,
            "order"  : 0 ,
            "files"  : "",
            "title"  : "",
            "cut"    : "",
            "tree"   : "",
            "label"  : "",
            "kfactor": 1.0
        }
        self.__dict__  = self.__template__
        self.__dict__.update(options)
        self.name      = name
        self.label     = self.label.lower()
        self.root_tree = ROOT.TChain()
    def set_root_tree(self,tree):
        """
        return: ROOT tree
        """
        self.root_tree = tree
    def set_root_tree_syst_up(self,tree):
        """return: systematic ROOT tree up"""
        self.root_tree_syst_up = tree
    def set_root_tree_syst_dw(self,tree):
        """return: systematic ROOT tree down"""
        self.root_tree_syst_dw = tree
    def __str__(self):
        return " -- sample :: %20s %12i" % (self.name, self.root_tree.GetEntries())
class options (object):
    """
    object type containing Heppi options:
    * ratio_range : the range in the ratio plots
    *
    """
    def __init__(self,options = {}):
        self.__template__ = {
            "ratio_range"   : [0.5,1.5],
            "ratioplot"     : True,
            "legend"        : [ "" ],
            "treename"      :   "",
            "output_label"  :   "",
            "kfactor"       :  1.0,
            "intlumi"       :  1.0,
            "cutflow"       : [ "" ],
            "weight_branch" : "weight"
        }
        self.__dict__  = self.__template__
        self.__dict__.update(options)
    def __str__(self):
        string = " -- Heppi options :\n"
        for opt in self.__dict__:
             string += "    + %15s : %20s \n" % ( opt , str(self.__dict__[opt]))
        return string

class instack ():
    def __init__(self, plotcard, cutcard = '', sampledir = '{PWD}'):
        self.plotcard    = plotcard
        self.samples     = collections.OrderedDict()
        self.variables   = {}
        self.rootfile    = {}
        self.cutflow     = []
        self.cutcard     = cutcard
        self.selection   = {}
        self.options     = None
        self.sampledir   = sampledir
        self.sig_root_tree = ROOT.TChain('sig_data')
        self.bkg_root_tree = ROOT.TChain('bkg_data')

    def set_samples_directory(self,directory = "{PWD}"):
        self.sampledir = directory
    def read_plotcard(self):
        _config_ = None
        with open(self.plotcard) as f:
            _config_ = json.loads(jsmin(f.read()))
        if self.cutcard != '':
            logger.info(' ---- cut card is specified ----')
            logger.info(' -- %20s ' % ( self.cutcard )    )
            with open(self.cutcard) as f:
                _cuts_   = json.loads(jsmin(f.read()))
                _config_ = merge(config, cuts)
        for key in _config_:
            if 'variables' in key.lower():
                logger.info(' ----------------------------- ')
                for var in _config_[key]:
                    v = variable(var,_config_[key][var])
                    self.variables[v.name] = v
                    logger.info ( v )
            if 'processes' in key.lower():
                _samples_ = {}
                for proc in _config_[key]:
                    p = sample(proc,_config_[key][proc])
                    _samples_[p.name] = p
                self.samples = OrderedDict(sorted(_samples_.items(), key=lambda x: x[1].order ))
            if 'options' in key.lower():
                logger.info(' ----------------------------- ')
                self.options = options(_config_[key])
                logger.info( self.options )
        logger.info(' ----------------------------- ')
    def get_signal_tree(self):
        return self.sig_chain
    def get_background_tree(self):
        return self.bkg_chain
    def book_trees(self, make_sig_bkg_trees = False):
        _samples_ = []
        for proc,sample in self.samples.items():
            chainName = ""
            if sample.tree == "":
                chainName = str(self.options.treename).format(sampleid = sample.name)
                print chainName
            else:
                chainName = str(self.options.treename).format(sampleid = sample.tree)
            chain = ROOT.TChain(chainName)
            #chainSysUp = []
            #chainSysDw = []
            if type(sample.files) == type([]):
                for sam in sample.files:
                    for f in glob.glob( self.sampledir + '/*'+ sam +'*.root'):
                        chain.Add(f)
                        if 'signal'     in sample.label and make_sig_bkg_trees:
                            self.sig_root_tree.Add(f+'/'+ chainName)
                        if 'background' in sample.label and make_sig_bkg_trees:
                            self.bkg_root_tree.Add(f+'/'+ chainName)
            #    if proc != 'Data':
            #         for sys in treesUpSys:
            #             print "debug::(",proc,")", sys, " == ", samples[proc].get('label')
            #             chainUp = ROOT.TChain(sys.replace('*',proc))
            #             for sam in samples[proc].get('name',[]):
            #                 for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
            #                     chainUp.Add(f)
            #                 chainSysUp.append(chainUp)
            #         for sys in treesDwSys:
            #             chainDw = ROOT.TChain(sys.replace('*',proc))
            #             for sam in samples[proc].get('name',[]):
            #                 for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
            #                     chainDw.Add(f)
            #                 chainSysDw.append(chainDw)
            else:
                sam = sample.files
                for f in glob.glob( self.sampledir + '/*'+ sam +'*.root'):
                    chain.Add(f)
                    if 'signal' in sample.label and make_sig_bkg_trees:
                        self.sig_root_tree.Add(f+'/' + chainName )
                    if 'background' in sample.label and make_sig_bkg_trees:
                        self.bkg_root_tree.Add(f+'/' + chainName )
            #     if samples[proc].get('label') != 'Data':
            #         for sys in treesUpSys:
            #             chainUp = ROOT.TChain(sys.replace('*',proc))
            #             for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
            #                 chainUp.Add(f)
            #             chainSysUp.append(chainUp)
            #         for sys in treesDwSys:
            #             chainDw = ROOT.TChain(sys.replace('*',proc))
            #             for f in glob.glob( sampledir + '/*'+ sam +'*.root'):
            #                 chainDw.Add(f)
            #             chainSysDw.append(chainDw)
            # read systematic trees
            #self.samples[proc].update({'_root_tree_'       : chain})
            self.samples[proc].set_root_tree(chain)
            #self.samples[proc].update({'_root_tree_sysDw_' : chainSysDw})
            #self.samples[proc].update({'_root_tree_sysUp_' : chainSysUp})
            _samples_.append([  self.samples[proc].order,
                                self.samples[proc].name ,
                                self.samples[proc].tree ,
                                self.samples[proc].kfactor ,
                                self.samples[proc].label,
                                self.samples[proc].cut  ,
                                self.samples[proc].root_tree.GetEntries()])
        logger.info("\n" + tabulate(_samples_, ["","sample","tree","kfactor","label","cut","events"],
                                    tablefmt="psql"))
    # ---- create a cut flow except the considered variables
    def variable_cutflow(self, variable, select=''):
        cutflow = ''
        for key,var in self.variables.items():
            if (len(var.cut) == 0) or (var.name == variable): continue
            if  len(cutflow) == 0 : cutflow = '(' + var.cut + ')'
            else: cutflow  = cutflow + '&&' + '(' + var.cut + ')'
        if select  != '':
            cutflow = cutflow + '&&' + select
        return cutflow
    #---------------------------------------------------------
    def print_cutflow(self, format="psql" ):
        _header_  = ["cutflow"]
        _table_   = []
        _noselec_ = []
        _noselec_.append("no cut")
        _total_   = {}
        for proc,sample in self.samples.items():
            _header_.append("N : "+sample.name )
            _header_.append("eff(%)")
            _total_[sample.name] = sample.root_tree.GetEntries(sample.cut)
            _noselec_.append(sample.root_tree.GetEntries(sample.cut))
            _noselec_.append(str(100))
        _table_.append(_noselec_)
        _cutflow_ = ''
        for var in self.variables:
            if (len(self.variables[var].cut) !=0):
                _selec_ = []
                if 'latex' not in format :
                    _selec_.append(self.variables[var].cut)
                else:
                    _cut_ = self.variables[var].cut.replace(var,self.variables[var].title)
                    _selec_.append(_cut_.replace('#',''))

                if len(_cutflow_) == 0:
                    _cutflow_ =  '&&'.join([self.variables[var].cut])
                else:
                    _cutflow_ =  '&&'.join([_cutflow_, self.variables[var].cut])
                for proc,sample in self.samples.items():
                    tot_events = sample.root_tree.GetEntries(sample.cut)
                    _cut_ = _cutflow_
                    if len(sample.cut) != 0:
                        _cut_ =  '&&'.join([_cut_, sample.cut])
                    _selec_.append(sample.root_tree.GetEntries(_cut_))
                    _selec_.append(100*sample.root_tree.GetEntries(_cut_)/float(tot_events))
                _table_.append(_selec_)
        logger.info("\n" + tabulate(_table_, _header_,tablefmt=format,floatfmt=".2f"))

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
    def draw_categories(self,categories = [], miny=0, maxy=100):
        for cat in categories:
            line = ROOT.TLine()
            line.SetLineColor(129)
            line.SetLineStyle(7)
            line.SetLineWidth(2)
            line.DrawLine(cat,miny,cat,maxy)
    #---------------------------------------------------------
    def MakeStatProgression(self,myHisto,histDwSys={},histUpSys={},
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
                y    = statPrecision.GetBinContent(ibin)
                stat = statPrecision.GetBinError  (ibin)
                valup = {}
                valdw = {}
            for sys in histUpSys:
                val   = histUpSys[sys].GetBinContent(ibin)
                valup[sys] = val
            for sys in histDwSys:
                val   = histDwSys[sys].GetBinContent(ibin)
                valdw[sys] = val

            systError2   = 0
            for up in valup:
                dw = up.replace("Up","Down")
                e = 0.5*(valup[up] - valdw[dw])
                systError2 += e*e

            error  = 0
            if combine_with_systematic:
                error = math.sqrt(systError2 + stat*stat)
            else:
                error = math.sqrt(systError2)

            if (y>0):
                systPrecision.SetBinContent(ibin,   1)#0.5*(largest_val + smallest_val)/y);
                systPrecision.SetBinError  (ibin,   error/y );
                statPrecision.SetBinContent(ibin,   1)#0.5*(largest_val + smallest_val)/y);
                statPrecision.SetBinError  (ibin,   stat/y );
            else:
                statPrecision.SetBinContent(ibin,   1);
                statPrecision.SetBinError  (ibin,   0);
                systPrecision.SetBinContent(ibin,   1)#0.5*(largest_val + smallest_val)/y);
                systPrecision.SetBinError  (ibin,   0);
        else:
            for bin in range(myHisto.GetNbinsX()+1):
                y   = statPrecision.GetBinContent(bin);
                err = statPrecision.GetBinError  (bin);
                if (y>0):
                    statPrecision.SetBinContent(bin,1);
                    statPrecision.SetBinError  (bin,err/y);
                    systPrecision.SetBinContent(bin,1);
                    systPrecision.SetBinError  (bin,err/y);
                else:
                    statPrecision.SetBinContent(bin,1);
                    statPrecision.SetBinError  (bin,0);
                    systPrecision.SetBinContent(bin,1);
                    systPrecision.SetBinError  (bin,0);
        statPrecision.GetYaxis().SetRangeUser(self.options.ratio_range[0], self.options.ratio_range[1])
        systPrecision.GetYaxis().SetRangeUser(self.options.ratio_range[0], self.options.ratio_range[1])
        return (statPrecision, systPrecision)
    #---------------------------------------------------------
    def drawStatErrorBand(self,myHisto,histDwSys={},histUpSys={},systematic_only=True, combine_with_systematic=True):
        """
        Draw this histogram with the statistical
        precision error in each bin
        """
        statPrecision = myHisto.Clone('_statErrors_')
        ROOT.SetOwnership(statPrecision,0)
        statPrecision.SetFillColorAlpha(settings.error_band_color,settings.error_band_opacity)
        statPrecision.SetFillStyle(settings.error_band_style)
        statPrecision.SetMarkerColorAlpha(0,0)

        systPrecision = myHisto.Clone('_systErrors_')
        ROOT.SetOwnership(systPrecision,0)
        systPrecision.SetFillColorAlpha(settings.syst_error_band_color,settings.syst_error_band_opacity)
        systPrecision.SetFillStyle(settings.syst_error_band_style)
        systPrecision.SetMarkerColorAlpha(0,0)


        if combine_with_systematic : systematic_only = True
        if systematic_only:
            for ibin in range(myHisto.GetNbinsX()+1):
                y    = statPrecision.GetBinContent(ibin);
                stat = statPrecision.GetBinError  (ibin);
                valup = {}
                valdw = {}
                for sys in histUpSys:
                    val   = histUpSys[sys].GetBinContent(ibin)
                    valup[sys] = val
                for sys in histDwSys:
                    val   = histDwSys[sys].GetBinContent(ibin)
                    valdw[sys] = val

                systError2   = 0
                for up in valup:
                    dw = up.replace("Up","Down")
                    e = 0.5*(valup[up] - valdw[dw])
                    systError2 += e*e

                error  = 0
                if combine_with_systematic:
                    error = math.sqrt(systError2 + stat*stat)
                else:
                    error = math.sqrt(systError2)

                if (y>0):
                    systPrecision.SetBinContent(ibin,   y)#0.5*(largest_val + smallest_val)/y);
                    systPrecision.SetBinError  (ibin,   error );
                    statPrecision.SetBinContent(ibin,   y)#0.5*(largest_val + smallest_val)/y);
                    statPrecision.SetBinError  (ibin,   stat );
                else:
                    statPrecision.SetBinContent(ibin,   0);
                    statPrecision.SetBinError  (ibin,   0);
                    systPrecision.SetBinContent(ibin,   0)#0.5*(largest_val + smallest_val)/y);
                    systPrecision.SetBinError  (ibin,   0);

                # ------
        return (statPrecision, systPrecision)
    #---------------------------------------------------------
    def makeRatioPlotCanvas(self, name=''):
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
    def makeRatio(self, hist1,hist2,ymax=2.1,ymin=0,norm=False, isdata =False):
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
    def DataMCratio(self, histMC,histData,
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

        (errorHist,systHist) = self.MakeStatProgression(histMC,title="")
        ROOT.SetOwnership(errorHist,0)
        ROOT.SetOwnership(systHist ,0)
        errorHist.GetXaxis().SetTitle(xTitle)
        errorHist.GetYaxis().SetTitle(yTitle)
        #
        errorHist.Draw('E2')
        sysrHist.Draw('E2,same')
        ratioHist = self.makeRatio(histData,histMC,ymax= ratioMax,ymin=ratioMin,norm=norm)
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
    def customizeHisto(self, hist):
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
    #---------------------------------------------------------
    #---------------------------------------------------------
    def test_tree_book():
        for sam in samples:
            logger.info('nominal::'+ sam +' tree: '+ samples[sam].get('_root_tree_',ROOT.TChain()).GetName()
                        + ' nEvent:' + str(samples[sam].get('_root_tree_',ROOT.TChain()).GetEntries()))
    #---------------------------------------------------------
    def draw(self, varkey, label='VBF', select=''):
        variable = None
        histos = []
        try:
            variable = self.variables.get(varkey)
        except KeyError:
            pass

        histname = ('stack_histogram_' +
                    variable.name + '_' + label + '_'
                    '')
        variable.root_legend = None
        if settings.two_colomn_legend:
            variable.root_legend  = ROOT.TLegend(0.45, 0.72,
                                        (1.00 - ROOT.gStyle.GetPadRightMargin()),
                                        (0.96 - ROOT.gStyle.GetPadTopMargin()))
            variable.root_legend.SetNColumns(2)
            variable.root_legend.SetColumnSeparation(0)
        else:
            variable.root_legend  = ROOT.TLegend(0.6, 0.62,
                                        (1.00 - ROOT.gStyle.GetPadRightMargin()),
                                        (0.96 - ROOT.gStyle.GetPadTopMargin()))

        variable.root_cutflow = self.variable_cutflow(variable.name,'')
        #if len(variable.root_cutflow)!=0:
        #    variable.root_cutflow = variable_cutflow(variable.name,select)

        hstack = ROOT.THStack('hs_' + variable.name,'')
        hstack.SetName('hs_'+ variable.name)
        hstack.SetTitle(";" + variable.title+";entries")

        histUpSys = {}
        histDwSys = {}

        # for sys in treesUpSys:
        #     sysname   = sys.split('*')[1]
        #     histUpSys.update({sysname : None })
        # for sys in treesDwSys:
        #     sysname   = sys.split('*')[1]
        #     histDwSys.update({sysname : None })

        #if len(variable.root_cutflow)!=0 and options.nocuts == False:
        if len(variable.root_cutflow)!=0:
            _cutflow_ = [self.options.weight_branch]
            _cutflow_.append('('+variable.root_cutflow+')')
            variable.root_cutflow = '*'.join(_cutflow_)
        else:
            variable.root_cutflow = self.options.weight_branch
        bar    = ProgressBar(widgets=[colored('-- variables:: %20s   ' % variable.name, 'green'),
                            Percentage(),'  ' ,Bar('>'), ' ', ETA()], term_width=100)
        for proc,sample in bar(self.samples.items()):
            logger.info(' -- %17s  %12s ' % (proc,  sample.name) )
            _cutflow_ = variable.root_cutflow
            if len(sample.cut) != 0:
                _cutflow_ = '&&'.join([variable.root_cutflow[:-1],sample.cut+')'])
            if len(variable.blind) != 0 and sample.label == 'data':
                _cutflow_ = '&&'.join([variable.root_cutflow[:-1],variable.blind+')'])

            print "cutflow--> ",_cutflow_
            if sample.label != 'data':
                sample.root_tree.Project(
                    'h_' + variable.name + variable.hist,
                    variable.formula,
                    '*'.join(
                        [   _cutflow_,
                            "%f" % self.options.kfactor,
                            "%f" % self.options.intlumi,
                            "%f" % sample.kfactor
                        ]
                    )
#                    _cutflow_.replace('weight','weight*%f*%f*%f' % ( self.options.kfactor,
#                                                                     self.options.intlumi,
#                                                                     sample.kfactor     )
                    #)
                )
                print "cutflow ::",  _cutflow_
                print   '*'.join([  _cutflow_,
                                    str(self.options.kfactor),
                                    str(self.options.intlumi),
                                    str(sample.kfactor)     ])

            elif sample.label == 'data':
                sample.root_tree.Project(
                    'h_' + variable.name + variable.hist,
                    variable.formula,
                    _cutflow_
                )

            else:
                logger.error(' -- the label of the sample "%s" is not recognised by Heepi' % sample.name )
            #=== systematics
            # for sys in treesUpSys:
            #     if proc != 'Data' and 'signal' != samples[proc].get('label',''):
            #         sysname = sys.split('*')[1]
            #         treeUp  = [x for x in samples[proc].get('_root_tree_sysUp_') if sysname in x.GetName()][0]
            #         treeUp.Project(
            #             'h_UpSys_' + sysname +'_'+ varname + variables[variable]['hist'],
            #             formula,
            #             _cutflow_.replace('weight','weight*%f*%f*%f' % ( treeinfo.get('kfactor',1.0),
            #                                                              treeinfo.get('lumi'   ,1.0),
            #                                                              samples[proc].get('kfactor',1.0)))
            #         )
            #         histUp = ROOT.gDirectory.Get('h_UpSys_' + sysname +'_'+ varname )
            #         histUp.SetDirectory(0)
            #         if histUpSys[sysname] == None:
            #             histUpSys[sysname] = histUp
            #         else:
            #             histUpSys[sysname].Add(histUp)
            # for sys in treesDwSys:
            #     if proc != 'Data' and 'signal' != samples[proc].get('label',''):
            #         #treeDw    = samples[proc].get('_root_tree_sysDw_')[0]
            #         sysname   = sys.split('*')[1]
            #         treeDw  = [x for x in samples[proc].get('_root_tree_sysDw_') if sysname in x.GetName()][0]
            #         treeDw.Project(
            #             'h_DwSys_' + sysname +'_'+ varname + variables[variable]['hist'],
            #             formula,
            #             _cutflow_.replace('weight','weight*%f*%f*%f' % ( treeinfo.get('kfactor',1.0),
            #                                                              treeinfo.get('lumi'   ,1.0),
            #                                                              samples[proc].get('kfactor',1.0)))
            #         )
            #         histDw = ROOT.gDirectory.Get('h_DwSys_' + sysname +'_'+ varname )
            #         histDw.SetDirectory(0)
            #         if histDwSys[sysname] == None:
            #             histDwSys[sysname] = histDw
            #         else:
            #             histDwSys[sysname].Add(histDw)

            # ----------------------------------------------
            hist = ROOT.gDirectory.Get('h_' + variable.name )
            hist.SetDirectory(0)

            hist.SetTitle(";" + variable.title + ";entries")
            if ('signal'==sample.label) or ('spectator'==sample.label):
                hist.SetLineColor(sample.color)
                hist.SetLineStyle(1)
                hist.SetLineWidth(2)
                hist.SetFillStyle(0)
                histos.append(hist)
                if sample.kfactor != 1:
                    variable.root_legend.AddEntry(hist,
                                    sample.title + ("#times%i" % sample.kfactor ),
                                    "l" );
                else:
                    variable.root_legend.AddEntry( hist, sample.title, "l" );
            if 'data' in sample.label:
                hist.SetMarkerColor(sample.color)
                hist.SetLineColor  (sample.color)
                hist.SetMarkerStyle(20)
                hist.SetMarkerSize (0.8) # fixme
                hist.SetFillColorAlpha(0,0)
                hist.SetLineWidth(2)
                hist.SetBinErrorOption(ROOT.TH1.kPoisson)
                hist.SetName(hist.GetName() + 'data')
                variable.root_legend.AddEntry( hist, sample.title, "lep" )
                histos.append(hist)
            if 'background' in sample.label:
                hist.SetLineColor(ROOT.kBlack)
                hist.SetFillColor(sample.color)
                hist.SetLineWidth(2)
                hstack.Add(hist)
                variable.root_legend.AddEntry( hist, sample.title, "f" )
        # drawing
        #c = ROOT.TCanvas("c","c",500,500)
        c = self.makeRatioPlotCanvas(name = variable.name)
        c.cd(1)
        _htmp_ = histos[0].Clone('__htmp__')
        ROOT.SetOwnership(_htmp_,0)
        bounds = [float(s) for s in re.findall('[-+]?\d*\.\d+|\d+',variable.hist )]
        _htmp_.SetTitle(';' + variable.title
                       + (';events %s %s '% (utils.fformat((bounds[2]-bounds[1])/bounds[0]),
                                            variable.unit)    ))
        _htmp_.Reset()
        if variable.log:
            ymin = 0.01 - 0.003
            ymax = hstack.GetMaximum()*1000
            _htmp_.GetYaxis().SetRangeUser(ymin,ymax)
            ROOT.gPad.SetLogy()
        else:
            ymin = 0
            ymax = hstack.GetMaximum() + hstack.GetMaximum()*0.5
            _htmp_.GetYaxis().SetRangeUser(ymin,ymax)

        self.customizeHisto(_htmp_)
        _htmp_.Draw('hist')
        hstack.Draw('hist,same')
        (herrstat, herrsyst) = self.drawStatErrorBand(hstack.GetStack().Last(), histDwSys, histUpSys)
        herrsyst.Draw('E2,same')
        herrstat.Draw('E2,same')
        #
        #hdata = None
        for h in histos:
            if 'data' not in h.GetName():
                h.Draw('hist,same')
            else:
                h.Draw('E,same')
                hdata = h
        # # if len(histUpSys)>0 and len(histDwSys)>0:
        # #     variable.root_legend.AddEntry(herrstat, "Stat", "f" )
        # #     variable.root_legend.AddEntry(herrsyst, "Stat #oplus Syst", "f" )
        # # else:
        # #     variable.root_legend.AddEntry(herrstat, "Stat Uncert", "f" )
        #
        # cosmetics
        utils.draw_cut_line(_htmp_,variable)
        self.draw_categories(variable.boundaries, miny=_htmp_.GetMinimum(),maxy=_htmp_.GetMaximum())
        ROOT.gPad.RedrawAxis()
        # this is for the legend
        variable.root_legend.SetTextAlign( 12 )
        variable.root_legend.SetTextFont ( 43 )
        variable.root_legend.SetTextSize ( 18 )
        variable.root_legend.SetLineColor( 0 )
        variable.root_legend.SetFillColor( 0 )
        variable.root_legend.SetFillStyle( 0 )
        variable.root_legend.SetLineColorAlpha(0,0)
        variable.root_legend.SetShadowColor(0)
        variable.root_legend.Draw()
        # draw labels
        utils.draw_labels(self.options.label)
        utils.draw_cms_headlabel( label_right='#sqrt{s} = 13 TeV, L = %1.2f fb^{-1}' % self.options.intlumi )
        #
        c.cd()
        c.cd(2)
        (errorHist,systHist) = self.MakeStatProgression(hstack.GetStack().Last(),histDwSys, histUpSys)
        ROOT.SetOwnership(errorHist,0)
        ROOT.SetOwnership(systHist ,0)
        errorHist.GetXaxis().SetTitle(_htmp_.GetXaxis().GetTitle())
        errorHist.GetYaxis().SetTitle('Data/MC')
        errorHist.GetYaxis().CenterTitle(True)
        systHist.GetXaxis().SetTitle(_htmp_.GetXaxis().GetTitle())
        systHist.GetYaxis().SetTitle('Data/MC')
        systHist.GetYaxis().CenterTitle(True)
        self.customizeHisto(errorHist)
        systHist.Draw('E2')
        errorHist.Draw('E2')
        systHist.Draw('E2,same')
        errorHist.Draw('E2,same')
        ratioHist = None
        sig_and_bkg_ratio = []
        #
        if hdata==None:
            ratioHist = hstack.GetStack().Last().Clone('_temp_')
            ratioHist.Clear()
            ratioHist.SetLineColorAlpha(0,0)
            ratioHist.SetMarkerColorAlpha(0,0)
            ROOT.SetOwnership(ratioHist,0)
            ratioHist.GetXaxis().SetTitle(_htmp_.GetXaxis().GetTitle())
            ratioHist.GetYaxis().SetTitle(_htmp_.GetYaxis().GetTitle())
            if settings.ratio_draw_signal:
                for sig in histos:
                    sig_and_bkg = hstack.GetStack().Last().Clone('_temp_bkg_' + sig.GetName())
                    sig_and_bkg.Add(sig)
                    sig_and_bkg_ratio_ = self.makeRatio(sig_and_bkg,hstack.GetStack().Last())
                    ROOT.SetOwnership(sig_and_bkg_ratio_,0)
                    sig_and_bkg_ratio_.GetXaxis().SetTitle(_htmp_.GetXaxis().GetTitle())
                    sig_and_bkg_ratio_.GetYaxis().SetTitle(_htmp_.GetYaxis().GetTitle())
                    sig_and_bkg_ratio_.SetFillColorAlpha(0,0)
                    sig_and_bkg_ratio_.SetLineColor(sig.GetLineColor())
                    sig_and_bkg_ratio.append(sig_and_bkg_ratio_)
        else:
            ratioHist = self.makeRatio(hist1 = hdata, hist2 = hstack.GetStack().Last(), isdata = True)
            ROOT.SetOwnership(ratioHist,0)
            ratioHist.GetXaxis().SetTitle(_htmp_.GetXaxis().GetTitle())
            ratioHist.GetYaxis().SetTitle(_htmp_.GetYaxis().GetTitle())
            if settings.ratio_draw_signal:
                for sig in histos:
                    sig_and_bkg = hstack.GetStack().Last().Clone('_temp_bkg_' + sig.GetName())
                    sig_and_bkg.Add(sig)
                    sig_and_bkg_ratio_ = self.makeRatio(sig_and_bkg,hstack.GetStack().Last())
                    ROOT.SetOwnership(sig_and_bkg_ratio_,0)
                    sig_and_bkg_ratio_.GetXaxis().SetTitle(_htmp_.GetXaxis().GetTitle())
                    sig_and_bkg_ratio_.GetYaxis().SetTitle(_htmp_.GetYaxis().GetTitle())
                    sig_and_bkg_ratio_.SetFillColorAlpha(0,0)
                    sig_and_bkg_ratio_.SetLineColor(sig.GetLineColor())
                    sig_and_bkg_ratio.append(sig_and_bkg_ratio_)

        # concidence
        line = ROOT.TLine(ratioHist.GetXaxis().GetXmin(),1,ratioHist.GetXaxis().GetXmax(),1)
        line.SetLineColor(4)
        line.SetLineStyle(7)
        line.Draw()
        self.draw_categories(variable.boundaries,
                    miny=_htmp_.GetMinimum(),
                    maxy=_htmp_.GetMaximum())
        ROOT.SetOwnership(line,0)
        ratioHist.Draw('same')

        c.cd()
        #
        if variable.norm == True:
            histname = histname + '_norm'
        for form in settings.plot_formats :
            c.SaveAs( 'plots/' + histname + '.' + form)
