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
                          "QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8"],
     "Data" : [ "DoubleEG_sethzenz-RunIISpring15-FinalPrompt-BetaV7-25ns-Spring15BetaV7-v0-Run2015D-PromptReco-v4",
                "DoubleEG_sethzenz-RunIISpring15-Prompt-BetaV7-25ns-Spring15BetaV7-v0-Run2015D-PromptReco-v4",
           	"DoubleEG_sethzenz-RunIISpring15-ReMiniAOD-BetaV7-25ns-Spring15BetaV7-v0-Run2015C_25ns-05Oct2015-v1",
		"DoubleEG_sethzenz-RunIISpring15-Prompt-SilverNotGold-BetaV7-25ns-Spring15BetaV7-v0-Run2015D-PromptReco-v4",
		"DoubleEG_sethzenz-RunIISpring15-ReMiniAOD-SilverNotGold-BetaV7-25ns-Spring15BetaV7-v0-Run2015D-05Oct2015-v1" ]
}

samples_2 =[
    "VBFHToGG_M-125_13TeV_powheg_pythia8"                                     ,
    "GluGluHToGG_M-125_13TeV_powheg_pythia8"                                  ,
    "VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8"                          ,
    "ttHJetToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8"                      ,
    "DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8"                 ,
    "GJet_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8" ,
    "GJet_Pt-20to40_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8"  ,
    "DiPhotonJetsBox_MGG-80toInf_13TeV-Sherpa"                                ,
    "QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8"   ,  
    "QCD_Pt-30toInf_DoubleEMEnriched_MGG-40to80_TuneCUETP8M1_13TeV_Pythia8"   ,
    "QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8"  ,
    "DoubleEG_sethzenz-RunIISpring15-ReMiniAOD-SilverNotGold-BetaV7-25ns"
]



def merge_sample():
    for sam in samples:
        print '---------------------------------------------------'
        flist = glob.glob( '*.root')
        mergefname = ''
        outdir     = 'merged/'
        allfiles   = ''
        os.system('mkdir -p ' +  outdir)
        for f in flist:
            for p in samples[sam]:
                if p in f:
                    print '\t sample:',sam,'  files::', f
                    mergefname = f.replace('_'+f.split('_')[-1:][0],'.root')
                    allfiles   = allfiles +' '+ f 
                    cmd = 'hadd -f ' + outdir + mergefname + ' ' + allfiles
        os.system(cmd)
        os.system(' mv merged/output_QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8.root merged/output_QCD_DoubleEMEnriched_TuneCUETP8M1_13TeV_Pythia8.root')
        os.system(' mv merged/output_GJet_DoubleEMEnriched_TuneCUETP8M1_13TeV_Pythia8.root merged/output_DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8.root')
        os.system('mv merged/output_DoubleEG_* merged/output_DoubleEG_sethzenz-RunIISpring15-ReMiniAOD-SilverNotGold-BetaV7-25ns.root')
def merge_sample_2():
    for sam in samples_2:
        print '---------------------------------------------------'
        flist = glob.glob( '*' + sam + '*')
        mergefname = ''
        outdir     = 'merged_test/'
        os.system('mkdir -p '+outdir )
        allfiles   = ''
        mergefname = ''
        for f in flist:
            #print '\t sample:',sam,'  files::', f
            mergefname = f.replace('_'+f.split('_')[-1:][0],'.root')
            allfiles   = allfiles +' '+ f 
            cmd = 'hadd -f ' + outdir + mergefname + ' ' + allfiles
        print "merged file -->> ", mergefname
        os.system(cmd)


merge_sample()
