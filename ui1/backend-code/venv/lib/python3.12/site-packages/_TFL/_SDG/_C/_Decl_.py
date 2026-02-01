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
#    TFL.SDG.C._Decl_
#
# Purpose
#    Model C declarations
#
# Revision Dates
#    28-Jul-2004 (CT) Creation
#    30-Jul-2004 (CT) `Decl_Group` added
#    30-Jul-2004 (CT) `Maybe_Const` added
#     9-Aug-2004 (CT) `Maybe_Static` changed to call `_update_scope`
#    12-Aug-2004 (MG) `Incl` group removed (nice try)
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C.Node
import _TFL._SDG._C._Scope_

class _Decl_ (TFL.SDG.C.Node) :
    """Root class for C declaration nodes"""

    cgi                  = TFL.SDG.C.Node.Decl

# end class _Decl_

class Maybe_Const (_Decl_) :
    """Mixin for node types that may be declared const"""

    init_arg_defaults    = dict (const = None)
    _autoconvert         = dict \
        ( const          = lambda s, k, v : v and "const "    or None
        )

# end class Maybe_Const

class Maybe_Extern (_Decl_) :
    """Mixin for node types that may be declared extern"""

    init_arg_defaults    = dict (extern = None)
    _autoconvert         = dict \
        ( extern         = lambda s, k, v : v and "extern "   or None
        )

# end class Maybe_Extern

class Maybe_Static (_Decl_) :
    """Mixin for node types that may be declared static"""

    init_arg_defaults    = dict (static = None)
    _autoconvert         = dict \
        ( static         = lambda s, k, v : v and "static "   or None
        )

    def __init__ (self, * args, ** kw) :
        self.__super.__init__ (* args, ** kw)
        if self.static :
            self._update_scope (TFL.SDG.C.C)
    # end def __init__

# end class Maybe_Static

class Maybe_Volatile (_Decl_) :
    """Mixin for node types that may be declared volatile"""

    init_arg_defaults    = dict (volatile = None)
    _autoconvert         = dict \
        ( volatile       = lambda s, k, v : v and "volatile "   or None
        )

# end class Maybe_Volatile

class Decl_Group (_Decl_, TFL.SDG.C._Scope_) :
    """Group of C declarations not enclosed in a block."""

    scope                = TFL.SDG.C.C
    star_level           = 2
    h_format = c_format  = """
        %(::*description:)s
        %(::*explanation:)s
        %(::*decl_children:)s
        %(::*head_children:)s
        %(::*body_children:)s
        %(::*tail_children:)s
    """

# end class Decl_Group

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*", "_Decl_")
### __END__ TFL.SDG.C._Decl_
