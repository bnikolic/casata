Installation
============

CLPLOT installs itself into your CASA distribution. I have only tested
it with CASA tar balls. You need to specify where CASA has been
unpacked, e.g.::

  export CASADIR=/data/p/casa-release-4.6.0-el6

At first installation into new CASA we need to setup PIP::

  wget https://bootstrap.pypa.io/get-pip.py
  ${CASADIR:? must be set}/bin/python get-pip.py
  ${CASADIR}/bin/pip2.7 install --upgrade setuptools  

Then install clplot::

  ${CASADIR:? must be set}/bin/pip install --extra-index-url=https://www.mrao.cam.ac.uk/~bn204/soft/py clplot


Note that https://www.mrao.cam.ac.uk/~bn204/soft/py is the remote
software repository from which clplot will be downloaded
  
To uninstall clplot::

  ${CASADIR:? must be set}/bin/pip uninstall clplot
