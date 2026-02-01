# -*- coding: utf-8 -*-
# Copyright (C) 2006-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Units.Time
#
# Purpose
#    Time units
#
# Revision Dates
#     9-Feb-2005 (CED) Creation
#    15-Feb-2006 (CT)  Done right
#     8-Nov-2006 (CED) `microfortnight` added (used in VMS)
#     5-Jun-2020 (CT)  Add `Command`
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.Object
import _TFL._Units.Kind
import _TFL._Units.Prefix
import _TFL._Units.Unit

class Time (TFL.Units.Kind) :
    """Units of time.

       >>> Time (1)
       1
       >>> Time (1, "ns")
       1e-09
       >>> Time (1, "d")
       86400
       >>> Time (1, "wk")
       604800
       >>> Time (1, "wk") == Time (7, "d")
       True
    """

    Unit          = TFL.Units.Unit

    base_unit     = Unit ("second", 1.0, "s")

    _week         = 3600.0 * 24.0 * 7.0
    _units        = \
        ( ### see http://en.wikipedia.org/wiki/Conversion_of_units
        # SI prefixes
          Unit ("attosecond",      TFL.Units.atto,   "as")
        , Unit ("femtosecond",     TFL.Units.femto,  "fs")
        , Unit ("picosecond",      TFL.Units.pico,   "ps")
        , Unit ("nanosecond",      TFL.Units.nano,   "ns")
        , Unit ("microsecond",     TFL.Units.micro,  "us")
        , Unit ("millisecond",     TFL.Units.milli,  "ms")
        # Usual units
        , Unit ("jiffy",                  1 / 60.0)
        , Unit ("minute",                     60.0, "min")
        , Unit ("moment",                     90.0)
        , Unit ("hour",                     3600.0,  "h")
        , Unit ("day",               3600.0 * 24.0,  "d")
        , Unit ("week",                      _week, "wk")
        # Unusual units
        , Unit ("microfortnight",  TFL.Units.micro * 2.0 * _week)
        , Unit ("fortnight",                         2.0 * _week)
        # physics units
        , Unit ("planck_time",     1.351211818e-43)
        )

# end class Time

class _Time_Command (TFL.Units.Kind.Command) :
    """Convert time values from one unit to another."""

    _rn_prefix              = "_Time_"

    Kind                    = Time

Time.Command = _Time_Command # end class

if __name__ != "__main__" :
    TFL.Units._Export ("*")
else :
    Time.Command () ()
### __END__ TFL.Units.Time
