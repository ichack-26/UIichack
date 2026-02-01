# -*- coding: utf-8 -*-
# Copyright (C) 2003-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.bayesian
#
# Purpose
#    Calculate conditional probabilities using Rev. Thomas Bayes' formula
#
# Revision Dates
#     3-Aug-2003 (CT) Creation
#    29-Sep-2006 (CT) Two more doctests added
#    16-Jun-2013 (CT) Use `TFL.CAO`, not `TFL.Command_Line`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL import TFL

import _TFL.CAO

def bayesian (p_h, p_o_h, p_o_not_h) :
    """Calculate the probability of hypothesis `h` given the new observation
       `o`, where ::

       - `p_h` is the probability before the new observation was made,

       - `p_o_h` is the probability of the observation when the
         hypothesis `h` is true,

       - `p_o_not_h` is the probability of the observation when the
         hypothesis `h` is false.

       Consider a disease that appears in 1% of the population and a test for
       that disease is positive 80% (or 85%, or 90%) of the time when the
       disease is present and 10% (or 5%, or 1%) of the time when the disease
       is not present:

       >>> print ("%5.3f" % bayesian (0.01, 0.80, 0.10))
       0.075
       >>> print ("%5.3f" % bayesian (0.01, 0.85, 0.05))
       0.147
       >>> print ("%5.3f" % bayesian (0.01, 0.90, 0.01))
       0.476
       >>> print ("%5.3f" % bayesian (0.01, 0.99, 0.01))
       0.500

       Because so many people don't have the disease, the false positives far
       exceed the small percentage of those tested who actually have the
       disease.

       >>> print ("%5.3f" % bayesian (0.50, 0.80, 0.10))
       0.889
       >>> print ("%5.3f" % bayesian (0.50, 0.85, 0.05))
       0.944
       >>> print ("%5.3f" % bayesian (0.50, 0.90, 0.01))
       0.989
       >>> print ("%5.3f" % bayesian (0.50, 0.99, 0.01))
       0.990
    """
    p_not_h         = 1.0 - p_h
    p_h_times_p_o_h = p_h * p_o_h
    return p_h_times_p_o_h / (p_h_times_p_o_h + (p_not_h * p_o_not_h))
# end def bayesian

def _main (cmd) :
    print ("%5.3f" % bayesian (cmd.p_h, cmd.p_o_h, cmd.p_o_not_h))
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler       = _main
    , args          =
        ( "p_h:F"
            "?probability of hypothesis  before the new observation was made"
        , "p_o_h:F"
            "?probability of the observation when the hypothesis `h` is true"
        , "p_o_not_h:F"
            "?probability of the observation when the hypothesis `h` is false"
        )
    , min_args      = 3
    , max_args      = 3
    )

if __name__ != "__main__" :
    TFL._Export ("*")
else :
    _Command ()
### __END__ TFL.bayesian
