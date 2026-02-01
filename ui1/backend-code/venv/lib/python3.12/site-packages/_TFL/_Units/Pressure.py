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
#    TFL.Units.Pressure
#
# Purpose
#    Units of pressure
#
# Revision Dates
#     8-Aug-2004 (CT) Creation
#    19-Feb-2017 (CT) Add `hectopascal`
#     5-Jun-2020 (CT) Add `Command`
#    17-May-2021 (CT) Add `kilopascal`
#    ««revision-date»»···
#--

from   _TFL import TFL

import _TFL._Meta.Object
import _TFL._Units.Kind
import _TFL._Units.Prefix

class Pressure (TFL.Units.Kind) :
    """Units of pressure

       >>> Pressure (1.0)
       1
       >>> Pressure (1.0,"bar")
       100000
       >>> Pressure (1.0,"atm")
       101325
    """

    Unit              = TFL.Units.Unit

    base_unit         = Unit ("pascal", 1.0, "Pa")
    _units            = \
        ( ### see http://en.wikipedia.org/wiki/Conversion_of_units
        # SI prefixes
          Unit ("hectopascal",           TFL.Units.hecto, "hPa")
	, Unit ("kilopascal",            TFL.Units.kilo,  "kPa")
        # Usual units
        , Unit ("torr",                  133.3223684,     "torr")
        , Unit ("atmosphere",              1.01325E+5,    "atm")
        , Unit ("bar",                     1.0E+5,        "bar")
        # US customary units
        , Unit ("pound_per_square_foot",  47.880259,      "psf")
        , Unit ("pound_per_square_inch",   6.894757e3,    "psi")
        )

# end class Pressure

class _Pressure_Command (TFL.Units.Kind.Command) :
    """Convert pressure values from one unit to another."""

    _rn_prefix              = "_Pressure_"

    Kind                    = Pressure

Pressure.Command = _Pressure_Command # end class

if __name__ != "__main__" :
    TFL.Units._Export ("*")
else :
    Pressure.Command () ()
### __END__ TFL.Units.Pressure
