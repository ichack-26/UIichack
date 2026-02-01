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
#    TFL.Units.Speed
#
# Purpose
#    Units of speed
#
# Revision Dates
#    15-Feb-2006 (CT) Creation
#     5-Jun-2020 (CT) Add `Command`
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.Object
import _TFL._Units.Kind
import _TFL._Units.Length
import _TFL._Units.Prefix
import _TFL._Units.Time
import _TFL._Units.Unit

class Speed (TFL.Units.Kind) :
    """Units of speed.

       >>> Speed (1)
       1
       >>> Speed (1, "kmh")
       0.277777777778
       >>> Speed (1, "c")
       299792458
    """

    Length        = TFL.Units.Length
    Time          = TFL.Units.Time
    Unit          = TFL.Units.Unit

    base_unit     = Unit ("meter_per_second", 1.0, "m/s")
    _units        = \
        ( ### see http://en.wikipedia.org/wiki/Conversion_of_units
        # Usual units
          Unit ("kilometer_per_hour", Length.kilometer     / Time.hour,   "kmh")
        # US customary units
        , Unit ("furlong_per_fortnight", Length.furlong    / Time.fortnight)
        , Unit ("mile_per_hour",      Length.statute_mile  / Time.hour,   "mph")
        , Unit ("knots",              Length.nautical_mile / Time.hour,    "kn")
        # physics units
        , Unit ("speed_of_light",     Length.light_second  / Time.second,   "c")
        )

# end class Speed

class _Speed_Command (TFL.Units.Kind.Command) :
    """Convert speed values from one unit to another."""

    _rn_prefix              = "_Speed_"

    Kind                    = Speed

Speed.Command = _Speed_Command # end class

if __name__ != "__main__" :
    TFL.Units._Export ("*")
else :
    Speed.Command () ()
### __END__ TFL.Units.Speed
