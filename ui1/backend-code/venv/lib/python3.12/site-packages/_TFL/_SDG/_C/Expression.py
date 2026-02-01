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
#    TFL.SDG.C.Expression
#
# Purpose
#    Model C expressions
#
# Revision Dates
#    28-Jul-2004 (CT) Creation
#    25-Aug-2004 (CT) Add `H` to scope (otherwise `ifdef.condition` doesn't
#                     work in header files)
#    20-Oct-2004 (CT) `H` removed from scope (not all expressions should
#                     appear in headerfile by default)
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C.Node

class Expression (TFL.SDG.C.Node) :
    """Model C expressions"""

    scope               = TFL.SDG.C.C

    init_arg_defaults   = dict \
        ( code          = ""
        )

    front_args          = ("code", )

    h_format = c_format = "%(code)s"

# end class Expression

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.Expression
