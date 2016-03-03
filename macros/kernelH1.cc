#ifndef HISTKDE_CC
#define HISTKDE_CC

#include <TH1.h>
#include <TF1.h>
#include <TKDE.h>
#include <TGraph.h>
#include "Math/Minimizer.h"
#include "Math/Factory.h"
#include "Math/Functor.h"
#include "TRandom2.h"
#include "TError.h"


class H1kernel
{
private:
  //! private declarations
  TKDE * _kde;
  double  _rho;
  double  _np;
public:
  H1kernel(TH1 *histo, double rho=1.0, int npoints=1000):
    _rho(rho), _np(npoints)
  {
    int n       =  histo->GetNbinsX();
    double xmin =  histo->GetXaxis()->GetXmin(); 
    double xmax =  histo->GetXaxis()->GetXmax(); 
    std::vector<double> data   (n);
    std::vector<double> weights(n);
    for (int ibin=0; ibin < n; ibin++ ) {
      data[ibin]    = histo->GetBinCenter (ibin);
      weights[ibin] = histo->GetBinContent(ibin);
    }
    _kde = new TKDE(n, &data[0],&weights[0], xmin, xmax, "", rho);
  }
  virtual ~H1kernel()
  {
    delete  _kde;
    //delete  _histo;
  }
  
  TF1 * function()      {return _kde->GetFunction(_np);}
  TF1 * function_upper(){return _kde->GetUpperFunction(0.684);}
  TF1 * function_lower(){return _kde->GetLowerFunction(0.684);}
  
  void Draw(TString option) {_kde->Draw(option);}
};

class  function_cdf
{
private:
  //! private declarations
  TF1 * _function;
public:
  function_cdf(TF1 *function) : _function(function)
  {/*_function = (TF1*)function->Clone();*/}
  TF1 * function()
  {
    TString name(_function->GetName());
    return new TF1( name + "_cdf",[&](double*x, double *p){
	return _function->Integral(_function->GetXmin(),x[0]);
      },
      _function->GetXmin(),_function->GetXmax(), 0);
  }
  virtual ~function_cdf()
  {/*delete _function;*/}
};

class zfom 
{
private:
  //! private declarations
  TF1    * _fsig;
  TF1    * _fbkg;
  int      _ncat;
public:
  zfom(TF1* sig, TF1* bkg, int ncat=2): _fsig(sig), _fbkg(bkg), _ncat(ncat)
  {/*_function = (TF1*)function->Clone();*/}
  
  double Eval(const double * x) const 
  {
    double z = (_fsig->Integral(-1,x[0]) * _fsig->Integral(-1,x[0]))/_fbkg->Integral(-1,x[0]);
    for (int i = 0; i < _ncat-2; i++ )
      {
	z += (_fsig->Integral(x[i],x[i+1]) * _fsig->Integral(x[i],x[i+1]))/_fbkg->Integral(x[i],x[i+1]);
      }
    z += (_fsig->Integral(x[_ncat-1],1) * _fsig->Integral(x[_ncat-1],1))/_fbkg->Integral(x[_ncat-1],1);
    return z;
  }
};

class optimizer
{
  
private:
  ROOT::Math::Minimizer * _min;

  TF1    * _fsig;
  TF1    * _fbkg;
public:
  optimizer(TString name,TF1* sig, TF1* bkg, int ncat=2): _fsig(sig), _fbkg(bkg)
  {
    _min = ROOT::Math::Factory::CreateMinimizer(name.Data(), "Minuit2");
    _min->SetMaxFunctionCalls(1000000); // for Minuit/Minuit2
    _min->SetMaxIterations(10000);  // for GSL
    _min->SetTolerance(0.001);
    _min->SetPrintLevel(1);
    zfom myfom(_fsig, _fbkg, ncat);
    ROOT::Math::Functor f(  &myfom, &zfom::Eval, ncat);
    std::vector<double> initbounds(ncat);
    std::vector<double> variable  (ncat);
    double minbound = -1;
    for (int i=1; i < ncat+1 ; i++)
      {
	initbounds[i-1] = minbound + i*(2.0/ncat);
	TRandom2 r(1);
	variable[i] = r.Uniform(-1,1);
      }

    _min->SetFunction(f);
    for (int i = 0; i < ncat-2; i++ )
      {
	_min->SetVariable(i,Form("bound_%i",i),variable[i], initbounds[i]);
      }
    _min->Minimize();
    const double *xs = _min->X();
    std::cout << "Minimum: f(" ;
    for (int i = 0; i < ncat-2; i++ )
      std::cout << xs[i] << ",";
    std::cout<< ") :: " <<  _min->MinValue()  << std::endl;
  }
  virtual ~optimizer();
};


class perfML
{
  
private:
  TF1    * _fsig;
  TF1    * _fbkg;
public:
  perfML (TF1 * sig_cdf, TF1 * bkg_cdf): _fsig(sig_cdf), _fbkg(bkg_cdf){}
  TGraph * getROC(TString name, int steps=500)
  {
    TGraph *gr = new TGraph();
    gr->SetName (name);
    gr->SetTitle(";#varepsilon_{background};#varepsilon_{signal}");
    double xmin =  _fsig->GetXmin();
    double step = (_fsig->GetXmax() - _fbkg->GetXmin())/steps;
    gr->SetPoint(0, 1, 1);
    for (int i=1; i< steps; i++){
      double x = xmin + i* step;
      gr->SetPoint(i, 1 - _fbkg->Eval(x), 1 - _fsig->Eval(x));
      //std::cout << "\t x == "<< x << std::endl;
    }
    gr->SetPoint(steps+1, 0, 0);
    std::cout << " ROC (" << name << ") Integral :=" << gr->Integral() << std::endl;
    return gr;
  }
  /*
    These functions represents figures of merit to optiimise bundaries
    in some ML output distribution
  */
  TF1 * getAMS(TString name, double ws=1, double wb=1)
  {
    TF1 *f = new TF1( name + "_cdf",[&](double*x, double *p){
	double s = p[0] * (1-_fsig->Eval(x[0]));
	double b = p[1] * (1-_fbkg->Eval(x[0]));
	if (_fbkg->Eval(x[0]) != 0){
	  return (1-_fsig->Eval(x[0])) * (1-_fsig->Eval(x[0]))/(1-_fbkg->Eval(x[0]));
	}else{
	  return 0.0;
	}
      },
      _fsig->GetXmin(),_fsig->GetXmax(), 2);
    f->SetParameters(ws,wb);
    return f;
  }
  
  TF1 * getAMS2(TString name, double ws=1, double wb=1)
  {
    TF1 *f =  new TF1( name + "_cdf",[&](double*x, double *p){
	double s = p[0] * (1-_fsig->Eval(x[0]));
	double b = p[1] * (1-_fbkg->Eval(x[0]));
	if ( (s + b ) != 0){
	  return s * s/( s + b );
	}else{
	  return 0.0;
	}
      },
      _fsig->GetXmin(),_fsig->GetXmax(), 2);
    f->SetParameters(ws,wb);
    return f;
  }
  virtual ~perfML(){}
};

#endif /* HISTKDE_CC */
