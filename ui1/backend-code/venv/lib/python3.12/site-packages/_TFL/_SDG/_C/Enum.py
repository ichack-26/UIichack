# -*- coding: utf-8 -*-
# Copyright (C) 2005-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.C.Enum
#
# Purpose
#    C enum declaration
#
# Revision Dates
#    24-May-2005 (CED) Creation
#    30-Aug-2005 (CT)  Use `split_hst` instead of home-grown code
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
from   _TFL.predicate    import split_hst
import _TFL._SDG._C.Node

class Enum_Item (TFL.SDG.C.Node, TFL.SDG.Leaf) :
    """Model an item of a C enum."""

    init_arg_defaults    = dict \
        ( name           = ""
        , value          = ""
        , comment        = ""
        )

    front_args           = ("name", "value", "comment")

    _autoconvert         = dict \
        ( value          = lambda s, k, v : s._convert_value   (v)
        , comment        = lambda s, k, v : s._convert_comment (v)
        )

    c_format = h_format  = """ \
          %(name)s%(value)s%(:front= :>*comment:)s
       """

    def _convert_comment (self, comment) :
        result = ""
        if comment :
            result = TFL.SDG.C.Comment (comment)
        return result
    # end def _convert_comment

    def _convert_value (self, value) :
        result = ""
        if value :
            result = " = %s" % value
        return result
    # end def _convert_value

# end class Enum_Item

class Enum (TFL.SDG.C.Node, TFL.SDG.Leaf) :
    """Model C enum declarations"""

    init_arg_defaults    = dict \
        ( name           = ""
        , values         = []
        , standalone     = ""
        )

    _autoconvert         = dict \
        ( values         = lambda s, k, v : s._convert_values (v)
        , standalone     = lambda s, k, v : v and ";" or ""
        )

    front_args           = ("name", "values")

    c_format = h_format  = \
        ( """enum _%(name)s """
          """%(:front=%(NL)s%(base_indent)s{ """
          """¡front0={"""
          """¡sep=%(base_indent)s, """
          """¡rear=%(NL)s%(base_indent)s}"""
          """¡rear0=}"""
          """:*values:)s%(standalone)s"""
        )

    def _convert_values (self, values) :
        result = []
        if not values :
            raise ValueError \
               ("Enum declaration need at least one possible value")
        for v in values :
            item, _, comment = [s.strip () for s in split_hst (v, "//")]
            name, _, value   = [s.strip () for s in split_hst (item, "=")]
            result.append (Enum_Item (name, value, comment))
        return result
    # end def _convert_values

# end class Enum

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.Enum
