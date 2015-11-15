# configuration file
#!/usr/bin/python
import ROOT
"""

This is a configuration file containing 
the code colors in hex, and translated 
in the ROOT format.

The colors has been inspired from :
http://flatuicolors.com/

you can use the follwing command to 
transform the HEX color format to ROOT
format : ROOT.TColor.GetColor(hexcolor)

"""

hexcolor = {
    "turquoise"    :"#1abc9c",
    "emerald"      :"#2ecc71",
    "peter_river"  :"#3498db",#ggf
    "amethyst"     :"#9b59b6",
    "wet_asphalt"  :"#34495e",
    "green_sea"    :"#16a085",
    "nephritis"    :"#27ae60",
    "belize_hole"  :"#2980b9",
    "wisteria"     :"#8e44ad",
    "midnight_blue":"#2c3e50",#gg+gj
    "sun_flower"   :"#f1c40f",#QCD (jj)
    "carrot"       :"#e67e22",
    "alizarin"     :"#e74c3c",
    "clouds"       :"#ecf0f1",
    "concrete"     :"#95a5a6",
    "orange"       :"#f39c12",
    "pumpkin"      :"#d35400",
    "pomegranate"  :"#c0392b",# VBF signal
    "silver"       :"#bdc3c7",
    "asbestos"     :"#7f8c8d"
}
rgbcolor = {
    "turquoise"     :[26 , 188, 156],
    "emerland"      :[46 , 204, 113],
    "peter-river"   :[52 , 152, 219],
    "amethyst"      :[155, 89 , 182],
    "wet-asphalt"   :[52 , 73 , 94 ],
    "green-sea"     :[22 , 160, 133],
    "nephritis"     :[39 , 174, 96 ],
    "belize-hole"   :[41 , 128, 185],
    "wisteria"      :[142, 68 , 173],
    "midnight-blue" :[44 , 62 , 80 ],
    "sun-flower"    :[241, 196, 15 ],
    "carrot"        :[230, 126, 34 ],
    "alizarin"      :[231, 76 , 60 ],
    "clouds"        :[236, 240, 241],
    "concrete"      :[149, 165, 166],
    "orange"        :[243, 156, 18 ],
    "pumpkin"       :[211, 84 , 0  ],
    "pomegranate"   :[192, 57 , 43 ],
    "silver"        :[189, 195, 199],
    "asbestos"      :[127, 140, 141]}

usercolor = {}
def declar_color():
    with open('./.color-for-root.C','w') as g:
        ci = 1500
        g.write('{\n')
        for c in rgbcolor:
            col = ROOT.TColor(ci,
                              rgbcolor[c][0],
                              rgbcolor[c][1],
            rgbcolor[c][2]) 
            line  = ('TColor *c_%s  = new TColor(%i,%d,%d,%d);'
                   % ( c, ci,
                       rgbcolor[c][0]/255.,
                       rgbcolor[c][1]/255.,
                       rgbcolor[c][2]/255.)
            )
            ci = ci + 1;
            usercolor[c]=ci
            g.write(line + '\n')
        g.write('}')
        
#usercolor={
#    "vbf_m125"           : 99,
#    "ggf_m125"           : 215,
#    "qcd"                : 91,
#    "gamgam"             : 65,
#    "gamJet"             : 51,
#    "dy_toll_m50"        : 85,
#}
