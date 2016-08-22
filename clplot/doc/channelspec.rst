Channel Specification
=====================

Many of the functions take a *chan* parameter. This is a channel
selection specification in the format accepted by the ms.selectchannel
task, passed as a dictionary. Specifically the following elements are
possible:

* *nchan* Number of channels to use in closure computations

* *start* The first input channel

* *width* The number of input channels to average together to form
  each channel which is used in the closure computation

* *inc* Number of input channels between each group of channels

Example::

   clquants.closurePh(d_fg,
                      alist=(1,2,3),
                      chan={"nchan": 1, "start": 0,
                      "width": 10, "inc": 1})

This averages the first 10 channels into a single channel and computes
the closure quantities on this averaged channel only.
