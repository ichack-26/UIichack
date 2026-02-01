# -*- coding: utf-8 -*-
# Copyright (C) 2011-2015 Martin Glueck All rights reserved
# ****************************************************************************
#
# Langstrasse 4, A--2244 Spannberg. martin@mangari.org
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Sphere
#
# Purpose
#    Distance calculation between two points on a sphere
#
# Revision Dates
#     6-Apr-2011 (MG) Creation
#    23-May-2011 (CT) `doctest` fixed (no floating point in output)
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL               import TFL
import _TFL._Meta.Object
import  math

class Sphere (TFL.Meta.Object) :
    """A sphere

    >>> p1 = Earth.Point (48.110278, 16.569722, 183) ### Airport Vienna    (VIE), Austria
    >>> p2 = Earth.Point (47.260278, 11.343889, 581) ### Airport Innsbruck (INN), Austria
    >>> print ("%10.2f" % Earth.distance (p1, p2))
    402469.91
    >>> print ("%10.2f" % Earth.distance (p2, p1))
    402469.91
    """

    class Point (TFL.Meta.Object) :
        """A point on a sphere."""

        def __init__ (self, lat, lon, height = 0) :
            self.lat    = lat
            self.lon    = lon
            self.height = height
        # end def __init__

    # end class Point
    #
    def __init__ (self, radius = None, diameter = None) :
        if radius is None :
            radius = diameter / 2.
        self.radius = radius
    # end def __init__

    def distance (self, p1, p2) :
        lat1 = math.radians (p1.lat)
        lng1 = math.radians (p1.lon)
        lat2 = math.radians (p2.lat)
        lng2 = math.radians (p2.lon)

        sin_lat1, cos_lat1 = math.sin (lat1), math.cos (lat1)
        sin_lat2, cos_lat2 = math.sin (lat2), math.cos (lat2)

        delta_lng            = lng2 - lng1
        cos_d_lng, sin_d_lng = math.cos (delta_lng), math.sin (delta_lng)

        # We're correcting from floating point rounding errors on very-near
        # and exact points here
        central_angle = math.acos \
            (min (1.0, sin_lat1 * sin_lat2 + cos_lat1 * cos_lat2 * cos_d_lng))

        d = math.atan2 \
            ( math.sqrt
                ( (cos_lat2 * sin_d_lng) ** 2
                + (cos_lat1 * sin_lat2 - sin_lat1 * cos_lat2 * cos_d_lng) ** 2
                )
            , sin_lat1 * sin_lat2 + cos_lat1 * cos_lat2 * cos_d_lng
            )
        return self.radius * d
    # end def distance

# end class Sphere

Earth = Sphere (6372795) ### Average radius of the earth in meters

if __name__ != "__main__" :
    TFL._Export ("Sphere", "Earth")
### __END__ TFL.Sphere
