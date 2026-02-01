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
#    TFL.SDG.C.Switch
#
# Purpose
#    Model switch statements in the code of a C file
#
# Revision Dates
#     9-Aug-2004 (CT) Creation
#    20-Oct-2004 (CT) Import for `Statement` added
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C.Block
import _TFL._SDG._C.Conditional
import _TFL._SDG._C.Expression
import _TFL._SDG._C.Statement

class Case (TFL.SDG.C.Stmt_Group) :
    """Case clause of a switch statement"""

    cgi                  = TFL.SDG.C.Node.Case

    init_arg_defaults    = dict \
        ( selector       = ""
        )

    front_args           = ("selector", )

    _autoconvert         = dict \
        ( selector       = lambda s, k, v
              : s._convert (v, TFL.SDG.C.Expression)
        )

    c_format             = """
        case %(::*selector:)s :
        >>%(::*body_children:)s
        >>break;
    """

# end class Case

class Default_Case (TFL.SDG.C.Stmt_Group) :
    """Default clause of a switch statement"""

    cgi                  = TFL.SDG.C.Node.Default
    c_format             = """
        default :
        >>%(::*body_children:)s
    """

# end class Default_Case

class Switch (TFL.SDG.C.Conditional, TFL.SDG.C._Statement_) :
    """Switch statement"""

    c_format             = """
        switch (%(::*condition:)s)
        >{
        >>%(::*case_children:)s
        >>%(::*default_children:)s
        >};
    """

    children_group_names = \
        ( TFL.SDG.C.Node.Case
        , TFL.SDG.C.Node.Default
        )

    def insert (self, child, index = None, delta = 0) :
        if not child :
            return
        child = self._convert (child, Case)
        if isinstance (child, Default_Case) :
            if self.default_children :
                raise TFL.SDG.Invalid_Node (self, child)
        elif not isinstance (child, Case) :
            raise TFL.SDG.Invalid_Node (self, child)
        self.__super.insert (child, index, delta)
    # end def insert

# end class Switch

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.Switch
