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
#    TFL.SDG.C.Node
#
# Purpose
#    Model a node of the code in a C file
#
# Revision Dates
#    26-Jul-2004 (CT) Creation
#    27-Jul-2004 (CT) Creation continued
#    28-Jul-2004 (CT) Creation continued...
#     2-Aug-2004 (CT) `children_group_names` redefined
#     2-Aug-2004 (CT) `write_to_c_stream` and `write_to_h_stream` added
#     2-Aug-2004 (CT) Methods put into alphabetical order
#     3-Aug-2004 (CT) `Then`, `Elseif`, and `Else` added (including their
#                     respective `_children` properties)
#     9-Aug-2004 (CT) `Case` and `Default` added (including their
#                     respective `_children` properties)
#     9-Aug-2004 (CT) Defaults of `description` and `eol_desc` changed
#                     from `""` to `None`
#    12-Aug-2004 (MG) `Incl` group removed (nice try)
#    12-Aug-2004 (MG) `formatted` pass * args and ** kw to super function
#    26-Aug-2004 (CT)  `_convert` moved to `TFL.SDG.Node`
#    23-Sep-2004 (MG) `vaps_channel_format` and friends added
#     7-Oct-2004 (CED) `apidoc_tex_format` and friends added
#    31-Oct-2011 (MG)  imports corrected
#    26-Feb-2012 (MG) `__future__` imports added
#    19-Apr-2020 (CT)  Use "``" for doc strings, not "`'"
#    ««revision-date»»···
#--

from   _TFL              import TFL
from   _TFL.pyk          import pyk

import _TFL._SDG._C
import _TFL._SDG.Node

from   _TFL.NO_List      import NO_List
from   _TFL.predicate    import *

H  = 1
C  = 2
HC = H | C

class _C_Node_ (TFL.SDG.Node) :
    """Model a node of the code in a C file"""

    _real_name           = "Node"

    base_indent          = "  "
    description_level    = 1
    eol_desc_level       = description_level + 4
    star_level           = 1
    pass_scope           = True

    children_group_names = \
        ( Body
        , Decl
        , Head
        , Tail
        , Then
        , Elseif
        , Else
        , Case
        , Default
        )                = range (9)
    body_children        = property (lambda s : s.children_groups [s.Body])
    decl_children        = property (lambda s : s.children_groups [s.Decl])
    head_children        = property (lambda s : s.children_groups [s.Head])
    tail_children        = property (lambda s : s.children_groups [s.Tail])
    then_children        = property (lambda s : s.children_groups [s.Then])
    elseif_children      = property (lambda s : s.children_groups [s.Elseif])
    else_children        = property (lambda s : s.children_groups [s.Else])
    case_children        = property (lambda s : s.children_groups [s.Case])
    default_children     = property (lambda s : s.children_groups [s.Default])

    init_arg_defaults    = dict \
        ( description    = None
        , eol_desc       = None
        , scope          = HC
        )

    _autoconvert         = dict \
        ( description    =
              lambda s, k, v : s._convert_c_comment (k, v, eol = False)
        , eol_desc       =
              lambda s, k, v : s._convert_c_comment (k, v, eol = True)
        )

    _list_of_formats     = TFL.SDG.Node._list_of_formats + \
        ( "c_format", "h_format", "vaps_channel_format", "apidoc_tex_format")

    _scope_filter        = dict \
        ( c_format       = C
        , h_format       = H
        )

    vaps_channel_format  = "" ### not implemented for all types
    apidoc_tex_format    = "" ### not implemented for all types

    def as_c_code (self, base_indent = None) :
        return self.formatted ("c_format", base_indent = base_indent)
    # end def as_c_code

    def as_h_code (self, base_indent = None) :
        return self.formatted ("h_format", base_indent = base_indent)
    # end def as_h_code

    def as_vaps_channel (self, base_indent = None) :
        return self.formatted \
            ("vaps_channel_format", base_indent = base_indent)
    # end def as_c_code

    def as_apidoc (self, base_indent = None) :
        return self.formatted \
            ("apidoc_tex_format", base_indent = base_indent)
    # end def as_apidoc

    def formatted (self, format_name, * args, ** kw) :
        if self.scope & self._scope_filter.get (format_name, 0xFF) :
            return self.__super.formatted (format_name, * args, ** kw)
        else :
            return ()
    # end def formatted

    def write_to_c_stream (self, cstream = None, gauge = None) :
        """Write `self` and all elements in `self.children` to `cstream`.
        """
        self._write_to_stream (self.as_c_code (), cstream, gauge)
    # end def write_to_c_stream

    write_to_stream = write_to_c_stream

    def write_to_h_stream (self, hstream = None, gauge = None) :
        self._write_to_stream (self.as_h_code (), hstream, gauge)
    # end def write_to_h_stream

    def write_to_vaps_channel (self, stream = None, gauge = None) :
        self._write_to_stream (self.as_vaps_channel (), stream, gauge)
    # end def write_to_vaps_channel

    def write_to_apidoc (self, stream = None, gauge = None) :
        self._write_to_stream (self.as_apidoc (), stream, gauge)
    # end def write_to_apidoc

    def _convert_c_comment (self, name, value, eol = 0, new_line_col = 0) :
        result = value
        if result  and isinstance (result, pyk.string_types) :
            result = (result, )
        if result and isinstance (result, (tuple, list)) :
            result = TFL.SDG.C.Comment \
                  ( *  result
                  , ** dict
                      ( level        = getattr
                            ( self, "%s_level" % (name, )
                            , self.description_level
                            )
                      , stars        = self.star_level
                      , eol          = eol
                      , new_line_col = new_line_col
                      )
                  )
        return result
    # end def _convert_c_comment

    def _convert_c_stmt (self, value) :
        if value and isinstance (value, pyk.string_types) :
            result = []
            for s in value.split (";") :
                stmt = self._convert (s.strip (), TFL.SDG.C.Statement)
                if stmt :
                    result.append (stmt)
        else :
            if isinstance (value, (list, tuple, NO_List)) :
                result = value
            else :
                result = [value]
        return result
    # end def _convert_c_stmt

    def _force (self, value, Class, * args, ** kw) :
        """Converts `value` to an instance of `Class`."""
        value = self._convert (value, Class, * args, ** kw)
        if not isinstance (value, Class) :
            value = Class (value, * args, ** kw)
        return value
    # end def _force

    def _insert (self, child, index, children, delta = 0) :
        if child :
            self._update_scope_child (child, self.scope)
            self.__super._insert (child, index, children, delta)
    # end def _insert

    def _update_scope (self, scope) :
        self.scope = self.scope & scope
    # end def _update_scope

    def _update_scope_child (self, child, scope) :
        if self.pass_scope :
            child._update_scope (self.scope)
    # end def _update_scope_child

# end class _C_Node_

Node = _C_Node_

if __name__ != "__main__" :
    TFL.SDG.C._Export ("Node", "H", "C", "HC")
### __END__ TFL.SDG.C.Node
