# -*- coding: utf-8 -*-
# Copyright (C) 2000-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Gauge_Logger
#
# Purpose
#    Provide access to progress gauge without introducing dependencies to
#    window system (e.g., instances of Gauge_Logger can be used in
#    interactive and batch applications)
#
# Revision Dates
#    27-Jan-2000 (MG)  Creation
#     7-Feb-2000 (CT)  `__nonzero__' added
#    29-Jun-2000 (CT)  Use `predicate.relax' instead of home-grown `_gobble'
#    14-Jul-2000 (MG)  Methods `__str__' and `__repr__' added
#    18-Jul-2000 (GS)  Corrected a typo in __repr__ (selg -> self)
#    27-Jul-2000 (CT)  `verbose' added
#    11-Jun-2003 (CT)  s/!= None/is not None/
#    31-Mar-2004 (GWA) 'Gauge_Interval', 'Gauge_Handler' added
#     6-May-2004 (GWA) 'Gauge_Handler' improved
#    10-May-2004 (GWA) '__getattr__' fixed in 'Gauge_Handler'
#    14-Mar-2005 (CT)  `_activate` added
#    14-Mar-2005 (CT)  Dead code courtesy of GWA removed
#    21-Jan-2006 (MG)  Moved into `TFL` package
#    23-Nov-2006 (PGO) Inheritance changed
#     8-Oct-2015 (CT)  Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   _TFL                import TFL
from   _TFL.pyk            import pyk

import _TFL._Meta.Object
import _TFL.predicate

class Gauge_Logger (TFL.Meta.Object) :
    """Provide access to progress gauge without introducing dependencies to
       window system (e.g., instances of Gauge_Logger can be used in
       interactive and batch applications)
    """
    def __init__ (self, gauge = None, log = 0) :
        self.gauge = gauge
        self.log   = log
    # end def __init__

    def echo (self, * msg, ** kw) :
        verbose = kw.get ("verbose", 1)
        if self.log >= verbose :
            for m in msg :
                print (m, end = " ")
    # end def echo

    def _activate (self, title = "", label = " ", * args, ** kw) :
        print (label or title)
    # end def _activate

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if self.gauge :
            return getattr (self.gauge, name)
        elif name == "activate" :
            return self._activate
        return TFL.relax
    # end def __getattr__

    def __bool__ (self) :
        return self.gauge is not None
    # end def __bool__

    def __str__ (self) :
        return "Log: %d, Gauge: %s" % (self.log, self.gauge)
    # end def __str__

    def __repr__ (self) :
        return "%s (log = %s, gauge = %s)" % \
            (self.__class__.__name__, self.log, self.gauge)
    # end def __repr__

# end class Gauge_Logger

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Gauge_Logger
