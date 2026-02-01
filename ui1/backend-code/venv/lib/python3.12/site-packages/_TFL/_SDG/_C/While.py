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
#    TFL.SDG.C.While
#
# Purpose
#    Model while statements in the code of a C file
#
# Revision Dates
#     9-Aug-2004 (CT) Creation
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C.Block
import _TFL._SDG._C.Conditional

class While (TFL.SDG.C.Conditional, TFL.SDG.C.Block) :
    """While statement"""

    Ancestor             = TFL.SDG.C.Block

    c_format             = "\n".join \
        ( ( """while (%(::*condition:)s)"""
          , Ancestor._c_format
          )
        )

# end class While

class Do_While (TFL.SDG.C.Conditional, TFL.SDG.C.Block) :
    """A `do` ... `while ()` loop"""

    Ancestor             = TFL.SDG.C.Block

    c_format             = "\n".join \
        ( ( """do"""
          , Ancestor._c_format.strip ()
          , """while (%(::*condition:)s);"""
          )
        )

    trailer              = ""

# end class Do_While

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.While
