# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.D2.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.D2.Cardinal_Direction
#
# Purpose
#    Cardinal directtion in 2D space
#
# Revision Dates
#    13-Aug-2012 (CT) Creation
#    16-Aug-2012 (CT) Add `Point.from_name` and `.as_name`
#    ««revision-date»»···
#--

from   _TFL           import TFL
from   _TFL.pyk       import pyk
from   _TFL._D2       import D2

from   _TFL.Math_Func import sign
from   _TFL.Regexp    import Regexp, re

import _TFL._D2.Point

class _Cardinal_Direction_ (D2._Point_) :
    """Base class for points expressed by cardinal directions in 2D space."""

    value_map      = \
        { ( 0, +1) : "N"
        , (+1, +1) : "NE"
        , (+1,  0) : "E"
        , (+1, -1) : "SE"
        , ( 0, -1) : "S"
        , (-1, -1) : "SW"
        , (-1,  0) : "W"
        , (-1, +1) : "NW"
        }

    name_map        = dict ((v, k) for k, v in pyk.iteritems (value_map))

    def _directions (self) :
        v_map = self.value_map
        x, y  = tuple (self)
        sx    = sign  (x)
        sy    = sign  (y)
        ax    = abs   (x)
        ay    = abs   (y)
        if ax == ay :
            if ax :
                yield (v_map [sx, sy], ax)
            else :
                yield ("(0,0)", 1)
        else :
            if ax :
                yield (v_map [sx,  0], ax)
            if ay :
                yield (v_map [ 0, sy], ay)
    # end def _directions

    def _formatted (self) :
        _fd = self._formatted_dir
        return " + ".join (_fd (* d) for d in self._directions ())
    # end def _formatted

    def _formatted_dir (self, d, f) :
        return ("%s*%s" % (d, f)) if f != 1 else d
    # end def _formatted_dir

    def __str__ (self) :
        return self._formatted ()
    # end def __str__

# end class _Cardinal_Direction_

class Cardinal_Direction (_Cardinal_Direction_, D2.Point) :
    """Cardinal direction in rectangular, 2D space.

    >>> for d in (N, E, S, W) :
    ...     print (d, tuple (d), repr (d))
    N (0, 1) Cardinal_Direction (0, 1)
    E (1, 0) Cardinal_Direction (1, 0)
    S (0, -1) Cardinal_Direction (0, -1)
    W (-1, 0) Cardinal_Direction (-1, 0)

    >>> print (E + N)
    NE

    >>> print (2*N + 2*E)
    NE*2

    >>> print (S + 5*W)
    W*5 + S

    >>> p = E*2 + N*5
    >>> q = R_Point_P (p, E*3 + N)
    >>> print ("p =", p)
    p = E*2 + N*5
    >>> print ("q =", q)
    q = E*5 + N*6

    >>> print (p.as_name ())
    E2_N5

    >>> print ("p =", p.scale (Point (2, 0.5)))
    p = E*4 + N*2.5
    >>> print ("q =", q)
    q = E*7 + N*3.5

    >>> print ("q =", q.scale (Point (3, 2)))
    q = E*21 + N*7.0

    >>> import _TFL._D2.Line
    >>> l = D2.Line   (Point (0, 0), Point (20, 10))
    >>> q = R_Point_L (l, 0.5, NE * 2)
    >>> r = -q
    >>> print ("l =", l)
    l = ((0,0), E*20 + N*10)
    >>> print ("q =", q)
    q = E*12.0 + N*7.0
    >>> print ("r =", r)
    r = W*12.0 + S*7.0

    >>> l.shift (Point (5, 5))
    Line (NE*5, E*25 + N*15)

    >>> print ("l =", l)
    l = (NE*5, E*25 + N*15)
    >>> print ("q =", q)
    q = E*17.0 + N*12.0
    >>> print ("r =", r)
    r = W*17.0 + S*12.0

    >>> print (Point.from_name ("W2_S1"))
    W*2 + S
    >>> print (Point.from_name ("S1_E3"))
    E*3 + S
    >>> print (Point.from_name ("E3_S3"))
    SE*3
    >>> print (Point.from_name ("NE3_E1"))
    E*4 + N*3

    >>> for n in sorted (Point.name_map) :
    ...     p = Point.from_name (n)
    ...     print ("positive:", p, ", negative:", -p)
    positive: E , negative: W
    positive: N , negative: S
    positive: NE , negative: SW
    positive: NW , negative: SE
    positive: S , negative: N
    positive: SE , negative: NW
    positive: SW , negative: NE
    positive: W , negative: E

    """

    _name_pattern  = Regexp \
        ( r"^"
        + r"(?P<dir> "
        + "|".join (sorted (_Cardinal_Direction_.name_map, reverse = True))
        + r")"
        + r"(?P<f> \d*)"
        + r"$"
        , re.VERBOSE | re.IGNORECASE
        )

    @classmethod
    def from_name (cls, v) :
        def _gen (v, pat, map) :
            for p in v.split ("_") :
                if pat.match (p) :
                    d = map [pat.dir]
                    f = int (pat.f or 1)
                    if f != 1:
                        d = tuple (c*f for c in d)
                    yield d
                else :
                    raise ValueError ("Invalid direction name %s" % (p, ))
        ps = tuple (_gen (v, cls._name_pattern, cls.name_map))
        if ps :
            return sum ((cls (* p) for p in ps), cls ())
        else :
            raise ValueError ("Invalid direction name %s" % (v, ))
    # end def from_name

    def as_name (self) :
        return "_".join \
            (("%s%s" % (d, f) if f != 1 else d) for d, f in self._directions ())
    # end def as_name

Point = Cardinal_Direction # end class

class _CD_R_Point_ (_Cardinal_Direction_, D2._R_Point_) :
    """Base class for cardinal direction Points positioned relative to
       another point.
    """

    Point = Cardinal_Direction

# end class _CD_R_Point_

def _derived (base) :
    real_name = base.__name__
    name      = "CD_" + real_name
    return base.__class__ \
        ( name, (_CD_R_Point_, base)
        , dict (_real_name = real_name)
        )
# end def _derived

R_Point_P  = Pp = _derived (D2.R_Point_P)
R_Point_L  = Pl = _derived (D2.R_Point_L)
R_Point_R  = Pr = _derived (D2.R_Point_R)
R_Point_nP = Pn = _derived (D2.R_Point_nP)

### cardinal directions
N  = North      = Cardinal_Direction ( 0, +1)
E  = East       = Cardinal_Direction (+1,  0)
S  = South      = Cardinal_Direction ( 0, -1)
W  = West       = Cardinal_Direction (-1,  0)

### ordinal directions
NE = North_East = Cardinal_Direction (+1, +1)
SE = South_East = Cardinal_Direction (+1, -1)
SW = South_West = Cardinal_Direction (-1, -1)
NW = North_West = Cardinal_Direction (-1, +1)

if __name__ != "__main__" :
    TFL.D2._Export_Module ()
    TFL.D2.CD = TFL.D2.Cardinal_Direction
### __END__ TFL.D2.Cardinal_Direction
