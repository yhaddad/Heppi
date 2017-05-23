#!/usr/bin/python

import os, sys, glob

samples ={
    "vbf_m125"        : [ "VBFHToGG_M-125_13TeV_powheg_pythia8" ],
    "ggf_m125"        : [ "GluGluHToGG_M-125_13TeV_powheg_pythia8"],
    "vh_m125"         : [ "VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8"],
    "tth_m125"        : [ "ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8"],
    "dy_toll_m50"     : [ "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8"],
    "gamJet"          : [ "GJet_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8",
                          "GJet_Pt-20to40_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8"],
    "gamgamjetbox"    : [ "DiPhotonJetsBox_MGG-80toInf_13TeV-Sherpa"],
    "qcd"             : [ "QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8",
                          "QCD_Pt-30toInf_DoubleEMEnriched_MGG-40to80_TuneCUETP8M1_13TeV_Pythia8",
                          "QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8"]
}

outdir     = 'merged/'
os.system('mkdir -p ' + outdir)

for sam in samples:
    print '---------------------------------------------------'
    flist = glob.glob( '*.root')
    mergefname = ''
    allfiles   = ''
    for f in flist:
        for p in samples[sam]:
            if p in f:
                print '\t sample:',sam,'  files::', f
                mergefname = f.replace('_'+f.split('_')[-1:][0],'.root')
                allfiles   = allfiles +' '+ f 
    cmd = 'hadd -f ' + outdir + mergefname + ' ' + allfiles
    os.system(cmd)

# make the file name more understandable

os.system('mv ')
os.system('mv ')
