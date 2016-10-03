Usage of clplot
===============

First see how to do :doc:`install`. Start CASA as normal, just make sure that you start the version that clplot was installed in. You should be able to do ``${CASADIR:? must be set}/bin/casa``


Calculate and write out closure phase
-------------------------------------

The function to use is :py:func:`clio.closurePhTriad`

Enter into CASA::

  import clplot.clio as clio
  clio.closurePhTriad("/home/bnikolic/sciencedata/HERA-closure/centA.ms",  [22, 9, 20], "test.csv", integ=0)

This will create a file *test.csv* containing the closure phase for
the first integration in this file for triad [22,9,20]. 





