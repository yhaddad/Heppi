#!/bin/bash

./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_mass --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dijet_mva --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_mva --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_dijet_MVA --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v leadPho_PToM --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v sublPho_PToM --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_leadEta --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_subEta --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_leadIDMVA --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_subIDMVA --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_vtxprob --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_CosPhi --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_sigmarv --label qcd-param-ptweight-original
./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_sigmawv --label qcd-param-ptweight-original

#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_mass --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dijet_mva --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_mva --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_dijet_MVA --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v leadPho_PToM --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v sublPho_PToM --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_leadEta --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_subEta --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_leadIDMVA --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_subIDMVA --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_vtxprob --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_CosPhi --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_sigmarv --label qcd-param-ptweight-full
#./plot -r plotcard/vbf_plotcard_hgg.json -s /afs/cern.ch/work/e/escott/public/VBFStudies/ -v dipho_sigmawv --label qcd-param-ptweight-full

#cp plots/* ~/www/ICHEP16/SplitVtx/
#cp plots/* ~/www/ICHEP16/SplitWiderBins/
cp plots/* ~/www/ICHEP16/SplitFull/
rm plots/*
