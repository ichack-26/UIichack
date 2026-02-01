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
#    TFL.SDG.XML.Node
#
# Purpose
#    Model a node of a XML document
#
# Revision Dates
#     5-Sep-2005 (CT)  Creation (factored from Element)
#     5-Sep-2005 (CT)  `_attr_values` changed to sort `x_attrs` and to align "="
#     6-Sep-2005 (CT)  `kw` added to `as_xml` and `write_to_xml_stream`
#     6-Sep-2005 (CT)  `_attr_iter` factored from `_attr_values` (and
#                      alignment to "=" removed, again)
#     6-Sep-2005 (CT)  `_attr_values` changed to use `textwrap`
#     9-Sep-2005 (PGO) `_attr_values' modifies `textwrap`s word wrapping
#    20-Sep-2005 (CT)  `break_long_words = False` passed to
#                      `textwrap.TextWrapper`
#    20-Nov-2007 (MG)  Imports fixed
#    29-Nov-2007 (CT)  `_attr_values` changed to not use `textwrap` (quoted
#                      values should *not* be wrapped)
#    26-Feb-2012 (MG) `__future__` imports added
#    27-Aug-2012 (CT) Add and use `attr_name_translate`
#    18-Nov-2013 (CT) Change default `encoding` to `utf-8`
#    19-Apr-2020 (CT)  Use "``" for doc strings, not "`'"
#    ««revision-date»»···
#--

from   _TFL              import TFL
from   _TFL.pyk          import pyk

import _TFL._SDG._XML
import _TFL._SDG.Node

from   _TFL.Regexp       import *

class _XML_Node_ (TFL.SDG.Node) :
    """Model a node of a XML document"""

    _real_name           = "Node"

    attr_names           = ()
    attr_name_translate  = {}
    base_indent          = "  "
    encoding             = "utf-8"
    init_arg_defaults    = dict \
        ( description    = None
        ,
        )

    _autoconvert         = dict \
        ( description    = lambda s, k, v : s._convert (v, TFL.SDG.XML.Comment)
        ,
        )

    _list_of_formats     = TFL.SDG.Node._list_of_formats + \
        ( "xml_format", )

    _xml_name_pat        = Regexp ("[A-Za-z_:][-_:.A-Za-z0-9]*")
    _special_char_pat    = Regexp \
        ("[<>]|(&(?! %s;))" % _xml_name_pat.pattern, re.X)
    _special_quot_pat    = Regexp ("&(amp|lt|gt|apos|quot);")
    _wordsep_pat         = Regexp (r'(\s+)')

    def as_xml (self, base_indent = None, ** kw) :
        return self.formatted ("xml_format", base_indent = base_indent, ** kw)
    # end def as_xml

    def write_to_xml_stream (self, stream = None, gauge = None, ** kw) :
        """Write `self` and all elements in `self.children` to `stream`.
        """
        self._write_to_stream (self.as_xml (** kw), stream, gauge)
    # end def write_to_xml_stream

    def _attr_iter (self) :
        attr_values = \
            ( [(a, getattr (self, a)) for a in self.attr_names]
            + sorted (pyk.iteritems (self.x_attrs))
            )
        if attr_values :
            translate = lambda a : self.attr_name_translate.get (a, a)
            for a, v in attr_values :
                if v is not None :
                    k = translate (a)
                    v = str (v).replace ("'", "&quot;")
                    yield u'''%s="%s"''' % (k, v)
    # end def _attr_iter

    def _attr_values (self, * args, ** kw) :
        ow        = kw ["output_width"]
        ia        = kw ["indent_anchor"]
        ht        = kw ["ht_width"]
        max_width = max (ow - ia - ht - 4, 4)
        pieces    = []
        width     = 0
        for attr_value in self._attr_iter () :
            attr_len = len (attr_value)
            if pieces and (width + attr_len) > max_width :
                yield " ".join (pieces)
                pieces = []
                width  = 0
            width += attr_len + bool (pieces)
            pieces.append (attr_value)
        if pieces :
            yield " ".join (pieces)
    # end def _attr_values

    def _checked_xml_name (self, value) :
        if not self._xml_name_pat.match (value) :
            raise ValueError \
                ( "`%s` doesn not match %s"
                % (value, self._xml_name_pat.pattern)
                )
        return value
    # end def _checked_xml_name

    def _insert (self, child, index, children, delta = 0) :
        if child is not None :
            if isinstance (child, pyk.string_types) :
                import _TFL._SDG._XML.Char_Data
                child = TFL.SDG.XML.Char_Data (child)
            self.__super._insert (child, index, children, delta)
    # end def _insert

    def _special_char_replacer (self, match) :
        return { "&"      : "&amp;"
               , "<"      : "&lt;"
               , ">"      : "&gt;"
               , "'"      : "&apos;"
               , '"'      : "&quot;"
               } [match.group (0)]
    # end def _special_char_replacer

    def _special_quot_replacer (self, match) :
        return { "&amp;"  : "&"
               , "&lt;"   : "<"
               , "&gt;"   : ">"
               , "&apos;" : "'"
               , "&quot;" : '"'
               } [match.group (0)]
    # end def _special_quot_replacer

Node = _XML_Node_ # end class _XML_Node_

if __name__ != "__main__" :
    TFL.SDG.XML._Export ("*")
### __END__ TFL.SDG.XML.Node
