#!/usr/bin/python

import ROOT
import sys, os, glob, json, re
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
    if tree.GetEntries()==0:
        print 'ERROR: the tree is empty ...'
    # create list of variables
    varlist={}
    for var in tree.GetListOfLeaves():
        # print var.GetName()
        L    = tree.GetBranch(str(var))


        if '[' in var.GetTitle() and ']' in var.GetTitle():
            dim = [int(s) for s in re.findall('[-+]?\d*\.\d+|\d+', var.GetTitle().split('[')[1])]

            for idim in range(0, dim[0]):
                _var_ = var.GetTitle().replace('[{0:d}]'.format(dim[0]), '[{0:d}]'.format(idim))
                tree.Project("_h_"+_var_.split('[')[0],_var_)
                _h_  = ROOT.gDirectory.Get('_h_' + _var_.split('[')[0])
                nbin = _h_.GetNbinsX()
                xmin = _h_.GetXaxis().GetXmin()
                xmax = _h_.GetXaxis().GetXmax()
                hist = "({0:d},{1:1.3f},{2:1.3f})".format(nbin, xmin, xmax)
                varlist[_var_]={
                    'cut'  :'',
                    "hist" : hist,
                    "cut"  : "",
                    "blind": "",
                    "log"  : True ,
                    "norm" : False,
                    "title": var.GetTitle().replace('[{0:d}]'.format(dim[0]), '_{0:d}'.format(idim))
                }
                print ('variable: {0:25!s}'.format(var.GetTitle().replace('[{0:d}]'.format(dim[0]), '[{0:d}]'.format(idim))))
        else:

            tree.Project("_h_"+var.GetTitle(),var.GetTitle())
            _h_ = ROOT.gDirectory.Get('_h_'+var.GetTitle())
            nbin = _h_.GetNbinsX()
            xmin = _h_.GetXaxis().GetXmin()
            xmax = _h_.GetXaxis().GetXmax()
            hist = "({0:d},{1:1.3f},{2:1.3f})".format(nbin, xmin, xmax)
            varlist[var.GetTitle()]={
                'cut'  :'',
                "hist" : hist,
                "cut"  : "",
                "blind": "",
                "log"  : True ,
                "norm" : False,
                "title": var.GetTitle()
            }
            print ('variable: {0:25!s}'.format(var.GetTitle()))
        # create a json file
    # samples     = json.loads(open('samples.json').read())
    samples_new = {}
    sample_tree = {'name':treename}
    selection   = {'cutflow':''}
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
