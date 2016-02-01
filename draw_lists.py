import ROOT
ROOT.gROOT.ProcessLine(".x .root/rootlogon.C")
from collections import OrderedDict

data = OrderedDict()

data["VBF vs GGF"            ]= [0.733,0.740,0.745]
data["VBF vs QCD"            ]= [0.891,0.908,0.899]
data["VBF vs #gamma+jet"     ]= [0.889,0.892,0.896]
data["VBF vs #gamma#gamma"   ]= [0.867,0.867,0.868]


xx    = [0.02, 0.03, 0.04 ]
color = [131, 135, 122, 127]
#titles = ['VBF vs GGF', 'VBF vs QCD', 'VBF vs #gamma+jet']
mul   = ROOT.TMultiGraph()
count = 0

legend  = ROOT.TLegend( 0.55, 0.5,
                        (0.9 - ROOT.gStyle.GetPadRightMargin()),
                        (0.7 - ROOT.gStyle.GetPadTopMargin()))
legend.SetTextAlign( 12 )
legend.SetTextFont ( 42 )
legend.SetTextSize ( 0.03 )
legend.SetLineColor( 0 )
legend.SetFillColor( 0 )
legend.SetFillStyle( 0 )
legend.SetLineColorAlpha(0,0)
legend.SetShadowColor(0)

c = ROOT.TCanvas('c_Opt_','MVA',600,600)
c.cd()

for sam in  data:
    gr =  ROOT.TGraph()
    for x in xx:
        gr.SetPoint(xx.index(x),x, data[sam][xx.index(x)])
        
    gr.SetLineColor(color[count])
    gr.SetLineWidth(3)
    gr.SetMarkerColor(color[count])
    gr.SetMarkerStyle(20 )
    gr.SetMarkerSize (1.0)
    legend.AddEntry(gr, sam , 'lep')
    count = count+1
    mul.Add(gr)

mul.Draw("APL")
mul.SetTitle(";RMS cut; ROC-Inetgral")
mul.GetYaxis().SetRangeUser(0.6,1.0)
mul.GetXaxis().SetTitleSize(25)
mul.GetYaxis().SetTitleSize(25)
mul.GetXaxis().SetTitleOffset (1.2)
mul.GetYaxis().SetTitleOffset (1.2)
c.Update()
mul.Draw("APL")

legend.Draw()
c.SaveAs('plots/rms_performance.pdf')
c.SaveAs('plots/rms_performance.png')
#raw_input()
