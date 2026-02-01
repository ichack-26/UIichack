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
#    TFL.SDG.M_Node
#
# Purpose
#    Meta class for SDG.Node classes
#
# Revision Dates
#    23-Jul-2004 (CT) Creation
#    26-Jul-2004 (CT) Creation continued
#    15-Dec-2005 (CT) `normalize_formats` changed to normalize for each class
#                     anew (to avoid nasty surprises with `sep` aliasing when
#                     format is shared between sibling classes with different
#                     values for `sep`)
#    20-Nov-2007 (MG) Imports fixed
#    29-Aug-2008 (CT) s/super(...)/__m_super/
#    26-Feb-2012 (MG) `__future__` imports added
#    26-Jan-2015 (CT) Use `M_Auto_Update_Combined`, not `M_Auto_Combine_Dicts`,
#                     as metaclass
#    ««revision-date»»···
#--

from   _TFL                            import TFL
from   _TFL.pyk                        import pyk

import _TFL._Meta.M_Auto_Update_Combined
import _TFL._Meta.M_Class
import _TFL._SDG
import _TFL._SDG.Formatter

from   _TFL.Regexp                     import *

_indent_pat = Regexp (r">*")

class M_Node (TFL.Meta.M_Auto_Update_Combined, TFL.Meta.M_Class) :
    """Meta class for SDG.Node classes"""

    __id                     = 0
    _attrs_to_update_combine = ("init_arg_defaults", "_autoconvert")

    def __init__ (cls, name, bases, dict) :
        cls.__m_super.__init__ (name, bases, dict)
        cls._normalize_formats ()
    # end def __init__

    def __call__ (cls, * args, ** kw) :
        result     = cls.__new__  (cls, * args, ** kw)
        cls.__id  += 1
        result.id  = cls.__id
        result.__init__ (* args, ** kw)
        return result
    # end def __call__

    def _normalize_format (cls, fn, f) :
        format_lines = []
        for line in f.strip ().split ("\n") :
            line  = line.strip ().replace ("\\n", "\n")
            level = _indent_pat.match (line).end ()
            cf    = line [level:]
            format_lines.append (TFL.SDG.Formatter (level, cf))
        setattr (cls, fn, format_lines)
        setattr (cls, "__%s" % fn, f)
    # end def _normalize_format

    def _normalize_formats (cls) :
        for fn in cls._list_of_formats :
            f = getattr (cls, fn, None)
            if f is not None :
                if not isinstance (f, pyk.string_types) :
                    f = getattr (cls, "__%s" % fn)
                cls._normalize_format (fn, f)
    # end def _normalize_formats

# end class M_Node

if __name__ != "__main__" :
    TFL.SDG._Export ("*")
### __END__ TFL.SDG.M_Node
