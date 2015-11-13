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

# translate in ROOT
rootcolor={
    "alizarin"      :1180,
    "amethyst"      :1181,
    "asbestos"      :1182,
    "belize_hole"   :1183,
    "carrot"        :1184,
    "clouds"        :19,
    "concrete"      :1185,
    "emerald"       :1186,
    "green_sea"     :1187,
    "midnight_blue" :1188,
    "nephritis"     :1189,
    "orange"        :1190,
    "peter_river"   :1191,
    "pomegranate"   :1192,
    "pumpkin"       :1193,
    "silver"        :1194,
    "sun_flower"    :1097,
    "turquoise"     :1195,
    "wet_asphalt"   :1196,
    "wisteria"      :1197
}


usercolor={
    "vbf_m125"           : 99,
    "ggf_m125"           : 215,
    "qcd"                : 91,
    "gamgam"             : 65,
    "gamJet"             : 51,
    "dy_toll_m50"        : 85,
}

def hex_to_RGB(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))

def hex_to_rgb(value):
    (R,G,B) = hex_to_RGB(value)
    r  =  R/float(255)
    g  =  G/float(255)
    b  =  B/float(255)
    return (r, g, b) 


def print_colors():
    for key in hexcolor:
        print key ,'\t', hex_to_RGB(hexcolor[key]) #'\t',hex_to_rgb


claudia = {}
def convert_color(p=False):
    for c in hexcolor:
        (r,g,b) = hex_to_RGB(hexcolor[c])
        claudia[c] = ROOT.TColor.GetColor(r,g,b)
        if p==True:
            print c,'\t', claudia[c]
