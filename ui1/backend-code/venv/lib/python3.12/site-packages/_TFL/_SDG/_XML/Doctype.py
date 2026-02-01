# -*- coding: utf-8 -*-
# Copyright (C) 2004-2023 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.XML.Doctype
#
# Purpose
#    Model the doctype declaration of a XML document
#
# Revision Dates
#    26-Aug-2004 (CT) Creation
#    21-Oct-2004 (CT) Use `"` instead of `'` in output
#     5-Sep-2005 (CT) `External_Id` factored
#     5-Sep-2005 (CT) `[` and `]` added to `xml_format`
#     5-Sep-2005 (CT) `__init__` removed
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    20-Nov-2007 (MG)  Imports fixed
#    26-Feb-2012 (MG) `__future__` imports added
#     8-Sep-2023 (CT) Use r-strings for strings with `\#`
#                     (PY 3.12 compatibility)
#    ««revision-date»»···
#--

from   _TFL                   import TFL
import _TFL._SDG._XML.Element
import _TFL._SDG._XML.External_Id

class Doctype (TFL.SDG.XML.Element) :
    r"""Model the doctype declaration of a XML document

       >>> from _TFL._SDG._XML import Decl
       >>> from _TFL._SDG._XML.External_Id import *
       >>> dt = Doctype ( "Test"
       ...              , Decl.Element  ("Test", "(head, body, tail)")
       ...              , Decl.Element  ("head", "(title, author)")
       ...              , Decl.Element  ("body", r"(\#PCDATA)")
       ...              , Decl.Element  ("tail", "(disclaimer)")
       ...              , Decl.Attlist  ( "head"
       ...                              , r"Date CDATA \#REQUIRED"
       ...                              , r"Version CDATA \#REQUIRED"
       ...                              )
       ...              , Decl.Notation ( "GIF", "SYSTEM '/usr/bin/display'")
       ...              , Decl.Entity   ( "entity"
       ...                              , "'An internal general parsed entity'"
       ...                              )
       ...              , Decl.Parameter( "parameter", "<!ELEMENT SAMPLE ANY>")
       ...              , Decl.Unparsed ( "unparsed"
       ...                              , "SYSTEM '/var/local/fubar.gif'"
       ...                              , "GIF"
       ...                              )
       ...              , dtd = "test.dtd"
       ...              )
       >>> dt.write_to_xml_stream ()
       <!DOCTYPE Test SYSTEM "test.dtd"
         [ <!ELEMENT Test (head, body, tail) >
           <!ELEMENT head (title, author) >
           <!ELEMENT body (\#PCDATA) >
           <!ELEMENT tail (disclaimer) >
           <!ATTLIST head Date CDATA \#REQUIRED
                      Version CDATA \#REQUIRED >
           <!NOTATION GIF SYSTEM '/usr/bin/display' >
           <!ENTITY entity 'An internal general parsed entity' >
           <!ENTITY % parameter <!ELEMENT SAMPLE ANY> >
           <!ENTITY unparsed SYSTEM '/var/local/fubar.gif' NDATA GIF >
         ]
       >
       >>> dt = Doctype ("svg", dtd = External_Id_Public
       ...     ( "-//W3C//DTD SVG 1.0//EN"
       ...     , "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd"
       ...     ))
       >>> dt.write_to_xml_stream ()
       <!DOCTYPE svg PUBLIC
           "-//W3C//DTD SVG 1.0//EN"
           "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
       >>> dt = Doctype ("svg", dtd = External_Id ("svg10.dtd"))
       >>> dt.write_to_xml_stream ()
       <!DOCTYPE svg SYSTEM "svg10.dtd">
    """

    front_args           = ("root_element", )
    init_arg_defaults    = dict \
        ( root_element   = None
        , dtd            = None
        )

    elem_type            = "DOCTYPE"

    xml_format           = \
        ( """<!DOCTYPE %(root_element)s %(::*dtd:)s"""
            """%(:front=%(NL)s  [%(" " * (indent_offset + 1))s"""
              """¡rear=%(NL)s  ]%(chr (10))s"""
              """¡sep=%(" " * (indent_offset + 4))s"""
              """:*body_children"""
              """:)s"""
          """>"""
        )

    _autoconvert         = dict \
        ( dtd            =
            lambda s, k, v : s._convert (v, TFL.SDG.XML.External_Id)
        ,
        )

# end class Doctype

if __name__ != "__main__" :
    TFL.SDG.XML._Export ("*")
### __END__ TFL.SDG.XML.Doctype
