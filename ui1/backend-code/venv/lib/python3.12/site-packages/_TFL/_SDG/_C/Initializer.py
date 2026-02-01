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
#    TFL.SDG.C.Initializer
#
# Purpose
#    Model initializers for C data types
#
# Revision Dates
#     9-Aug-2004 (CT) Creation
#    21-Sep-2004 (CT) `Init_Atom.c_format` changed (s/front/head/)
#    23-Sep-2004 (CT) `Init_Comp.c_format` changed (total revamp)
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C.Node

class Init_Atom (TFL.SDG.C.Node) :
    """Initializer for atomic variables/fields"""

    init_arg_defaults    = dict \
        ( init           = ""
        )
    front_args           = ("init", )

    c_format             = """%(init)s%(:head= :*description:)s"""

# end class Init_Atom

class Init_Comp (TFL.SDG.C.Node) :
    """Initializer for composite variables/fields"""

    c_format             = """
        { %(:rear=%(NL)s}¡sep=, :>*body_children:)s%(:head= :*description:)s
    """

# end class Init_Comp

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.Initializer
