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
#    TFL.Units.Energy
#
# Purpose
#    Units of energy
#
# Revision Dates
#    15-Feb-2006 (CT) Creation
#     5-Jun-2020 (CT) Add `Command`
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.Object
import _TFL._Units.Kind

class Energy (TFL.Units.Kind) :
    """Units of energy

       >>> Energy (1.0)
       1
       >>> Energy (1, "cal")
       4.1868
       >>> Energy (1, "kWh")
       3600000
    """

    Unit              = TFL.Units.Unit

    base_unit         = Unit ("joule", 1.0, "J")
    _units            = \
        ( ### see http://en.wikipedia.org/wiki/Conversion_of_units
          Unit ("electron_volt",           1.602176e-19,  "eV")
        , Unit ("erg",                     1.0e-7,        "erg")
        , Unit ("calorie",                 4.1868,        "cal")
        , Unit ("kilocalorie",             4.1868e3,      "kcal")
        , Unit ("horsepower_hour",         2.6845e6,      "hph")
        , Unit ("kilowatt_hour",           3.6e6,         "kWh")
        , Unit ("watt_hour",               3.6e3,         "Wh")
        )

# end class Energy

class _Energy_Command (TFL.Units.Kind.Command) :
    """Convert Energy values from one unit to another."""

    _rn_prefix              = "_Energy_"

    Kind                    = Energy

Energy.Command = _Energy_Command # end class

if __name__ != "__main__" :
    TFL.Units._Export ("*")
else :
    Energy.Command () ()
### __END__ TFL.Units.Energy
