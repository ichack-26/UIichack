# -*- coding: utf-8 -*-
# Copyright (C) 2016-2020 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.dc_base32
#
# Purpose
#    Douglas Crockford's base32 encoding
#
# Revision Dates
#     7-Dec-2016 (CT) Creation
#    ««revision-date»»···
#--

"""
Implement Douglas Crockford's base32 encoding as defined in
http://www.crockford.com/wrmg/base32.html.
"""

from   _TFL        import TFL

symbols       = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
check_symbols = symbols + "*~$=U"

base          = len (symbols)
check_base    = len (check_symbols)

decode_map    = dict \
    ( { (c, i) for i, c in enumerate (check_symbols) }
    , I = 1
    , L = 1
    , O = 0
    )

def check_symbol (number) :
    """Check symbol for `number` using Douglas Crockford's base32 encoding."""
    return check_symbols [number % check_base]
# end def check_symbol

def decoded (string) :
    """Decode `string` in Douglas Crockford's base32 encoding to number.

    >>> decoded ("1A")
    42

    >>> decoded ("3RJ0")
    123456

    >>> decoded ("1A31-X0PH-PND")
    1481107684514477

    """
    return _decoded (normalized (string))
# end def decoded

def decoded_checked (string) :
    """Decode `string` with check symbol in Douglas Crockford's base32 encoding
       to number.

    >>> decoded_checked ("1A5")
    42

    >>> with expect_except (ValueError) :
    ...     decoded_checked ("1A6")
    ValueError: Invalid check symbol `6` for `1A`

    >>> decoded_checked ("3RJ0R")
    123456

    >>> decoded_checked ("1A-31-X0-PH-PN-D7")
    1481107684514477

    """
    s      = normalized (string)
    vs, cs = s [:-1], s [-1]
    result = _decoded   (vs)
    check  = decode_map [cs.upper ()]
    if result % check_base != check :
        raise ValueError ("Invalid check symbol `%s` for `%s`" % (cs, vs))
    return result
# end def decoded_checked

def encoded (number) :
    """Encode `number` using Douglas Crockford's base32 encoding.

    >>> print (encoded (42))
    1A

    >>> print (encoded (123456))
    3RJ0

    >>> print (encoded (1481107684514477))
    1A31X0PHPND

    """
    n = int (number)
    if n < 0 :
        raise ValueError \
            ("dc_base32.encoded expects non-negative numbers; got %s" % number)
    return "".join (_gen_encoded (n)) [::-1]
# end def encoded

def encoded_checked (number) :
    """Encode `number` using Douglas Crockford's base32 encoding plus check
       symbol.

    >>> print (encoded_checked (42))
    1A5

    >>> print (encoded_checked (123456))
    3RJ0R

    >>> print (encoded_checked (1481107684514477))
    1A31X0PHPND7

    """
    return encoded (number) + check_symbol (number)
# end def encoded_checked

def normalized (string) :
    """Normalize a base32 encoded string."""
    return string.upper ().replace ("-", "")
# end def normalized

def _decoded (string) :
    result = 0
    for s in string.upper () :
        result = result * base + decode_map [s]
    return result
# end def _decoded

def _gen_encoded (number, symbols = symbols, base = base) :
    while number > 0 :
        number, i = divmod (number, base)
        yield symbols [i]
# end def _gen_encoded

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.dc_base32
