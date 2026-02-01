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
#    TFL.Units.Mass
#
# Purpose
#    Mass units
#
# Revision Dates
#     8-Aug-2004 (CT)  Creation
#     8-Nov-2006 (CED) `firkin` added (old british unit)
#    26-Nov-2014 (CT)  Use prefixes, add `decagram`
#     5-Jun-2020 (CT)  Add `Command`
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.Object
import _TFL._Units.Kind
import _TFL._Units.Prefix

class Mass (TFL.Units.Kind) :
    """Units of mass

       >>> Mass (1)
       1
       >>> Mass (1, "g")
       0.001
       >>> Mass (1, "dag")
       0.01
       >>> Mass (1, "t")
       1000
       >>> Mass (1, "oz")
       0.028349523125
       >>> Mass (1, "stone")
       6.35029318
       >>> Mass (1, "lb")
       0.45359237
    """

    Unit              = TFL.Units.Unit

    base_unit         = Unit ("kilogram", 1.0, "kg")
    _pound            = 0.45359237
    _units            = \
        (
        # SI prefixes (as base unit is `kilogram`, these are offset by `kilo`)
          Unit ("microgram", TFL.Units.micro / TFL.Units.kilo, "ug")
        , Unit ("milligram", TFL.Units.milli / TFL.Units.kilo, "mg")
        , Unit ("gram",                    1 / TFL.Units.kilo, "g")
        , Unit ("decagram",  TFL.Units.deca  / TFL.Units.kilo, "dag")
        , Unit ("ton",       TFL.Units.kilo,                   "t")
        # US customary units
        , Unit ("pound",     _pound,                           "lb")
        , Unit ("grain",     _pound / 7000)
        , Unit ("drams",     _pound /  256,                    "dr")
        , Unit ("ounce",     _pound /   16,                    "oz")
        , Unit ("short_ton", _pound * 2000)
        , Unit ("long_ton",  _pound * 2240)
        # Odd British unit
        , Unit ("stone",     _pound *   14)
        , Unit ("firkin",    40.91481)
        )

# end class Mass

class _Mass_Command (TFL.Units.Kind.Command) :
    """Convert mass values from one unit to another."""

    _rn_prefix              = "_Mass_"

    Kind                    = Mass

Mass.Command = _Mass_Command # end class

if __name__ != "__main__" :
    TFL.Units._Export ("*")
else :
    Mass.Command () ()
### __END__ TFL.Units.Mass
