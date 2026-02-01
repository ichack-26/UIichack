# -*- coding: utf-8 -*-
# Copyright (C) 2015 Christian Tanzer All rights reserved
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
#    TFL.ui_display
#
# Purpose
#    Generic function returning a string usable for display in user interface
#
# Revision Dates
#     6-Feb-2015 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL                       import TFL

from   _TFL._Meta.Single_Dispatch import Single_Dispatch
from   _TFL.portable_repr         import portable_repr
from   _TFL.pyk                   import pyk

import decimal

@Single_Dispatch
def ui_display (obj) :
    return portable_repr (obj)
# end def ui_display

@ui_display.add_type (decimal.Decimal, * pyk.int_types)
def _ui_display_int (obj) :
    return str (obj)
# end def _ui_display_int

@ui_display.add_type (float)
def _ui_display_float (obj) :
    return "%.2f" % obj
# end def _ui_display_float

@ui_display.add_type (* pyk.string_types)
def _ui_display_string (obj) :
    return pyk.decoded (obj)
# end def _ui_display_string

__doc__ = """
``ui_display`` returns a string representation of `obj`  usable for display
in an user interface.

Examples::

    >>> print (ui_display (1))
    1

    >>> print (ui_display (1.))
    1.00

    >>> print (ui_display (1.2))
    1.20

    >>> print (ui_display (1.23))
    1.23

    >>> print (ui_display (1.234))
    1.23

    >>> print (ui_display (1.235))
    1.24

    >>> print (ui_display ("1"))
    1

    >>> print (ui_display ("a"))
    a

    >>> print (ui_display (u"a"))
    a

For types with no specific implementation, ``ui_display`` returns the
``portable_repr``:

    >>> import datetime
    >>> d = datetime.date (2014, 2, 6)

    >>> print (ui_display (d))
    datetime.date(2014, 2, 6)

Adding an implementation for a specific type is easy enough, though::

    >>> @ui_display.add_type (datetime.date)
    ... def _ui_display_date (obj) :
    ...     return str (obj)

    >>> print (ui_display (d))
    2014-02-06

"""

if __name__ != "__main__" :
    TFL._Export ("ui_display")
### __END__ TFL.ui_display
