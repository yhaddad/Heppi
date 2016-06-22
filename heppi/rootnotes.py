"""
Adapted from alexander.mazurov@cern.ch and andrey.ustyuzhanin@cern.ch
More examples: http://mazurov.github.io/webfest2013/
"""

import ROOT
ROOT.gROOT.ProcessLine(".x .root/rootlogon.C")

import tempfile
from   IPython.core import display


def canvas(name="icanvas", size=(800, 600)):
    """Helper method for creating canvas"""
    assert len(size) == 2
    return ROOT.TCanvas(name, name, size[0], size[1])


def _display_canvas(canvas):
    file = tempfile.NamedTemporaryFile(suffix=".png")
    canvas.SaveAs(file.name)
    ip_img = display.Image(filename=file.name, format='png', embed=True)
    return ip_img._repr_png_()


def _display_any(obj):
    file = tempfile.NamedTemporaryFile(suffix=".png")
    obj.Draw()
    ROOT.gPad.SaveAs(file.name)
    ip_img = display.Image(filename=file.name, format='png', embed=True)
    return ip_img._repr_png_()

# register display function with PNG formatter:
png_formatter = get_ipython().display_formatter.formatters['image/png'] # noqa
png_formatter.for_type(ROOT.TCanvas, _display_canvas)
png_formatter.for_type(ROOT.TF1, _display_any)
