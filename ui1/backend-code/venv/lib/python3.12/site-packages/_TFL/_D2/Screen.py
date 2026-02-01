# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Christian Tanzer All rights reserved
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
#    TFL.D2.Screen
#
# Purpose
#    2D as used on screens ([0, 0] is top-left corner of screen, coordinates
#    grow to the right and down directions)
#
# Revision Dates
#    20-Aug-2012 (CT) Creation (factored from TFL.D2.Rect)
#    26-Aug-2012 (CT) Redefine `side_dict`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL            import TFL

from    _TFL._D2       import D2
import  _TFL._D2.Rect

class _Screen_Rect_ (D2.Rect) :
    """Model an axes-parallel rectangle in 2D screen coordinates.

    >>> def rect_points (r) :
    ...     for p in sorted (r.corner_dict.keys ()) :
    ...         print ("%-20s : %s" % (p, getattr (r, p)))
    >>> def rect_sides (r) :
    ...     for s in sorted (r.side_dict.keys ()) :
    ...         print ("%-20s : %s" % (s, getattr (r, s)))
    >>> def connection_points (r) :
    ...     P = D2.Point
    ...     for p, off in sorted (
    ...               [ (r.top_left,     P ( 0.0, -0.5))
    ...               , (r.top_left,     P (-0.5,  0.0))
    ...               , (r.top_right,    P ( 0.0, -0.5))
    ...               , (r.top_right,    P ( 0.5,  0.0))
    ...               , (r.bottom_left,  P ( 0.0,  0.5))
    ...               , (r.bottom_left,  P (-0.5,  0.0))
    ...               , (r.bottom_right, P ( 0.0,  0.5))
    ...               , (r.bottom_right, P ( 0.5,  0.0))
    ...               ]
    ...             , key = lambda x : tuple (x [0] + x [1])
    ...             ) :
    ...         q = p + off
    ...         print ("%s : %s" % (q, r.connection_point (q, r.center)))
    >>> q = Rect (D2.Point (1.0, 1.0), D2.Point (2.0, 1.0))
    >>> rect_points (q)
    bottom_left          : (1.0, 2.0)
    bottom_right         : (3.0, 2.0)
    center               : (2.0, 1.5)
    center_bottom        : (2.0, 2.0)
    center_left          : (1.0, 1.5)
    center_right         : (3.0, 1.5)
    center_top           : (2.0, 1.0)
    top_left             : (1.0, 1.0)
    top_right            : (3.0, 1.0)
    >>> q.scale (2)
    Rect ((1.0, 1.0), (4.0, 2.0))
    >>> rect_points (q)
    bottom_left          : (1.0, 3.0)
    bottom_right         : (5.0, 3.0)
    center               : (3.0, 2.0)
    center_bottom        : (3.0, 3.0)
    center_left          : (1.0, 2.0)
    center_right         : (5.0, 2.0)
    center_top           : (3.0, 1.0)
    top_left             : (1.0, 1.0)
    top_right            : (5.0, 1.0)
    >>> q.shift (D2.Point (1, 1))
    Rect ((2.0, 2.0), (4.0, 2.0))
    >>> rect_points (q)
    bottom_left          : (2.0, 4.0)
    bottom_right         : (6.0, 4.0)
    center               : (4.0, 3.0)
    center_bottom        : (4.0, 4.0)
    center_left          : (2.0, 3.0)
    center_right         : (6.0, 3.0)
    center_top           : (4.0, 2.0)
    top_left             : (2.0, 2.0)
    top_right            : (6.0, 2.0)
    >>> rect_sides (q)
    bottom               : ((2.0, 4.0), (6.0, 4.0))
    left                 : ((2.0, 2.0), (2.0, 4.0))
    right                : ((6.0, 2.0), (6.0, 4.0))
    top                  : ((2.0, 2.0), (6.0, 2.0))
    >>> q = Rect (D2.Point (1.0, 1.0), D2.Point (1.0, 1.0))
    >>> connection_points (q)
    (0.5, 1.0) : (1.0, 1.25)
    (0.5, 2.0) : (1.0, 1.75)
    (1.0, 0.5) : (1.25, 1.0)
    (1.0, 2.5) : (1.25, 2.0)
    (2.0, 0.5) : (1.75, 1.0)
    (2.0, 2.5) : (1.75, 2.0)
    (2.5, 1.0) : (2.0, 1.25)
    (2.5, 2.0) : (2.0, 1.75)

    """

    _real_name    = "Rect"

    Bottom_Left   = D2.Point (0.0, 1.0)
    Bottom_Right  = D2.Point (1.0, 1.0)
    Center        = D2.Point (0.5, 0.5)
    Center_Bottom = D2.Point (0.5, 1.0)
    Center_Left   = D2.Point (0.0, 0.5)
    Center_Right  = D2.Point (1.0, 0.5)
    Center_Top    = D2.Point (0.5, 0.0)
    Top_Left      = D2.Point (0.0, 0.0)
    Top_Right     = D2.Point (1.0, 0.0)

    side_dict = \
        { "bottom" : (lambda r : D2.Line (r.bottom_left,  r.bottom_right))
        , "left"   : (lambda r : D2.Line (r.top_left,     r.bottom_left))
        , "right"  : (lambda r : D2.Line (r.top_right,    r.bottom_right))
        , "top"    : (lambda r : D2.Line (r.top_left,     r.top_right))
        }

    @property
    def ref_point (self) :
        return self.top_left
    # end def ref_point

    @ref_point.setter
    def ref_point (self, value) :
        self.top_left = value
    # end def ref_point

Rect = _Screen_Rect_ # end class

if __name__ != "__main__" :
    TFL.D2._Export_Module ()
### __END__ TFL.D2.Screen
