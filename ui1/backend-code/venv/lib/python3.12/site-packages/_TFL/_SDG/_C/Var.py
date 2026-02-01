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
#    TFL.SDG.C.Var
#
# Purpose
#    Model C variables
#
# Revision Dates
#    28-Jul-2004 (CT) Creation
#    30-Jul-2004 (CT) `Maybe_Const` factored
#    30-Jul-2004 (CT) `Multiple_Var` added
#     9-Aug-2004 (CT) `Initializer` handling added
#     9-Aug-2004 (CT) `_Var_` factored
#    12-Aug-2004 (MG) Formats changed
#    23-Sep-2004 (CT) `c_format` changed (`front0` added and `front` changed
#                     to include `%(NL)s`)
#    23-Sep-2004 (MG) `vaps_channel_format` added
#    23-Feb-2005 (CED) `apidoc_tex_format` defined
#    13-Jul-2005 (MG)  Parameter `type_name_length` added and used in
#                      `h_format`
#     6-Dec-2007 (CT) Imports fixed
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C._Decl_
import _TFL._SDG._C.Expression
import _TFL._SDG._C.Initializer
import _TFL._SDG._C.Struct
import _TFL._SDG._C.Type

class _Var_ ( TFL.SDG.C.Maybe_Const
            , TFL.SDG.C.Maybe_Extern
            , TFL.SDG.C.Maybe_Static
            , TFL.SDG.C.Maybe_Volatile
            , TFL.SDG.Leaf
            ) :

    init_arg_defaults      = dict \
        ( type             = ""
        , init             = None
        , new_line_col     = 0
        , type_name_length = 0
        )

    initializers         = None

    _autoconvert         = dict \
        ( type           = lambda s, k, v : s._convert_type (v)
        )
    _struct              = None

    front_args           = ("type", "name")

    _common_head         = \
        ("""%(::.extern:)s"""
         """%(::.static:)s"""
         """%(::.volatile:)s"""
         """%(::.const:)s"""
         """%(::.struct:)s"""
         """%(::*type:)-{type_name_length}s %(name)s"""
        )

    _common_tail        = \
        """%(trailer)s%(:head= :>*eol_desc:)s
           >>%(::*description:)s
        """

    def _convert_type (self, v) :
        result = self._convert (v, TFL.SDG.C.Type)
        if result.name in TFL.SDG.C.Struct.extension :
            self._struct = TFL.SDG.C.Struct.extension [result.name]
        return result
    # end def _convert_type

# end class _Var_

class Var (_Var_) :
    """Model C variables"""

    Ancestor             = _Var_

    init_arg_defaults    = dict \
        ( struct         = None
        , init_dict      = {}
        , trailer        = ";"
        )

    _autoconvert         = dict \
        ( init           = lambda s, k, v
              : v not in ("", None) and TFL.SDG.C.Init_Atom (v) or None
        , struct         = lambda s, k, v : v and "struct " or None
        )

    h_format             = "".join \
        ( ( Ancestor._common_head
          , Ancestor._common_tail
          )
        )

    c_format             = "".join \
        ( ( Ancestor._common_head
          , """%(:front= =%(NL)s%(base_indent)s¡front0= = :*initializers:)s"""
          , Ancestor._common_tail
          )
        )

    apidoc_tex_format   = """%(::*type:)s %(name)s"""

    vaps_channel_format = """
      %(name)s     1     %(::*type:)s
    """

    def __init__ (self, type, name, init = "", ** kw) :
        ### redefine to allow optional positional argument `init`
        self.__super.__init__ (type, name, init = init, ** kw)
    # end def __init__

    def formatted (self, * args, ** kw) :
        ### XXX add comment
        if self.init_dict :
            if not self._struct :
                raise TFL.SDG.Invalid_Node (self, self.type, self.init_dict)
            self.initializers = self._struct._setup_initializers \
                (self.init_dict)
        if self.init :
            if self.init_dict :
                raise TFL.SDG.Invalid_Node (self, self.init, self.init_dict)
            self.initializers = self.init
        return self.__super.formatted (* args, ** kw)
    # end def formatted

# end class Var

class Multiple_Var (Var) :
    """Declaration for multiple variables"""

    Ancestor             = Var

    init_arg_defaults    = dict \
        ( var_names      = ""
        )

    h_format             = "".join \
        ( ( Ancestor._common_head
          , """%(:front=, :._var_names:)s"""
          , Ancestor._common_tail
          )
        )

    c_format             = "".join \
        ( ( Ancestor._common_head
          , """%(:front=, :._var_names:)s"""
          , """%(:head= = :*init:)s"""
          , Ancestor._common_tail
          )
        )

    _var_names           = property (lambda s : ", ".join (s.var_names))

    def __init__ (self, type, name, * var_names, ** kw) :
        ### need to jump through hoops to accomodate optional arg `init` of
        ### ancestor vs. `* var_names`
        self.__super.__init__ (type, name, var_names = var_names, ** kw)
    # end def __init__

# end class Multiple_Var

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*", "_Var_")
### __END__ TFL.SDG.C.Var
