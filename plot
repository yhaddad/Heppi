#!/usr/bin/python
from optparse import OptionParser
import logging
import heppi 
import ROOT

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
                      Specify the detrectory where the trees are. 
                      example: --filedir /data/trees
                      """)
    parser.add_option("-t", "--tree",
                      dest="treename", default='vbfTagDumper/trees/*VBFDiJet',
                      help="Tree path in the root file that you want to use")
    parser.add_option("-a", "--all", 
                      action="store_true", dest="draw_all", default=False,
                      help="draw all the variables specified in the plotcard")
    parser.add_option("-d", "--display", 
                      action="store_false", dest="display", default=False,
                      help="draw all the variables specified in the plotcard")
    parser.add_option("-v", "--variable",
                      dest="variable",default="",
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
                      help="Label added in the plot file names")
    parser.add_option('--verbose', dest='verbose', action='count',
                     help="Increase verbosity (specify multiple times for more)")
    return parser.parse_args()

if __name__ == "__main__":
    (opt, args) = get_options()
    heppi.options  = opt
    
    heppi.allnormhist = opt.allnormhist
    heppi.allloghist  = opt.allloghist
    heppi.sampledir   = opt.sampledir
    
    log_level = logging.WARNING # default
    if opt.verbose == 1:
        log_level = logging.INFO
    elif opt.verbose >= 2:
        log_level = logging.DEBUG

    # Set up basic configuration, out to stderr with a reasonable default format.
    logging.basicConfig(level=log_level)
  
    ROOT.gROOT.ProcessLine(".x .root/rootlogon.C")
    if opt.display:
        ROOT.gROOT.SetBatch( ROOT.kFALSE ) 
    else:
        ROOT.gROOT.SetBatch( ROOT.kTRUE  ) 
    heppi.read_plotcard(heppi.options.plotcard)
    heppi.print_cutflow()
    
    if opt.draw_all and opt.variable == '':
        for var in heppi.variables:
            heppi.draw_instack(var,heppi.options.label,heppi.selection['title'])
    else:
        if opt.variable != '':
            heppi.draw_instack(opt.variable,heppi.options.label,heppi.selection['title'])
        else:
            logging.error('please specify the variable you wnat to plot ...')
            
