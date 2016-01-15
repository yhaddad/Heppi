#!/usr/bin/python
from optparse import OptionParser
import heppi 

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
                      help="label to the produced plots")
    
    return parser.parse_args()

if __name__ == "__main__":
    (opt, args) = get_options()
    options  = opt
    ROOT.gROOT.SetBatch( opt.display ) 
    
    allnormhist = options.allnormhist
    allloghist  = options.allloghist
    sampledir   = options.sampledir
    
    ROOT.gROOT.ProcessLine(".x .rootlogon.C")
    heppi.read_plotcard(options.plotcard)
    heppi.print_cutflow()
    
    if opt.variable == "":
        for var in variables:
            draw_instack(var,options.label,selection['title'])
    
    
