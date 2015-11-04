#!/usr/bin/python

import ROOT # needed
import os, sys, glob, sys, json
import logging

samples={}
variables={}

def read_plotcard(plotcard):
    config = json.loads(open(plotcard).read())
    for key in config:
        
        if 'variables' in key:
            logging.debug(' ---- variables ----')
            for var in config[key]:
                variables[var] = config[key][var]
                logging.debug(' -- ' + var + '\t',config[key][var]['hist'])
        if 'processes' in key:
            logging.debug(' ---- processes ----')
            for proc in config[key]:
                logging.debug(' -- ' + proc + '\t',config[key][proc])
                samples[proc] = config[key][proc]
        logging.debug(' -------------------')
                
def draw_variable(variable):
    print ' -- ', variable,'\t',variables[variable]
    # create a list of histogram for each process
    for proc in samples:
        print '\t', proc, '\t', samples[proc]
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

    #parser.add_option("-l", "--log",#callback=check_var,
    #                  dest="loglevel",default="INFO",
    #                  help="debug level [INFO, DEBUG, WARNING]")
    #print '--- running with the follwing options ---'
    #print '-----------------------------------------'
    return parser.parse_args()

if __name__ == "__main__":
    (options, args) = get_options()
    # reading the plotcard from json
    #logging.basicConfig(level=options.loglevel)
    

    read_plotcard(options.plotcard)
    draw_variable('jet3_pt')
    
