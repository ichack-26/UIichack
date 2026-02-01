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
#    TFL.SDG.C.If_Stmt
#
# Purpose
#    Model if statements in the code in a C file
#
# Revision Dates
#    30-Jul-2004 (CT) Creation
#     2-Aug-2004 (CT) Creation continued
#     2-Aug-2004 (CT) `children_group_names` redefined
#     3-Aug-2004 (CT) Don't redefine value of `Else`
#     3-Aug-2004 (CT) children_group_names `Then` and `Elseif` added
#     3-Aug-2004 (CT) `If.insert` simplified
#     9-Aug-2004 (CT) `Conditional` factored
#    10-Aug-2004 (MG) Missing import of `TFL.SDG.C.Statement` added
#    24-Aug-2004 (CT) `_convert_then` factored and implemented to force
#                     `self.then_class`
#    08-Dec-2005 (MG) `Then` exported
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C.Block
import _TFL._SDG._C.Conditional
import _TFL._SDG._C.Statement

class Else (TFL.SDG.C.Block) :
    """Else clause of If statement"""

    Ancestor             = TFL.SDG.C.Block
    cgi                  = TFL.SDG.C.Node.Else
    init_arg_defaults    = dict \
        ( name           = "else"
        )

    c_format             = "\n".join \
        ( ( """else"""
          , Ancestor._c_format
          )
        )

    trailer              = ""

# end class Else

class Elseif (TFL.SDG.C.Conditional, TFL.SDG.C.Block) :
    """Else-If clause of If statement"""

    Ancestor             = TFL.SDG.C.Block
    cgi                  = TFL.SDG.C.Node.Elseif

    c_format             = "\n".join \
        ( ( """else if (%(::*condition:)s)"""
          , Ancestor._c_format
          )
        )

    trailer              = ""

# end class Elseif

Then = TFL.SDG.C.Block

class If (TFL.SDG.C.Conditional, TFL.SDG.C._Statement_) :
    """If statement"""

    then_class           = Then
    else_class           = Else
    elif_class           = Elseif

    init_arg_defaults    = dict \
        ( then           = ""
        )

    front_args           = ("condition", "then")

    _autoconvert         = dict \
        ( then           = lambda s, k, v : s._convert_then (v)
        )

    c_format             = "\n".join \
        ( ( """if (%(::*condition:)s)"""
          , """%(::*then_children:)s"""
          , """%(::*elseif_children:)s"""
          , """%(::*else_children:)s"""
          )
        )

    children_group_names = \
        ( TFL.SDG.C.Node.Then
        , TFL.SDG.C.Node.Elseif
        , TFL.SDG.C.Node.Else
        )

    def __init__ (self, * args, ** kw) :
        self.__super.__init__     (* args, ** kw)
        self.then_children.append (self.then)
        self.then._update_scope   (self.scope)
    # end def __init__

    def formatted (self, format_name, * args, ** kw) :
        last = self.else_children or self.elseif_children or self.then_children
        last [-1].trailer = ";"
        return self.__super.formatted (format_name, * args, ** kw)
    # end def formatted

    def insert (self, child, index = None, delta = 0) :
        if not child :
            return
        child = self._convert (child, self.else_class)
        if isinstance (child, self.else_class) :
            if self.else_children :
                raise TFL.SDG.Invalid_Node (self, child)
        elif not isinstance (child, self.elif_class) :
            raise TFL.SDG.Invalid_Node (self, child)
        child.trailer = ""
        self.__super.insert (child, index, delta)
    # end def insert

    def _convert_then (self, v) :
        if not isinstance (v, self.then_class) :
            v = self.then_class (v)
        v.trailer = ""
        return v
    # end def _convert_then

# end class If

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*", "Then")
### __END__ TFL.SDG.C.If_Stmt
