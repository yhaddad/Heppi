#!/usr/bin/python

import ROOT # needed
import os, sys, glob, sys


samples={}
variables={}

def read_plotcard(jsonfile, datadir):
    
    
def draw_variable():
    

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
    parser.add_option("-t", "--tree", dest="treename",default='VBFMVADumper/*VBFDiJet',
                      help="dumper tree that you want to use", metavar="FILE")
    parser.add_option("-a", "--all", 
                      action="store_false", dest="draw_all", default=False,
                      help="draw all the variables specified in the plotcard")
    parser.add_option("-v", "--variable",#callback=check_var,
                      dest="variable",default="dijet_leadPt",
                      help="name of the variable you want to draw")

    #print '--- running with the follwing options ---'
    #print '-----------------------------------------'
    return parser.parse_args()

if __name__ == "__main__":
    (options, args) = get_options()
    

    
