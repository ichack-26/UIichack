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
#    TFL.SDG.C.Array
#
# Purpose
#    C array declaration
#
# Revision Dates
#     9-Aug-2004 (CT)  Creation
#    12-Aug-2004 (MG)  Format changed
#    21-Sep-2004 (CT)  `c_format` changed (use `head` instead of `front` for
#                      `description`)
#    23-Sep-2004 (CT)  `c_format` changed (total revamp of `x_forms` for
#                      `initializers`)
#    23-Sep-2004 (MG)  `vaps_channel_format` added
#    27-Oct-2004 (MG)   Calculate the default of `bounds` based on the length
#                       of `init` (to be backward compatible)
#    16-Nov-2004 (MG)  Multidimension array support added
#    16-Sep-2005 (MG)  Changed to support `fmt` again
#    19-Oct-2006 (CED) Length check added
#    31-Jul-2007 (MG)  Add description to `h_format`
#    18-Oct-2007 (MZO) [25170] `init_comments` added
#     6-Dec-2007 (CT) Imports fixed
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
from   _TFL.pyk          import pyk

import _TFL._SDG._C._Decl_
import _TFL._SDG._C.Expression
import _TFL._SDG._C.Struct
import _TFL._SDG._C.Type
import _TFL._SDG._C.Var

from   _TFL.predicate    import un_nested

class Array (TFL.SDG.C._Var_) :
    """C array declaration"""

    Ancestor             = TFL.SDG.C._Var_

    init_arg_defaults    = dict \
        ( bounds         = ""
        , fmt            = "%s"
        , per_row        = 0
        )

    _autoconvert         = dict \
        ( bounds         = lambda s, k, v : s._convert_bounds (v)
        )
    _bounds              = property (lambda s : "][".join (s.bounds))
    _common_format       = "".join \
        ( ( Ancestor._common_head
          , """ [%(::._bounds:)s]"""
          )
        )
    h_format             = "".join \
        ( ( _common_format
          , ";%(:head= :*description:)s"
          )
        )

    c_format             = "".join \
        ( ( _common_format
          , """%(:front= =%(NL)s%(base_indent)s:*initializers:)s"""
          , ";"
          , """%(:head= :*description:)s"""
          )
        )

    vaps_channel_format = """
        %(name)s     %(::._bounds:)s     %(::*type:)s
        """
    ### to be able to use `Ancestor._common_format` which references `struct`
    struct               = None

    def __init__ \
        (self, type, name
        , bounds        = None
        , init          = ()
        , init_comments = ()
        , ** kw
        ) :
        if bounds is None :
            bounds = len (init)
        if isinstance (bounds, int) :
            assert len (init) <= bounds, (bounds, init)
        self.__super.__init__ \
            (type, name, bounds = bounds, init = init, ** kw)
        if self.init :
            self.initializers = self._setup_initializers \
                (self.init, init_comments = init_comments)
    # end def __init__

    def _convert_bounds (self, bounds) :
        if isinstance (bounds, pyk.string_types + pyk.int_types) :
            bounds = (bounds, )
        return [str (b) for b in bounds]
    # end def _convert_bounds

    def _setup_initializers \
        ( self
        , init_list
        , description   = None
        , init_comments = ()
        ) :
        result   = TFL.SDG.C.Init_Comp (description = description)
        t        = self._struct or self.type
        if isinstance (t, (TFL.SDG.C.Struct, TFL.SDG.C.Array)) :
            Init = t._setup_initializers
        else :
            if len (self.bounds) <= 1 :
                fmt = self.fmt.replace ("%%", "%")
                Init = lambda v, ** kw : \
                           TFL.SDG.C.Init_Atom (fmt % (v, ), ** kw)
                kw   = dict (format = self.fmt)
            else :
                return self._apply_array_level (init_list, description or "")
        if not init_comments :
            init_comments = [None] * len (init_list)
        for k, (v, comment) in enumerate (zip (init_list, init_comments)) :
            d = "[%s]" % k
            if comment :
                d = "%s %s" % (d, comment)
            result.add (Init (v, description = d))
        return result
    # end def _setup_initializers

    def _apply_array_level (self, init_list, level) :
        result = TFL.SDG.C.Init_Comp (description = "%s" % (level, ))
        for k, v in enumerate (init_list) :
            desc = "%s[%d]" % (level, k)
            if isinstance (v, (tuple, list)) :
                result.add (self._apply_array_level (v, desc))
            else :
                result.add ( TFL.SDG.C.Init_Atom (v, description = desc))
        return result
    # end def _apply_array_level

# end class Array

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.Array
