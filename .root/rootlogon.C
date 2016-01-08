/*  rootlogon.C
 *  Autor: Haddad Yacine
 *  Mail : yhaddad@cern.ch  
 *  All rights reserved.
 */

#include "TStyle.h"
#include <time.h>

TStyle* YacineStyle;

void declar_colors(){
  new TColor(120, 26/255., 188/255., 156/255.,"turquoise"     );
  new TColor(121, 46/255., 204/255., 113/255.,"emerland"      );
  new TColor(122, 52/255., 152/255., 219/255.,"peter-river"   );
  new TColor(123,155/255.,  89/255., 182/255.,"amethyst"      );
  new TColor(124, 52/255.,  73/255.,  94/255.,"wet-asphalt"   );
  new TColor(125, 22/255., 160/255., 133/255.,"green-sea"     );
  new TColor(126, 39/255., 174/255.,  96/255.,"nephritis"     );
  new TColor(127, 41/255., 128/255., 185/255.,"belize-hole"   );
  new TColor(128,142/255.,  68/255., 173/255.,"wisteria"      );
  new TColor(129, 44/255.,  62/255.,  80/255.,"midnight-blue" );
  new TColor(130,241/255., 196/255.,  15/255.,"sun-flower"    );
  new TColor(131,230/255., 126/255.,  34/255.,"carrot"        );
  new TColor(132,231/255.,  76/255.,  60/255.,"alizarin"      );
  new TColor(133,236/255., 240/255., 241/255.,"clouds"        );
  new TColor(134,149/255., 165/255., 166/255.,"concrete"      );
  new TColor(135,243/255., 156/255.,  18/255.,"orange"        );
  new TColor(136,211/255.,  84/255.,   0/255.,"pumpkin"       );
  new TColor(137,192/255.,  57/255.,  43/255.,"pomegranate"   );
  new TColor(138,189/255., 195/255., 199/255.,"silver"        );
  new TColor(139,127/255., 140/255., 141/255.,"asbestos"      );
}

void setYacineStyle(){
  YacineStyle = new  TStyle("YacineStyle", "Yacine Style");
  
  gInterpreter->ProcessLine(".! ps | grep root");
  
  // General
  YacineStyle->SetFillColor(10);
  YacineStyle->SetTitleFillColor(10);
  YacineStyle->SetTextFont(18); //@
  //YacineStyle->SetLineWidth(2); //@
  
  YacineStyle->SetPaperSize(20, 43);
  //
  ////  comment me
  //YacineStyle->SetPaperSize(20,20);
  //YacineStyle->SetScreenFactor(1.);
  //// For Canvas
  ////YacineStyle->SetCanvasPreferGL(true); // as a test
  YacineStyle->SetCanvasBorderMode(0);
  YacineStyle->SetCanvasColor(0);     // chaned fron kWhite to -1 
  YacineStyle->SetCanvasDefH(600);    //Height of canvas
  YacineStyle->SetCanvasDefW(600);    //Width of canvas
  YacineStyle->SetCanvasDefX(900);    //POsition on screen
  YacineStyle->SetCanvasDefY(20);
  //
  //// For Pad
  YacineStyle->SetPadBorderMode(0);
  YacineStyle->SetPadColor(0);        // chaned fron kWhite to -1 
  YacineStyle->SetPadGridX(false);
  YacineStyle->SetPadGridY(false);
  YacineStyle->SetGridColor(kGray);
  YacineStyle->SetGridStyle(3);
  YacineStyle->SetGridWidth(1);
  YacineStyle->SetPadTickX(1);  
  YacineStyle->SetPadTickY(1);
  
  //// for frame
  YacineStyle->SetFrameBorderMode(0);
  YacineStyle->SetFrameBorderSize(1);
  YacineStyle->SetFrameFillColor(0);   // chaned fron kWhite to -1  
  YacineStyle->SetFrameFillStyle(0);
  YacineStyle->SetFrameLineColor(1);
  YacineStyle->SetFrameLineStyle(1);
  YacineStyle->SetFrameLineWidth(1);   // default : 2 
  //
  //// For Hito
  YacineStyle->SetHistFillColor(0);    // changed from kWhite to -1
  YacineStyle->SetHistLineColor(kBlue+3);
  YacineStyle->SetHistLineStyle(0); //@
  YacineStyle->SetHistLineWidth(2); //@
  //YacineStyle->SetEndErrorSize(0);
  //YacineStyle->SetErrorX(0.);
  YacineStyle->SetMarkerColor(kBlue+3);
  YacineStyle->SetMarkerSize (0.7); //@
  //YacineStyle->SetMarkerStyle(20); //@
  //
  //// for function
  YacineStyle->SetFuncColor(kOrange-3);
  YacineStyle->SetFuncStyle(1);
  YacineStyle->SetFuncWidth(2);
  YacineStyle->SetOptFit(01100); 
  YacineStyle->SetFitFormat("3.4f"); //gStyle->SetFitFormat("3.1g");
  //
  //
  //// for the statistic box
  YacineStyle->SetOptStat(0);
  YacineStyle->SetStatBorderSize(0);
  YacineStyle->SetStatFont(43);
  YacineStyle->SetStatFontSize(25);
  YacineStyle->SetStatColor(0);
  YacineStyle->SetStatStyle(0);
  YacineStyle->SetStatW(0.25);
  YacineStyle->SetStatH(0.125);
  YacineStyle->SetStatX(0.90);
  YacineStyle->SetStatY(0.90);
  YacineStyle->SetStatBorderSize(0);
  //
  ////YacineStyle->SetStatX(1.0-YacineStyle->GetPadRightMargin()-0.02);
  ////YacineStyle->SetStatY(1.0-YacineStyle->GetPadTopMargin()-0.02);
  //
  //// Margins
  YacineStyle->SetPadBottomMargin(0.15);
  YacineStyle->SetPadTopMargin   (0.08); // def == 1.3
  YacineStyle->SetPadRightMargin (0.08); // def == 1.3
  YacineStyle->SetPadLeftMargin  (0.15);
  //
  //// Global Title
  YacineStyle->SetTitleFont  (43); //@
  YacineStyle->SetTitleSize  (25);//@
  YacineStyle->SetTitleColor (1);
  YacineStyle->SetTitleTextColor(1);
  YacineStyle->SetTitleFillColor(0);                // Changed -- JEK
  YacineStyle->SetTitleFontSize(25); //@
  YacineStyle->SetTitleBorderSize(0);
  YacineStyle->SetTitleAlign(33);
  YacineStyle->SetTitleX(0.8);
  YacineStyle->SetTitleY(0.95);
  //// Axis Titles
  YacineStyle->SetTitleColor (1 ,  "xyz");
  YacineStyle->SetTitleFont  (43,  "xyz");
  YacineStyle->SetTitleSize  (25,  "xyz");                  
  YacineStyle->SetTitleOffset(3 ,  "yz" );
  YacineStyle->SetTitleOffset(5 ,  "x"  );
  ////YacineStyle->SetTitleXOffset(1.08);
  ////YacineStyle->SetTitleYOffset(1.2);
  //
  //// Axis Labels
  ////YacineStyle->SetLabelColor (kBlack,"xyz");
  ////YacineStyle->SetLabelFont  (43,    "xyz");
  ////YacineStyle->SetLabelOffset(25,    "xyz");
  ////YacineStyle->SetLabelSize  (0.05,  "xyz");
  //
  //// Legend
  YacineStyle->SetLegendBorderSize(0);
  //
  //// Axis
  YacineStyle->SetAxisColor  (1    , "XYZ");
  YacineStyle->SetTickLength (0.03 , "XYZ");
  YacineStyle->SetNdivisions (508  , "XYZ");
  YacineStyle->SetStripDecimals(kTRUE);
  //
  //// Change for log plots
  YacineStyle->SetOptLogx(0);
  YacineStyle->SetOptLogy(0);
  YacineStyle->SetOptLogz(0);
  //
  YacineStyle->SetPalette(53,0); 

  declar_colors();
  //====> done
  YacineStyle->cd();
  gROOT->ForceStyle();
  gStyle->ls();

}


void rootlogon(){
  setYacineStyle();
}

// on the grid 
void onGrid(bool gridOn) {
  YacineStyle->SetPadGridX(gridOn);
  YacineStyle->SetPadGridY(gridOn);
}

// on the stat option
void onStatOpt(bool onStat)
{
  if(onStat) YacineStyle->SetOptStat("emr");
  else       YacineStyle->SetOptStat(0);
} 

void onFitOpt(bool onStat)
{
  if(onStat) YacineStyle->SetOptStat("emr");
  else       YacineStyle->SetOptStat(0);
} 

void onTranspacy(bool trans){
  YacineStyle->SetCanvasColor(-1);     // chaned fron kWhite to -1 
  YacineStyle->SetPadColor(-1);        // chaned fron kWhite to -1
  YacineStyle->SetFrameFillColor(-1); 
  YacineStyle->SetTitleFillColor(-1);
  YacineStyle->SetHistFillColor(-1);
  
}




