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

class model_build {
  public:
    model_build(RooRealVar *massVar, RooRealVar *MHvar, int mhLow, int mhHigh, std::vector<int> skipMasses, bool binnedFit, int bins);
    ~InitialFit();

    void sum_gauss(std::string name, int nGaussians, bool recursive=false, bool forceFracUnity=false);
  private:
    RooRealVar *mass;
    RooRealVar *MH;
    std::map<int,RooAddPdf*> sumOfGaussians;
    std::map<int,std::map<std::string,RooRealVar*> > fitParams;
    std::map<int,std::map<std::string,RooAbsReal*> > fitUtils;
    std::map<int,std::map<std::string,RooGaussian*> > initialGaussians;
    std::map<int,RooFitResult*> fitResults;
    int mhLow_;
    int mhHigh_;
		std::vector<int> skipMasses_;
    std::vector<int> allMH_;
    std::vector<int> getAllMH();
		bool skipMass(int mh);
    int verbosity_;
    bool binnedFit_;
    int bins_;

};
