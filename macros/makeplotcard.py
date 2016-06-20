#!/usr/bin/python

import ROOT
import sys, os, glob, json
#import colors

version=0.1

# --------------------
# read arguments
# --------------------
def create_json(rootfile='file.root', treename='', jout=''):
    """
    Create a json template file for
    plotng all the branches in a given
    tree
    """
    dumper = treename.split("*")[0]
    treerf = treename.split("*")[1]
    print 'dumper', dumper
    print 'treerf', treerf
    root = ROOT.TFile.Open(rootfile)
    # tree_dir = root.Get(dumper)
    #
    # treenm = ''
    # for a in tree_dir.GetListOfKeys():
    #     if treerf in a.GetName():
    #         treenm = a.GetName()
    tree = ROOT.gDirectory.Get(dumper+treerf)
    print dumper+treerf
    #if tree.GetEntries()==0:
    #    print 'ERROR: the tree is empty ...'
    # create list of variables
    varlist={}
    for var in tree.GetListOfLeaves():
        L    = tree.GetBranch(str(var))
        xmin = L.GetMaximum()
        print xmin
        print ('variable: %25s' % var.GetTitle())
        varlist[var.GetTitle()]={
            'cut'  :'',
            "hist" : "(100,0,10)",
            "cut"  : "",
            "blind": "",
            "log"  : True ,
            "norm" : False,
            "title": ""
        }
        # create a json file
    # samples     = json.loads(open('samples.json').read())
    samples_new = {}
    sample_tree = {'name':treename}
    selection   = {'cutflow':''}
    # count       = 0
    # for sam in samples:
    #     if 'processes' in sam:
    #         for proc in samples[sam]:
    #             samples_name = samples[sam][proc][0]
    #             samples_new[proc] = {'name': samples_name, 'color':count, 'title':proc, 'label':'', 'order':count}
    #             count = count + 1

    with open(jout, "w") as file:
        json.dump({'variables':varlist, 'processes':{}, 'option':{}}, file, indent=2)
        file.close()
# --------------------
# read arguments
# --------------------
from optparse import OptionParser
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-r", "--load", dest="rootfile",default='rootfile.root',
                      help="create a plot card from tree", metavar="FILE")
    parser.add_option("-t", "--tree", dest="treename",default='VBFMVADumper/*VBFDiJet',
                      help="Dumper tree that you wnat to plot", metavar="FILE")
    parser.add_option("-o", "--out", dest="jsonfile",default="plotcard.json",
                      help="specify output json file")

    (options, args) = parser.parse_args()
    create_json( options.rootfile,
                 options.treename,
                 options.jsonfile)
