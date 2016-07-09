#include <iostream>
#include <vector>
#include <string>
#include <map>

#include "RooAbsReal.h"
#include "RooGaussian.h"
#include "RooAddPdf.h"
#include "RooDataSet.h"
#include "RooDataHist.h"
#include "RooRealVar.h"
#include "RooFitResult.h"


void buildSumOfGaussians(string name, int nGaussians, bool recursive, bool forceFracUnity){
    for (unsigned int i=0; i<allMH_.size(); i++){
    int mh = allMH_[i];
    MH->setConstant(false);
    MH->setVal(mh);
    MH->setConstant(true);
    RooArgList *gaussians = new RooArgList();
    RooArgList *coeffs = new RooArgList();
    map<string,RooRealVar*> tempFitParams;
    map<string,RooAbsReal*> tempFitUtils;
    map<string,RooGaussian*> tempGaussians;

    for (int g=0; g<nGaussians; g++){
      RooRealVar *dm    = new RooRealVar(Form("dm_mh%d_g%d",mh,g),Form("dm_mh%d_g%d",mh,g),0.1,-8.,8.);
      RooAbsReal *mean  = new RooFormulaVar(Form("mean_mh%d_g%d",mh,g),Form("mean_mh%d_g%d",mh,g),"@0+@1",RooArgList(*MH,*dm));
      RooRealVar *sigma = new RooRealVar(Form("sigma_mh%d_g%d",mh,g),Form("sigma_mh%d_g%d",mh,g),2.,0.4,20.);
      RooGaussian *gaus = new RooGaussian(Form("gaus_mh%d_g%d",mh,g),Form("gaus_mh%d_g%d",mh,g),*mass,*mean,*sigma);
      tempFitParams.insert(pair<string,RooRealVar*>(string(dm->GetName()),dm));
      tempFitParams.insert(pair<string,RooRealVar*>(string(sigma->GetName()),sigma));
      tempFitUtils.insert(pair<string,RooAbsReal*>(string(mean->GetName()),mean));
      tempGaussians.insert(pair<string,RooGaussian*>(string(gaus->GetName()),gaus));
      gaussians->add(*gaus);
      if (g<nGaussians-1) {
        RooRealVar *frac = new RooRealVar(Form("frac_mh%d_g%d",mh,g),Form("frac_mh%d_g%d",mh,g),0.1,0.01,0.99);
        tempFitParams.insert(pair<string,RooRealVar*>(string(frac->GetName()),frac));
        coeffs->add(*frac);
      }
      if (g==nGaussians-1 && forceFracUnity){
        string formula="1.";
        for (int i=0; i<nGaussians-1; i++) formula += Form("-@%d",i);
        RooAbsReal *recFrac = new RooFormulaVar(Form("frac_mh%d_g%d",mh,g),Form("frac_mh%d_g%d",mh,g),formula.c_str(),*coeffs);
        tempFitUtils.insert(pair<string,RooAbsReal*>(string(recFrac->GetName()),recFrac));
        coeffs->add(*recFrac);
      }
    }
    assert(gaussians->getSize()==nGaussians && coeffs->getSize()==nGaussians-(1*!forceFracUnity));
    RooAddPdf *tempSumOfGaussians = new RooAddPdf(Form("%s_mh%d",name.c_str(),mh),Form("%s_mh%d",name.c_str(),mh),*gaussians,*coeffs,recursive);
    sumOfGaussians.insert(pair<int,RooAddPdf*>(mh,tempSumOfGaussians));
    fitParams.insert(pair<int,map<string,RooRealVar*> >(mh,tempFitParams));
    fitUtils.insert(pair<int,map<string,RooAbsReal*> >(mh,tempFitUtils));
    initialGaussians.insert(pair<int,map<string,RooGaussian*> >(mh,tempGaussians));
  }
}
