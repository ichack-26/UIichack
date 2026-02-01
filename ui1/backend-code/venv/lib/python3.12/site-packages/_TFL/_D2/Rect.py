# -*- coding: utf-8 -*-
# Copyright (C) 2002-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.D2.Rect
#
# Purpose
#    Classes modeling rectangles in 2D space
#
# Revision Dates
#    24-Jun-2002 (CT) Creation
#     9-Apr-2003 (MG) `point_in_rect` added
#    11-Jun-2003 (CT) s/!= None/is not None/
#    28-Sep-2004 (CT) Use `isinstance` instead of type comparison
#     4-Jun-2005 (CT) `str` added to show `size` instead of `bottom_right`
#    17-Jun-2011 (CT) `Sides` added
#    20-Aug-2012 (CT) Add `M_Rect` to set `corner_dict`
#    20-Aug-2012 (CT) Change to use real cartesian coordinates, not screen
#                     coordinates
#    20-Aug-2012 (CT) Add `transformed`
#    20-Aug-2012 (CT) Sort methods alphabetically
#    21-Aug-2012 (CT) Add `corners`
#    26-Aug-2012 (CT) Change `side_dict` to get nice sides
#    23-May-2013 (CT) Use `TFL.Meta.BaM` for Python-3 compatibility
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from    _TFL           import TFL

from    _TFL._D2       import D2
import  _TFL._D2.Point
import  _TFL._D2.Line

import  _TFL._Meta.Object

import  math

class M_Rect (TFL.Meta.Object.__class__) :
    """Meta class for `Rect`"""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        cls.corner_dict = \
            { "bottom_left"   : cls.Bottom_Left
            , "bottom_right"  : cls.Bottom_Right
            , "center"        : cls.Center
            , "center_bottom" : cls.Center_Bottom
            , "center_left"   : cls.Center_Left
            , "center_right"  : cls.Center_Right
            , "center_top"    : cls.Center_Top
            , "top_left"      : cls.Top_Left
            , "top_right"     : cls.Top_Right
            }
    # end def __init__

# end class M_Rect

class Rect (TFL.Meta.Object, metaclass = M_Rect) :
    """Model an axes-parallel rectangle in 2D space.

    >>> def rect_points (r) :
    ...     for p in sorted (r.corner_dict.keys ()) :
    ...         print ("%-20s : %s" % (p, getattr (r, p)))
    >>> def rect_sides (r) :
    ...     for s in sorted (r.side_dict.keys ()) :
    ...         print ("%-20s : %s" % (s, getattr (r, s)))
    >>> def connection_points (r) :
    ...     P = D2.Point
    ...     for p, off in sorted (
    ...               [ (r.top_left,     P ( 0.0, +0.5))
    ...               , (r.top_left,     P (-0.5,  0.0))
    ...               , (r.top_right,    P ( 0.0, +0.5))
    ...               , (r.top_right,    P ( 0.5,  0.0))
    ...               , (r.bottom_left,  P ( 0.0, -0.5))
    ...               , (r.bottom_left,  P (-0.5,  0.0))
    ...               , (r.bottom_right, P ( 0.0, -0.5))
    ...               , (r.bottom_right, P ( 0.5,  0.0))
    ...               ]
    ...             , key = lambda x : tuple (x [0] + x [1])
    ...             ) :
    ...         q = p + off
    ...         print ("%s : %s" % (q, r.connection_point (q, r.center)))
    >>> q = Rect (D2.Point (1.0, 1.0), D2.Point (2.0, 1.0))
    >>> rect_points (q)
    bottom_left          : (1.0, 1.0)
    bottom_right         : (3.0, 1.0)
    center               : (2.0, 1.5)
    center_bottom        : (2.0, 1.0)
    center_left          : (1.0, 1.5)
    center_right         : (3.0, 1.5)
    center_top           : (2.0, 2.0)
    top_left             : (1.0, 2.0)
    top_right            : (3.0, 2.0)

    >>> q.scale (2)
    Rect ((1.0, 1.0), (4.0, 2.0))
    >>> rect_points (q)
    bottom_left          : (1.0, 1.0)
    bottom_right         : (5.0, 1.0)
    center               : (3.0, 2.0)
    center_bottom        : (3.0, 1.0)
    center_left          : (1.0, 2.0)
    center_right         : (5.0, 2.0)
    center_top           : (3.0, 3.0)
    top_left             : (1.0, 3.0)
    top_right            : (5.0, 3.0)

    >>> q.shift (D2.Point (1, 1))
    Rect ((2.0, 2.0), (4.0, 2.0))
    >>> rect_points (q)
    bottom_left          : (2.0, 2.0)
    bottom_right         : (6.0, 2.0)
    center               : (4.0, 3.0)
    center_bottom        : (4.0, 2.0)
    center_left          : (2.0, 3.0)
    center_right         : (6.0, 3.0)
    center_top           : (4.0, 4.0)
    top_left             : (2.0, 4.0)
    top_right            : (6.0, 4.0)

    >>> rect_sides (q)
    bottom               : ((2.0, 2.0), (6.0, 2.0))
    left                 : ((2.0, 2.0), (2.0, 4.0))
    right                : ((6.0, 2.0), (6.0, 4.0))
    top                  : ((2.0, 4.0), (6.0, 4.0))

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

    Bottom_Left   = D2.Point (0.0, 0.0)
    Bottom_Right  = D2.Point (1.0, 0.0)
    Center        = D2.Point (0.5, 0.5)
    Center_Bottom = D2.Point (0.5, 0.0)
    Center_Left   = D2.Point (0.0, 0.5)
    Center_Right  = D2.Point (1.0, 0.5)
    Center_Top    = D2.Point (0.5, 1.0)
    Top_Left      = D2.Point (0.0, 1.0)
    Top_Right     = D2.Point (1.0, 1.0)

    side_dict = \
        { "bottom" : (lambda r : D2.Line (r.bottom_left,  r.bottom_right))
        , "left"   : (lambda r : D2.Line (r.bottom_left,  r.top_left))
        , "right"  : (lambda r : D2.Line (r.bottom_right, r.top_right))
        , "top"    : (lambda r : D2.Line (r.top_left,     r.top_right))
        }

    @property
    def corners (self) :
        return \
            self.bottom_left, self. bottom_right, self.top_left, self.top_right
    # end def sides

    @property
    def ref_point (self) :
        return self.bottom_left
    # end def ref_point

    @ref_point.setter
    def ref_point (self, value) :
        self.bottom_left = value
    # end def ref_point

    def __init__ (self, pos = (0.0, 0.0), size = (1.0, 1.0)) :
        if isinstance (pos, (list, tuple)) :
            pos  = D2.Point (* pos)
        if isinstance (size, (list, tuple)) :
            size = D2.Point (* size)
        self.ref_point = pos
        self.size      = size
    # end def __init__

    @classmethod
    def Sides (cls, diagonal, ratio) :
        """Return the sides `(a, b)` of a rectangle with `diagonal` and `ratio`
           between the sides.
        """
        b = math.sqrt (diagonal * diagonal / (1 + ratio * ratio))
        a = b * ratio
        return a, b
    # end def Sides

    def connection_point (self, point_1, point_2) :
        """Returns the intersection point between the rectangle and the line
           between `point_1` and `point_2`. If no intersection exists
           (both points are either inside or outside) than
           None is returned.
        """
        line = D2.Line (point_1, point_2)
        for side in (self.bottom, self.left, self.right, self.top) :
            cp = side.intersection (line)
            if cp is not None :
                return cp
        return None
    # end def connection_point

    def point (self, p = Center) :
        """Return point at position `p` relative to the rectangle."""
        return self.ref_point + (self.size * p)
    # end def point

    def point_in_rect (self, point) :
        if isinstance (point, (list, tuple)) :
            point = D2.Point (* point)
        tl = self.top_left
        br = tl + self.size
        if (  (point.x < tl.x) or (point.x > br.x)
           or (point.y < tl.y) or (point.y > br.y)
           ) :
            return None
        return 1
    # end def point_in_rect

    def scale (self, right) :
        self.size.scale (right)
        return self
    # end def scale

    def shift (self, right) :
        self.ref_point.shift (right)
        return self
    # end def shift

    def transformed (self, affine) :
        """Return another rectangle whose coordinates are derived via `affine`
           transform from `self`.
        """
        return self.__class__ \
            (self.ref_point.transform (affine), self.size.transformed (affine))
    # end def transformed

    def __getattr__ (self, name) :
        """Return the point or side `name`. The possible names are defined by
           `corner_dict` and `side_dict`.
        """
        if   name in self.corner_dict :
            return self.point (self.corner_dict [name])
        elif name in self.side_dict :
            return self.side_dict [name] (self)
        else :
            raise  AttributeError (name)
    # end def __getattr__

    def __repr__ (self) :
        return "%s %s" % (self.__class__.__name__, str (self))
    # end def __repr__

    def __str__ (self) :
        return "(%s, %s)" % (self.ref_point, self.size)
    # end def __str__

# end class Rect

def rectangle (x, y, w, h) :
    """Return a `Rect` at position `(x, y)` with size `(w, h)`"""
    return Rect (D2.Point (x, y), D2.Point (w, h))
# end def rectangle

if __name__ != "__main__" :
    D2._Export ("*")
### __END__ Rect
