data = {
    "ggh_125" : [0.733,0.740,0.745],
    "qcd"     : [0.891,0.908,0.899],
    "gjet"    : [0.889,0.892,0.896]
}


import ROOT



xx = [0.02, 0.03, 0.04 ]
mul = ROOT.TMultiGraph()
count = 1
for sam in  data:
    gr =  ROOT.TGraph()
    for x in xx:
        gr.SetPoint(xx.index(x),x, data[sam][xx.index(x)])

    gr.SetLineColor(count)
    count = count+1
    mul.Add(gr)
    

mul.Draw("APL")
raw_input()
