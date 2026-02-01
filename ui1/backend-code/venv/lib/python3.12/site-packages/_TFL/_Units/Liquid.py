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
#    TFL.Units.Liquid
#
# Purpose
#    Liquid capacity units
#
# Revision Dates
#     8-Aug-2004 (CT) Creation
#     5-Jun-2020 (CT) Add `Command`
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.Object
import _TFL._Units.Kind
import _TFL._Units.Volume

class Liquid (TFL.Units.Kind) :
    """Units of liquid capacity

       >>> Liquid (1)
       1
       >>> Liquid (1.0, "oz")
       0.029573
       >>> Liquid (1.0, "dr")
       0.003696625
       >>> Liquid (1.0, "gal")
       3.785344
       >>> Liquid (1.0, "pt")
       0.473168
    """

    Volume            = TFL.Units.Volume
    Unit              = TFL.Units.Unit

    base_unit         = Unit ("liter", 1.0, "l")
    _ounce            = 0.029573
    _units            = \
        (
        # SI prefixes
          Unit ("nanoliter",         TFL.Units.nano,  "nl")
        , Unit ("microliter",        TFL.Units.micro, "ul")
        , Unit ("milliliter",        TFL.Units.milli, "ml")
        , Unit ("centiliter",        TFL.Units.centi, "cl")
        , Unit ("deciliter",         TFL.Units.deci,  "dl")
        , Unit ("hectoliter",        TFL.Units.hecto, "hl")
        , Unit ("kiloliter",         TFL.Units.kilo,  "kl")
        , Unit ("cubic_decimeter",      1.0)
        , Unit ("cubic_meter",       1000.0)
        # US customary units
        , Unit ("ounce",             _ounce,          "oz")
        , Unit ("drop",              _ounce    / 360)
        , Unit ("drams",             _ounce    /   8, "dr")
        , Unit ("teaspoon",          _ounce    /   6, "tsp")
        , Unit ("tablespoon",        _ounce    /   2, "tb")
        , Unit ("cup",               _ounce    *   8)
        , Unit ("pint",              _ounce    *  16, "pt")
        , Unit ("quart",             _ounce    *  32, "qt")
        , Unit ("gallon",            _ounce    * 128, "gal")
        )

# end class Liquid

class _Liquid_Command (TFL.Units.Kind.Command) :
    """Convert liquid values from one unit to another."""

    _rn_prefix              = "_Liquid_"

    Kind                    = Liquid

Liquid.Command = _Liquid_Command # end class

if __name__ != "__main__" :
    TFL.Units._Export ("*")
else :
    Liquid.Command () ()
### __END__ TFL.Units.Liquid
