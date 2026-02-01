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
#    TFL.Units.Area
#
# Purpose
#    Area units
#
# Revision Dates
#     8-Aug-2004 (CT)  Creation
#     8-Nov-2006 (CED) `nanoacre` added (used in chip design)
#    26-Nov-2014 (CT)  Correct spelling of `deca` (not `deka`!)
#     5-Jun-2020 (CT)  Add `Command`
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.Object
import _TFL._Units.Kind
import _TFL._Units.Length

class Area (TFL.Units.Kind) :
    """Units of area

       >>> Area (1.0)
       1
       >>> Area (1.0, "are")
       100
       >>> Area (1.0, "hectare")
       10000
       >>> Area (1.0, "sqin")
       0.00064516
       >>> Area (1.0, "sqft")
       0.09290304
       >>> Area (1.0, "sqyd")
       0.83612736
       >>> Area (1.0, "sqmi")
       2589988.11034
       >>> Area (1.0, "sqkm")
       1000000
       >>> Area (1.0, "acre")
       4046.8564224
       >>> Area (640, "acre") == Area (1.0, "sqmi")
       True
    """

    Length            = TFL.Units.Length
    Unit              = TFL.Units.Unit

    base_unit         = Unit ("square_meter", 1.0, "sqm")
    _are              = Length.decameter  ** 2
    _hectare          = Length.hectometer ** 2
    _sq_mile          = Length.statute_mile ** 2
    _units            = \
        ( ### see http://en.wikipedia.org/wiki/Conversion_of_units
        # SI prefixes
          Unit ("square_nanometer",   Length.nanometer    ** 2,  "sqnm")
        , Unit ("square_micrometer",  Length.micrometer   ** 2,  "squm")
        , Unit ("square_millimeter",  Length.millimeter   ** 2,  "sqmm")
        , Unit ("square_centimeter",  Length.centimeter   ** 2,  "sqcm")
        , Unit ("square_decimeter",   Length.decimeter    ** 2,  "sqdm")
        , Unit ("square_decameter",   _are,                      "sqdam")
        , Unit ("square_hectometer",  _hectare,                  "sqhm")
        , Unit ("square_kilometer",   Length.kilometer    ** 2,  "sqkm")
        , Unit ("are",                _are,)
        , Unit ("hectare",            _hectare,                  "ha")
        # US customary units
        , Unit ("square_mil",         Length.mil          ** 2,  "sqmil")
        , Unit ("square_inch",        Length.inch         ** 2,  "sqin")
        , Unit ("board",              Length.inch * Length.foot, "bd")
        , Unit ("square_foot",        Length.foot         ** 2,  "sqft")
        , Unit ("square_yard",        Length.yard         ** 2,  "sqyd")
        , Unit ("nanoacre", TFL.Units.nano * (_sq_mile / 640.0))
        , Unit ("acre",                       _sq_mile / 640.0,    "ac")
        , Unit ("square_mile",                _sq_mile,          "sqmi")
        )

# end class Area

class _Area_Command (TFL.Units.Kind.Command) :
    """Convert area values from one unit to another."""

    _rn_prefix              = "_Area_"

    Kind                    = Area

Area.Command = _Area_Command # end class

if __name__ != "__main__" :
    TFL.Units._Export ("*")
else :
    Area.Command () ()
### __END__ TFL.Units.Area
