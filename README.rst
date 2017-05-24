
Heppi (Hep Plotting Interface)
==============================

.. image:: https://img.shields.io/pypi/v/heppi.svg
        :target: https://pypi.python.org/pypi/heppi

.. image:: https://travis-ci.org/yhaddad/Heppi.svg?branch=master
    :target: https://travis-ci.org/yhaddad/Heppi

.. image:: https://readthedocs.org/projects/heppi/badge/?version=latest
        :target: https://readthedocs.org/projects/heppi/?badge=latest
        :alt: Documentation Status

.. image:: https://zenodo.org/badge/45534212.svg
   :target: https://zenodo.org/badge/latestdoi/45534212


A High Energy Physics Plotting Interface

* Free software: ISC license
* Documentation: https://heppi.readthedocs.org.

Discription
-----------
``Heppi`` is a plotting interface written in python. It uses json files as configuration files
called plotcards with higly flexible syntax allowing a better handeling of the variable and the
samples.


installation
------------
* The recomended procedure to install ``Heppi`` is trough ``PyPI``
  .. code-block::
     pip install heppi

* For CERN users, you might need to install the package on your .local directory by adding ``--user`` option to the previous command.
  .. code-block::
     pip install heppi --user

* The dependencies will normaly be installed automatically.
* Since ``Heppi`` is based on pyROOT, ROOT env must be set

installation via Git
--------------------

* The alternative way to install Heppi is by cloning and building the project
  .. code-block::
     > git clone git@github.com:yhaddad/Heppi.git
     > cd Heppi
     > pip install dependencies --user
     > make install-user

Quick start
-----------

Find ROOT trees
~~~~~~~~~~~~~~~
Let start by downloading example of root tree stored in `figshare <https://figshare.com/>`_ ::

$ wget https://ndownloader.figshare.com/files/1920208
$ wget https://ndownloader.figshare.com/files/1920200



Produce a plotcard
~~~~~~~~~~~~~~~~~~~
* ``Heppi`` allows to create your own plotcard using the makeplotcard script. You can run::

  $ makeplotcard


Produce a stacked plots
~~~~~~~~~~~~~~~~~~~~~~~

1. To run ``heepi`` plotmaker you have to run the script ``plot``
2. you can print the options of the script by typing ``.\plot --help``
3. you have to combine the trees using ``rootmerge.py`` script
4. the commend I'm using is the follwing::

    $ ./plot -s /dir/to/merged/trees --load plotcard.json --all


5. if you want to print one variable in the plotcard you can replace the option ``--all`` by ``--variable`` or just ``-v`` followed by the name of the variable. example::

    $ ./plot -s /dir/to/merged/trees --load plotcard.json -v var1

Write a valid plotcard ?
~~~~~~~~~~~~~~~~~~~~~~~~

* Produce the plotcard using a processe.json files and input root file.
* The tree name must be specified::

   $ ./makeplotcard.py --load  /path/to/root/file.root \
                       --out   plotcard.json \
                       --tree  VBFMVADumper/*VBFDiJet

* the ``*`` will be replaced automatically by the remaining name of the tree found in the ``VBFMVADumper`` directory.
* This is for the use of .. _``flashgg``: https://github.com/cms-analysis/flashgg type dumper trees only, a more standard version will be pushed soon

Credits
-------
This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
