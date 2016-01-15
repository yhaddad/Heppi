===============================
Heppi
===============================

.. image:: https://img.shields.io/pypi/v/heppi.svg
        :target: https://pypi.python.org/pypi/heppi

.. image:: https://img.shields.io/travis/yhaddad/heppi.svg
        :target: https://travis-ci.org/yhaddad/heppi

.. image:: https://readthedocs.org/projects/heppi/badge/?version=latest
        :target: https://readthedocs.org/projects/heppi/?badge=latest
        :alt: Documentation Status


High Energy Physics Plotting Interface

* Free software: ISC license
* Documentation: https://heppi.readthedocs.org.

Features
--------
## how to run ? 
### produce a stacked plots
* To run `heepi` plotmaker you have to run the script `plot`
* you can print the options of the script by typing `.\plot --help`   
* you have to combine the trees using `rootmerge.py` script
* the commend I'm using is the follwing:
`./plot -s /dir/to/merged/trees --load plotcard.json --all`
* if you want to print one variable in the plotcard you can replace the option `--all` by `--variable` or just `-v` followed by the name of the variable.
example : `./plot -s /dir/to/merged/trees --load plotcard.json -v var1`

### how to write a valid plotcard ?
* Produce the plotcard using a processe.json files and input root file. 
* The tree name must be specified

```bash
./makeplotcard.py --load data/100000/output_VBFHToGG_M-125_13TeV_powheg_pythia8_numEvent100000_histos.root\
	          --out plotcard.json\
	          --tree  VBFMVADumper/*VBFDiJet

```
* the `*` will be replaced automatically by the remaining name of the tree found in the `VBFMVADumper` directory.
* This is for the use of [flashgg](https://github.com/cms-analysis/flashgg) type dumper trees only, a more standard version will be pushed soon

### installation
* installation : `pip install --user jsmin termcolor progressbar` : this must work in lxplus:  since in imperial does not existe, you I have to find a permanent solution to include those packages for the future. For the moment do not use comments in the json files !
* ROOT env must be set

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
