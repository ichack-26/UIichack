# -*- coding: utf-8 -*-
# Copyright (C) 2004-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.C.New_Line
#
# Purpose
#    Model empty lines in the code in a C file
#
# Revision Dates
#    26-Jul-2004 (CT) Creation
#    12-Aug-2004 (MG) formats changed
#    12-Aug-2004 (MG) `cgi` added
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C.Node

class New_Line (TFL.SDG.Leaf, TFL.SDG.C.Node) :
    """Model an empty line in the code in a C file"""

    cgi                  = None
    init_arg_defaults    = dict \
        ( lines          = 1
        )
    h_format = c_format  = """%('''\\n''' * (lines - 1))s"""

# end class New_Line

class New_Page (TFL.SDG.Leaf, TFL.SDG.C.Node) :
    """Adds a new page character (formfeed)."""

    cgi                  = None
    h_format = c_format  = """%('\f')s"""

# end class New_Page

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.New_Line
