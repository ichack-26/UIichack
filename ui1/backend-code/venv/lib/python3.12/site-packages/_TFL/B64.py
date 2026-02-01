# -*- coding: utf-8 -*-
# Copyright (C) 1998-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.B64
#
# Purpose
#    Provide conversion to/from strings in Base64 number system
#
# Revision Dates
#    27-Nov-1998 (CT) Creation
#    12-Sep-2004 (CT) Factored from B64.py in lib/python
#    12-Sep-2004 (CT) `_ord_map` changed (sequence of characters in sorted
#                     order, `.` replaced by `_`)
#    12-Sep-2004 (CT) Optional parameters added to `atoi` and `itoa`
#    ««revision-date»»···
#--

_base    = 64
_chars   = "0123456789=ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
_ord_map = {}
for i, c in enumerate (_chars) :
    _ord_map [i] = c
    _ord_map [c] = i

def atoi (string, _ord_map = _ord_map) :
    """Convert `string` in B64 representation to integer. If the result is
       too large to fit a normal integer, Pythons long integer type is used.
    """
    result = 0
    for c in string :
        result = (result << 6) + _ord_map [c]
    return result
# end def atoi

def itoa (number, _base = _base, _ord_map = _ord_map) :
    """Convert `number` to string in B64 representation."""
    result = []
    if number == 0 :
        result.append ("0")
    elif number > 0 :
        while number > 0 :
            number, r = divmod (number, _base)
            result.append (_ord_map [r])
        result.reverse ()
    else :
        raise ValueError ("Cannot handle negative number %s." % (number, ))
    return "".join (result)
# end def itoa

if __name__ != "__main__" :
    from _TFL import TFL
    TFL._Export_Module ()
### __END__ B64
