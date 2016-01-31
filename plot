#!/usr/bin/python
#from __future__ import print_function

from optparse   import OptionParser
from heppi      import heppi
from termcolor  import colored
import ROOT, logging, sys, logging, time 

#from etaprogress.progress import ProgressBar, ProgressBarBits, ProgressBarBytes, ProgressBarWget, ProgressBarYum

logging.basicConfig(format=colored('%(levelname)s:',attrs = ['bold'])
                    + colored('%(name)s:','blue') + ' %(message)s')
logger = logging.getLogger('heppi')
logger.setLevel(level=logging.INFO)

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
                      help="Label added in the plot file names")
    parser.add_option("--title", dest="title_on_plot",default=[],
                      help="replace labels name from the plot card")
    parser.add_option('--verbose', dest='verbose', action='count',
                     help="Increase verbosity (specify multiple times for more)")
    parser.add_option("--cut-card", dest="cut_card",default='',
                      help="Specify all the cut through a cut-card. This might be included also in the plotcard. Check the documentation")
    return parser.parse_args()

if __name__ == "__main__":
    (opt, args) = get_options()
    heppi.options       = opt
    heppi.allnormhist   = opt.allnormhist
    heppi.allloghist    = opt.allloghist
    heppi.sampledir     = opt.sampledir
    heppi.cut_card      = opt.cut_card
    heppi.title_on_plot = opt.title_on_plot.split(',')
    
    log_level = logging.WARNING # default
    if opt.verbose == 1:
        log_level = logging.INFO
    elif opt.verbose >= 2:
        log_level = logging.DEBUG
    
    #logging.basicConfig(level=log_level)
    
    ROOT.gROOT.ProcessLine(".x .root/rootlogon.C")
    if opt.display:
        ROOT.gROOT.SetBatch( ROOT.kFALSE ) 
    else:
        ROOT.gROOT.SetBatch( ROOT.kTRUE  )
        ROOT.gErrorIgnoreLevel = ROOT.kError
    heppi.read_plotcard(heppi.options.plotcard)
    heppi.print_cutflow()
    
    heppi.book_trees('')
    heppi.test_tree_book()    


    #files = {
    #    'CentOS-7.0-1406-x86_64-DVD.iso': 10 ,
    #    'CentOS-7.0-1406-x86_64-Everything.iso': 15 ,
    #    'md5sum.txt': 5,
    #}
    #for file_name, file_size in files.items():
    #    bar = ProgressBarYum(file_size, file_name)
    #    for i in range(0, file_size + 1):
    #        bar.numerator = i
    #        print(bar, end='\r')
    #        sys.stdout.flush()
    #        time.sleep(0.25)
    #    bar.numerator = file_size
    #    bar.force_done = True
    #    print(bar)
    
    if opt.draw_all and opt.variable == '':
        logger.info(colored(
            ('(%i) booked variables will be drawn ::\r' % len(heppi.variables)),
            'red', attrs=['bold']
        ))
        for var in heppi.variables:
            heppi.draw_instack(var,heppi.options.label,heppi.selection['title'])
    else:
        if opt.variable != '':
            heppi.draw_instack(opt.variable,heppi.options.label,heppi.selection['title'])
            if opt.display:
                raw_input('... Press any key to exit ...')
        else:
            logging.error('please specify the variable you wnat to plot ...')
    
            
