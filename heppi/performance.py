import heppi
import ROOT

def load_cpp_libraries():
    ROOT.ProcessLine(".L ../macro/kernelH1.cc+")
    
def main():
    load_cpp_libraries()
    
    
