# This is for intercepting the output of ROOT
# In a cell, put %%rootprint so that the output that would normally be
# sent directly to the stdout will instead be displayed in the cell.
# It must be the first element in the cell.
import tempfile
import ROOT
from IPython.core.magic import (Magics, magics_class, line_cell_magic)

@magics_class
class RootMagics(Magics):
    """Magics related to Root.

    %%rp  - Capture Root stdout output and show in result cell
    """

    def __init__(self, shell):
        super(RootMagics, self).__init__(shell)

    @line_cell_magic
    def rp(self, line, cell=None):
        """Capture Root stdout output and print in ipython notebook."""

        with tempfile.NamedTemporaryFile() as tmpFile:
            ROOT.gSystem.RedirectOutput(tmpFile.name, "w")
            # ns = {}
            # exec cell in self.shell.user_ns, ns
            if cell:
                exec cell in self.shell.user_ns
                ROOT.gROOT.ProcessLine("gSystem->RedirectOutput(0);")
                print tmpFile.read()
            else:
                exec line in self.shell.user_ns
                ROOT.gROOT.ProcessLine("gSystem->RedirectOutput(0);")
                print tmpFile.read()

# Register
ip = get_ipython() 
ip.register_magics(RootMagics)
