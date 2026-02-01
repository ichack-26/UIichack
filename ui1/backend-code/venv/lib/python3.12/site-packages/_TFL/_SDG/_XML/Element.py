# -*- coding: utf-8 -*-
# Copyright (C) 2004-2024 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.XML.Element
#
# Purpose
#    Model an element of a XML document
#
# Revision Dates
#    26-Aug-2004 (CT) Creation
#    20-Sep-2004 (CT) `x_attrs` added
#    21-Oct-2004 (CT) Use `"` instead of `'` in output
#     5-Sep-2005 (CT) `XML.Node` factored
#     6-Sep-2005 (CT) `xml_format` changed (`elem_type.rear0` empty instead
#                     of space)
#    19-Mar-2024 (CT) Add `Element_Compact`
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._XML.Node

class Element (TFL.SDG.XML.Node) :
    """Model an element of a XML document"""

    front_args           = ("elem_type", )
    init_arg_defaults    = dict \
        ( elem_type      = None
        , x_attrs        = {}
        )

    _xml_format          = """
        %(::*description:)s
        <%(elem_type)s%(:head= ¡rear0=¡rear=%(NL)s:>@_attr_values:)s>
        >%(::*body_children:)s
        </%(elem_type)s>
    """.strip ()

    xml_format           = _xml_format

    _autoconvert         = dict \
        ( elem_type      = lambda s, k, v : s._checked_xml_name (v)
        ,
        )

# end class Element

class Element_Compact (Element) :
    """Model an element of a XML document with compact representation."""

    xml_format          = \
        ( """%(::*description:)s"""
          """<%(elem_type)s%(:head= ¡rear0=¡rear=%(NL)s:>@_attr_values:)s>"""
            """%(::*body_children:)s"""
          """</%(elem_type)s>"""
        )

# end class Element_Compact

class Leaf (TFL.SDG.Leaf, Element) :
    """Model a leaf element of a XML document"""

# end class Leaf

class Empty (Leaf) :
    """Model an empty element of a XML document"""

    xml_format           = \
        ( """<%(elem_type)s"""
            """%(:head= ¡rear0=¡rear=%(NL)s:>@_attr_values:)s"""
          """/>"""
        )

# end class Empty

if __name__ != "__main__" :
    TFL.SDG.XML._Export ("*")
### __END__ TFL.SDG.XML.Element
