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
#    TFL.Units.Length
#
# Purpose
#    Length units
#
# Revision Dates
#     8-Aug-2004 (CT)  Creation
#     9-Feb-2005 (CED) Some additional units added
#    15-Feb-2006 (CT)  CED's additions corrected (rounding the speed of light
#                      in the context of units is a bad thing (TM))
#     8-Nov-2006 (CED) Some parsec variants added (used in astronomy for large
#                      structures)
#    28-Sep-2014 (CT)  Add `light_second`
#    26-Nov-2014 (CT)  Correct spelling of `deca` (not `deka`!)
#     5-Jun-2020 (CT)  Add `point`, `pica`
#     5-Jun-2020 (CT)  Add `Command`
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.Object
import _TFL._Units.Kind
import _TFL._Units.Prefix
import _TFL._Units.Unit

class Length (TFL.Units.Kind) :
    """Units of length.

       >>> Length (1)
       1
       >>> Length (1,"yd")
       0.9144
       >>> Length (1,"in")
       0.0254
       >>> Length (1,"fur")
       201.168
       >>> Length (1,"mi")
       1609.344
       >>> Length (1,"Nm")
       1852

       >>> print ("%.12g" % Length (72, "pt"))
       0.0254
       >>> print ("%.12g" % Length (72, "pt").as_in)
       1

    """

    Unit              = TFL.Units.Unit

    base_unit         = Unit ("meter", 1.0, "m")
    _parsec           = 3.0856775813e16
    _point            = 0.0003527777777777778 # 72 pt/in (Postscript points)
    _units            = \
        ( ### see http://en.wikipedia.org/wiki/Conversion_of_units
        # SI prefixes
          Unit ("nanometer",      TFL.Units.nano,            "nm")
        , Unit ("micrometer",     TFL.Units.micro,           "um")
        , Unit ("millimeter",     TFL.Units.milli,           "mm")
        , Unit ("centimeter",     TFL.Units.centi,           "cm")
        , Unit ("decimeter",      TFL.Units.deci,            "dm")
        , Unit ("decameter",      TFL.Units.deca,           "dam")
        , Unit ("hectometer",     TFL.Units.hecto,           "hm")
        , Unit ("kilometer",      TFL.Units.kilo,            "km")
        # US customary units
        , Unit ("mil",               2.54e-5,               "mil")
        , Unit ("inch",              0.0254,                 "in")
        , Unit ("foot",              0.3048,                 "ft")
        , Unit ("yard",              0.9144,                 "yd")
        , Unit ("rod",               5.0292,                 "rd")
        , Unit ("furlong",         201.168,                 "fur")
        , Unit ("statute_mile",   1609.344,                  "mi")
        , Unit ("nautical_mile",  1852.0,                    "Nm")
        # physics units
        , Unit ("astronomical_unit", 1.49597870691e11,       "AU")
        , Unit ("light_second",      299792458,              "ls")
        , Unit ("light_year",        9.4607304725808e15,     "ly")
        , Unit ("kiloparsec", TFL.Units.kilo * _parsec,     "kpc")
        , Unit ("megaparsec", TFL.Units.mega * _parsec,     "Mpc")
        , Unit ("gigaparsec", TFL.Units.giga * _parsec,     "Gpc")
        , Unit ("parsec",                      _parsec,      "pc")
        , Unit ("angstrom",       TFL.Units.nano / 10,        "A")
        # typesetting units
        , Unit ("point",                        _point,      "pt") # Postscript
        , Unit ("pica",                    12 * _point)
        )

# end class Length

class _Length_Command (TFL.Units.Kind.Command) :
    """Convert length values from one unit to another."""

    _rn_prefix              = "_Length_"

    Kind                    = Length

Length.Command = _Length_Command # end class

if __name__ != "__main__" :
    TFL.Units._Export ("*")
else :
    Length.Command () ()
### __END__ TFL.Units.Length
