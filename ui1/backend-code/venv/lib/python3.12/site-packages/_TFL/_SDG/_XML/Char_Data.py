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
#    TFL.SDG.XML.Char_Data
#
# Purpose
#    Model character data of a XML element
#
# Revision Dates
#    27-Aug-2004 (CT) Creation
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL                   import TFL
from   _TFL.pyk               import pyk

import _TFL._SDG._XML.Element

class Char_Data (TFL.SDG.XML.Leaf) :
    """Model character data of a XML element"""

    init_arg_defaults    = dict \
        ( text           = None
        )

    front_args           = ()
    rest_args            = "text"

    xml_format           = """%(::.text:)s"""

    _autoconvert         = dict \
        ( text           = lambda s, k, v : s._convert_text (v)
        )

    def _convert_text (self, args) :
        result = []
        for a in args :
            if a and isinstance (a, pyk.string_types) :
                a = self._special_char_pat.sub \
                    (self._special_char_replacer, a).split ("\n")
                result.extend (a)
            else :
                result.append (a)
        return result
    # end def _convert_text

# end class Char_Data

if __name__ != "__main__" :
    TFL.SDG.XML._Export ("*")
### __END__ TFL.SDG.XML.Char_Data
