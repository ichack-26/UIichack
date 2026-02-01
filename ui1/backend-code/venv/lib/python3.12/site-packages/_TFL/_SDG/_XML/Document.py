# -*- coding: utf-8 -*-
# Copyright (C) 2004-2013 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.XML.Document
#
# Purpose
#    Model a XML document (i.e., prolog plus root element)
#
# Revision Dates
#    26-Aug-2004 (CT) Creation
#    17-Sep-2004 (CT) Doctest changed (added `%` to document text)
#    21-Oct-2004 (CT) Use `"` instead of `'` in output
#     5-Sep-2005 (CT) Derive from `XML.Node` instead of `XML.Element`
#     5-Sep-2005 (CT) `root_element` added and `insert` redefined to delegate
#                     to `root_element`
#     5-Sep-2005 (CT) Doctest `svg` added
#     6-Sep-2005 (CT) Doctest adapted to change of `_attr_values`
#    20-Sep-2005 (CT) Doctest with over-long attributes added
#    29-Nov-2007 (CT) Another doctest with over-long attributes added
#    29-Aug-2008 (CT) Import for `Elem_Type` added to fix doctest
#    26-Feb-2012 (MG) `__future__` imports added
#    18-Nov-2013 (CT) Change default `encoding` to `utf-8`
#    ««revision-date»»···
#--

from   _TFL                   import TFL
from   _TFL.pyk               import pyk

import _TFL.I18N
import _TFL._SDG._XML.Comment
import _TFL._SDG._XML.Doctype
import _TFL._SDG._XML.Element
import _TFL._SDG._XML.Elem_Type
import _TFL._SDG._XML.Node

class Document (TFL.SDG.XML.Node) :
    """Model a XML document (i.e., the root element)

       >>> nl = chr (10)

       >>> d = Document ( "Memo", "First line of text"
       ...              , "& a second line of %text"
       ...              , "A third line of %text &entity; including"
       ...              , doctype     = "memo"
       ...              , description = "Just a test"
       ...              )
       >>> lines = list (d.formatted ("xml_format"))
       >>> print (nl.join (lines))
       <?xml version="1.0" encoding="utf-8" standalone="yes"?>
       <!DOCTYPE memo >
       <!-- Just a test -->
       <Memo>
         First line of text
         &amp; a second line of %text
         A third line of %text &entity; including
       </Memo>
       >>> d = Document ( "Memo", "First line of text"
       ...              , "& a second line of %text"
       ...              , "A third line of %text &entity; including"
       ...              , doctype     = TFL.SDG.XML.Doctype
       ...                                  ("memo", dtd = "memo.dtd")
       ...              , description = "Just a test"
       ...              )
       >>> print (nl.join (d.formatted ("xml_format")))
       <?xml version="1.0" encoding="utf-8" standalone="yes"?>
       <!DOCTYPE memo SYSTEM "memo.dtd">
       <!-- Just a test -->
       <Memo>
         First line of text
         &amp; a second line of %text
         A third line of %text &entity; including
       </Memo>
       >>> s = Document ( TFL.SDG.XML.Element
       ...                  ( "svg"
       ...                  , x_attrs     = dict
       ...                      ( viewBox = "10 60 450 260"
       ...                      , xmlns   = "http://www.w3.org/2000/svg"
       ...                      , width   = "100%"
       ...                      , height  = "100%"
       ...                      )
       ...                  )
       ...              , "..."
       ...              , encoding        = "UTF-8"
       ...              , standalone      = "no"
       ...              )
       >>> print (nl.join (s.formatted ("xml_format")))
       <?xml version="1.0" encoding="UTF-8" standalone="no"?>
       <svg height="100%" viewBox="10 60 450 260" width="100%"
            xmlns="http://www.w3.org/2000/svg"
       >
         ...
       </svg>
       >>> attrs = { "xmlns:fx"      : "http://www.asam.net/xml/fbx"
       ...         , "xmlns:ho"      : "http://www.asam.net/xml"
       ...         , "xmlns:flexray" : "http://www.asam.net/xml/fbx/flexray"
       ...         , "xmlns:xsi"
       ...         : "http://www.w3.org/2001/XMLSchema-instance"
       ...         , "xsi:schemaLocation"
       ...         : "http://www.asam.net/xml/fbx/all/fibex4multiplatform.xsd"
       ...         , "VERSION"       : "1.0.0a"
       ...         }
       >>> d = Document (TFL.SDG.XML.Element ("fx:FIBEX", x_attrs = attrs ))
       >>> print (nl.join (d.formatted ("xml_format")))
       <?xml version="1.0" encoding="utf-8" standalone="yes"?>
       <fx:FIBEX VERSION="1.0.0a"
                 xmlns:flexray="http://www.asam.net/xml/fbx/flexray"
                 xmlns:fx="http://www.asam.net/xml/fbx"
                 xmlns:ho="http://www.asam.net/xml"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://www.asam.net/xml/fbx/all/fibex4multiplatform.xsd"
       >
       </fx:FIBEX>

       ### Test for linebreaking in/between attribute values
       >>> Elem_Type = TFL.SDG.XML.Elem_Type
       >>> root_elem = Elem_Type ("foo", xmlns = "http://foo/bar")
       >>> elem  = Elem_Type ("bar", baz1 = None, baz2 = None, baz3 = None)
       >>> root  = root_elem ()
       >>> child = elem ( baz1 = "This really is the value of baz1"
       ...     , baz2 = "This really is the value of baz2"
       ...     , baz3 = "This really is the value of baz3"
       ...     )
       >>> root.add (child)
       >>> d = Document (root)
       >>> d.write_to_xml_stream ()
       <?xml version="1.0" encoding="utf-8" standalone="yes"?>
       <foo xmlns="http://foo/bar">
         <bar baz1="This really is the value of baz1"
              baz2="This really is the value of baz2"
              baz3="This really is the value of baz3"
         >
         </bar>
       </foo>
    """

    front_args           = ("root_element", )
    init_arg_defaults    = dict \
        ( doctype        = None
        , encoding       = "utf-8"
        , root_element   = None
        , standalone     = "yes"
        , xml_version    = 1.0
        )

    xml_format           = """
        <?xml version="%(xml_version)s" encoding="%(encoding)s" standalone="%(standalone)s"?>
        %(::*doctype:)s
        %(::*description:)s
        %(::*root_element:)s
    """

    _autoconvert         = dict \
        ( doctype        = lambda s, k, v : s._convert (v, TFL.SDG.XML.Doctype)
        , root_element   = lambda s, k, v : s._convert (v, TFL.SDG.XML.Element)
        , standalone     = lambda s, k, v :
            { "yes" : "yes"
            , True  : "yes"
            , False : "no"
            , "no"  : "no"
            } [v]
        )

    def formatted (self, format_name, * args, ** kw) :
        for r in self.__super.formatted (format_name, * args, ** kw) :
            if str != str and isinstance (r, str) :
                ### Only do this for Python2
                r = r.encode (self.encoding, "xmlcharrefreplace")
            yield r
    # end def formatted

    def insert (self, child, index = None, delta = 0) :
        self.root_element.insert (child, index, delta)
    # end def insert

# end class Document

if __name__ != "__main__" :
    TFL.SDG.XML._Export ("*")
### __END__ TFL.SDG.XML.Document
