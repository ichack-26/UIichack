# -*- coding: utf-8 -*-
# Copyright (C) 2004-2014 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG._trace
#
# Purpose
#    Enable tracing of SDG formatting
#
# Revision Dates
#    22-Sep-2004 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL                     import TFL
from   _TFL.predicate           import *
from   _TFL.pyk                 import pyk

import _TFL._SDG.Node
import _TFL._SDG.Formatter
import _TFL._FMW.Tracer
import _TFL.Caller

def _ (self) :
    d = {}
    for a in "indent_anchor", "indent_offset", "ht_width" :
        try :
            d [a] = self [a]
        except KeyError :
            pass
    return ", ".join \
        ([("%s = %s" % (n, v)) for (n, v) in sorted (pyk.iteritems (d))])
TFL.Caller.Object_Scope.__str__ = TFL.Caller.Object_Scope.__repr__ = _

def _ (self) :
    return "%s %s" % (self.__class__.__name__, self.name)
TFL.SDG.Node.__repr__ = _

def _ (self) :
    return "%s %s" % (self.__class__.__name__, self.name)
TFL.SDG.Node.__str__ = _

tracer = TFL.FMW.Tracer \
    (recorder = TFL.FMW.Trace_Recorder_F (open ("/tmp/trace", "w")))

Formatter = TFL.SDG._.Formatter

tracer.add_method (TFL.SDG.Node,                               "formatted")
tracer.add_method (Formatter.Partial_Line_Formatter,           "__call__")
tracer.add_method (Formatter.Single_Line_Formatter,            "__call__")
tracer.add_method (Formatter._Recursive_Formatter_,            "__call__")
tracer.add_method (Formatter._Recursive_Formatter_Method_,     "__iter__")
tracer.add_method (Formatter._Recursive_Formatter_Node_,       "__iter__")
tracer.add_method (Formatter._Recursive_Formatter_Attr_,       "__iter__")
tracer.add_method (Formatter._Recursive_Formatters_,           "__call__")
tracer.add_method (Formatter._Recursive_Formatters_,           "__iter__")
tracer.add_method (Formatter.Multi_Line_Formatter,             "__call__")

### __END__ TFL.SDG.Node
