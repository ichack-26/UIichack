# -*- coding: utf-8 -*-
# Copyright (C) 2010-2024 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Color
#
# Purpose
#    Model colors in RGB or HSL representation
#
# Revision Dates
#    26-Dec-2010 (CT) Creation
#    27-Dec-2010 (CT) Creation continued
#    29-Dec-2010 (CT) Creation finished
#     2-Jan-2011 (CT) `__add__` and `__radd__` added
#    17-Jan-2012 (CT) Change `HSL` to be compatible with CSS
#    18-Jan-2012 (CT) Add `_Color_.__eq__` and `__hash__`
#    18-Jan-2012 (CT) Return `name`, not `"name"`, from `SVG_Color.formatted`
#    16-Apr-2012 (CT) Add `sorted` to `.iteritems`
#    31-Aug-2012 (CT) Add property `Color.no_alpha`
#    23-May-2013 (CT) Use `TFL.Meta.BaM` for Python-3 compatibility
#    11-Feb-2015 (CT) Add `Color.with_alpha`
#    14-Jun-2015 (CT) Add `HUSL`; change signature and internals of `Value`
#     6-Oct-2015 (CT) Adapt `hex`, `hex_CSS` to Python 3.5
#                     ("%X" requires `int`, blows up for `float`)
#    16-Oct-2015 (CT) Add `__future__` imports
#    19-Feb-2017 (CT) Add `relative_luminance`, `contrast_ratio`
#     4-Apr-2017 (CT) Add `__repr__` to `_Color_`
#                     + Add `reprified` to `_Color_`, `SVG_Color`
#     8-Nov-2022 (CT) Add support for hexadecimal `alpha` to `RGB_X`
#                     + Factor `hex_tuple`, `CSS_hex_tuple`
#    15-Mar-2024 (CT) Factor `_Base_Color_` and `_Value_`
#                     + Factor `_normalized_hue`
#                     + Factor `_RGB_` (redefine `as_RGB` only for `RGB` itself)
#    18-Mar-2024 (CT) Move `_formatted_values` from `RGB`to `_RGB_`
#    22-Mar-2024 (CT) Redefine `_Ok_Color_.copy`, add `_Ok_Color_.set`
#    ««revision-date»»···
#--

from   _TFL                     import TFL
from   _TFL.pyk                 import pyk

from   _TFL._D2.Transform       import MT as Mx
from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.portable_repr       import portable_repr
from   _TFL.predicate           import identity

import _TFL._Meta.Object
import _TFL._Meta.Property
import _TFL.Regexp

from   collections              import namedtuple

import math

### math provides `cbrt` only for Python 3.11+
try :
    cbrt = math.cbrt
except AttributeError :
    def cbrt (x) :
        return x ** (1/3)

RGB_Value       = namedtuple ("RGB", ("red", "green", "blue"))
HSL_Value       = namedtuple ("HSL", ("hue", "saturation", "lightness"))
Value_Types     = HSL_Value, RGB_Value

try :
    import husl
except ImportError :
    HUSL_Value  = husl = None
else :
    HUSL_Value  = namedtuple ("HUSL", ("hue", "saturation", "lightness"))
    Value_Types = (HUSL_Value, ) + Value_Types

for _T in Value_Types :
    _T.name = _T.__name__.lower ()


OKLab_Value     = namedtuple ("OKLab", ("L", "a", "b"))
OKLCh_Value     = namedtuple ("OKLCh", ("L", "C", "H"))

Ok_Value_Types  = OKLCh_Value, OKLab_Value

for _T in Ok_Value_Types :
    _T.name = _T.__name__.lower ()

class _Value_ (TFL.Meta.Object) :
    """Base class for immutable color values."""

    Types           = () ### needs to be defined by subclasses

    def __init__ (self, v) :
        if not isinstance (v, self.Types) :
            raise TypeError \
                ( "Need one of %s, got %s %s instead"
                % (self.Types, type (v), v)
                )
        super ().__init__ ()
        self._vmap = {v.name : v}
    # end def __init__

    @property
    def preferred_value (self) :
        _vmap = self._vmap
        for T in self.Types :
            try :
                return _vmap [T.name]
            except KeyError :
                pass
    # end def preferred_value

    def __eq__ (self, rhs) :
        pv = self.preferred_value
        return pv == getattr (rhs, pv.name, None)
    # end def __eq__

    def __hash__ (self) :
        return hash (self.preferred_value)
    # end def __hash__

    def __repr__ (self) :
        v  = self.preferred_value
        vs = ", ".join ("%g" % (s, ) for s in v)
        return "%s (%s = (%s))" % (self.__class__.__name__, v.name, vs)
    # end def __repr__

# end class _Value_

class Ok_Value (_Value_) :
    """Model an immutable color value of an Ok color space.

    >>> srgb_red = Ok_Value.from_oklch (0.63, 0.26, 29.23)
    >>> srgb_red
    Ok_Value (oklch = (0.63, 0.26, 29.23))
    >>> print (portable_repr (srgb_red._vmap))
    {'oklch' : (0.63, 0.26, 29.23)}
    >>> srgb_red.oklab
    OKLab(L=0.63, a=0.22689329387478613, b=0.12696232982522787)
    >>> print (portable_repr (srgb_red._vmap))
    {'oklab' : (0.63, 0.226893293875, 0.126962329825), 'oklch' : (0.63, 0.26, 29.23)}

    >>> srgb_green = Ok_Value.from_oklch (0.87, 0.29, 142.5)
    >>> srgb_green.oklch
    OKLCh(L=0.87, C=0.29, H=142.5)
    >>> srgb_green.oklab
    OKLab(L=0.87, a=-0.23007246868445816, b=0.17654081441252903)

    >>> srgb_blue = Ok_Value.from_oklch (0.45, 0.31, 264.05)
    >>> srgb_blue.oklch
    OKLCh(L=0.45, C=0.31, H=264.05)
    >>> srgb_blue.oklab
    OKLab(L=0.45, a=-0.032134767244521106, b=-0.30832994783857837)

    """

    Types = Ok_Value_Types

    @classmethod
    def from_lab (cls, vs) :
        L, a, b = vs
        L = cls._normalized_L (L)
        v = OKLab_Value (L, a, b)
        assert  0.0 <= v.L <= 1.0, str (vs)
        assert -0.4 <= v.a <= 0.4, str (vs)
        assert -0.4 <= v.b <= 0.4, str (vs)
        return cls (v)
    # end def from_oklab

    @classmethod
    def from_oklch (cls, * vs) :
        L, C, H = vs
        L = cls._normalized_L (L)
        C = max (C, 0.0)
        H = OKLCh._normalized_hue (H)
        v = OKLCh_Value (L, C, H)
        return cls (v)
    # end def from_oklch

    @classmethod
    def _normalized_L (cls, L) :
        result  = min (max (L, 0.0), 1.0)
        return result
    # end def _normalized_L

    @Once_Property
    def oklab (self) :
        _vmap   = self._vmap
        result  = _vmap.get ("oklab")
        if result is None :
            L, C, H = self.oklch
            H_rad   = math.radians (H)
            a       = C * math.cos (H_rad)
            b       = C * math.sin (H_rad)
            result  = _vmap ["oklab"] = OKLab_Value (L, a, b)
        return result
    # end def oklab

    @Once_Property
    def oklch (self) :
        _vmap   = self._vmap
        result  = _vmap.get ("oklch")
        if result is None :
            L, a, b = self.oklab
            C       = math.sqrt    (a*a + b*b)
            H       = math.degrees (math.atan2 (b, a))
            H       = OKLCh._normalized_hue (H)
            result  = _vmap ["oklch"] = OKLCh_Value (L, C, H)
        return result
    # end def oklch

# end class Ok_Value

class Value (_Value_) :
    """Model an immutable color value.

    >>> white_1 = Value.from_rgb ((1.0, 1.0, 1.0))
    >>> white_1.rgb, white_1.hsl
    (RGB(red=1.0, green=1.0, blue=1.0), HSL(hue=0.0, saturation=0.0, lightness=1.0))

    >>> white_2 = Value.from_hsl ((0.0, 0.0, 1.0))
    >>> white_2.rgb, white_2.hsl
    (RGB(red=1.0, green=1.0, blue=1.0), HSL(hue=0.0, saturation=0.0, lightness=1.0))

    >>> white_1 == white_2
    True

    >>> grey50 = Value.from_rgb ((0.5, 0.5, 0.5))
    >>> grey50.rgb, grey50.hsl
    (RGB(red=0.5, green=0.5, blue=0.5), HSL(hue=0.0, saturation=0.0, lightness=0.5))

    >>> black = Value.from_rgb ((0.0, 0.0, 0.0))
    >>> black.rgb, black.hsl
    (RGB(red=0.0, green=0.0, blue=0.0), HSL(hue=0.0, saturation=0.0, lightness=0.0))

    >>> red = Value.from_hsl ((0.0, 1.0, 0.5))
    >>> red.rgb, red.hsl
    (RGB(red=1.0, green=0.0, blue=0.0), HSL(hue=0.0, saturation=1.0, lightness=0.5))

    >>> Value.from_rgb ((0.750, 0.750, 0.000)) == Value.from_hsl (( 60.0, 1.000, 0.375))
    True
    >>> Value.from_rgb ((0.000, 0.500, 0.000)) == Value.from_hsl ((120.0, 1.000, 0.250))
    True
    >>> Value.from_rgb ((0.500, 1.000, 1.000)) == Value.from_hsl ((180.0, 1.000, 0.750))
    True
    >>> Value.from_rgb ((0.500, 0.500, 1.000)) == Value.from_hsl ((240.0, 1.000, 0.750))
    True
    >>> Value.from_rgb ((0.750, 0.250, 0.750)) == Value.from_hsl ((300.0, 0.500, 0.500))
    True

    >>> for i in range (12) :
    ...     h = i * 30
    ...     v = Value.from_husl ((h, 0.9, 0.6))
    ...     print (i, v, v.hex)
    0 Value (husl = (0, 0.9, 0.6)) #F65682
    1 Value (husl = (30, 0.9, 0.6)) #DD742B
    2 Value (husl = (60, 0.9, 0.6)) #B18B2B
    3 Value (husl = (90, 0.9, 0.6)) #90962B
    4 Value (husl = (120, 0.9, 0.6)) #55A22A
    5 Value (husl = (150, 0.9, 0.6)) #2CA375
    6 Value (husl = (180, 0.9, 0.6)) #2EA095
    7 Value (husl = (210, 0.9, 0.6)) #309DAE
    8 Value (husl = (240, 0.9, 0.6)) #3398D5
    9 Value (husl = (270, 0.9, 0.6)) #9180F3
    10 Value (husl = (300, 0.9, 0.6)) #DE51F3
    11 Value (husl = (330, 0.9, 0.6)) #F549C1

    """

    Types = Value_Types

    @classmethod
    def from_hsl (cls, vs) :
        assert vs
        v = HSL_Value (* vs)
        assert 0.0 <= v.hue        <  360.0, str (vs)
        assert 0.0 <= v.saturation <=   1.0, str (vs)
        assert 0.0 <= v.lightness  <=   1.0, str (vs)
        return cls (v)
    # end def from_hsl

    @classmethod
    def from_husl (cls, vs) :
        assert vs
        v = cls.HUSL_Value (* vs)
        assert 0.0 <= v.hue        <  360.0, str (vs)
        assert 0.0 <= v.saturation <=   1.0, str (vs)
        assert 0.0 <= v.lightness  <=   1.0, str (vs)
        return cls (v)
    # end def from_husl

    if HUSL_Value is None :
        @TFL.Meta.Class_Property
        def HUSL_Value (cls) :
            raise ImportError \
                ("Module `husl` no installed; try: `pip install husl`")
        # end def HUSL_Value
    else :
        @TFL.Meta.Class_Property
        def HUSL_Value (cls) :
            return HUSL_Value
        # end def HUSL_Value

    @classmethod
    def from_rgb (cls, vs) :
        assert vs
        v = RGB_Value (* vs)
        assert all (0.0 <= x <= 1.0 for x in v), str (vs)
        return cls (v)
    # end def from_rgb

    @Once_Property
    def hex (self) :
        r, g, b = self.hex_tuple
        return "#%s%s%s" % (r, g, b)
    # end def hex

    @Once_Property
    def hex_CSS (self) :
        r, g, b = self.CSS_hex_tuple (* self.hex_tuple)
        return "#%s%s%s" % (r, g, b)
    # end def hex

    @Once_Property
    def hex_tuple (self) :
        return tuple ("%2.2X" % (int (x*255), ) for x in self.rgb)
    # end def hex_tuple

    @Once_Property
    def hsl (self) :
        _vmap  = self._vmap
        result = _vmap.get ("hsl")
        if result is None :
            r, g, b = rgb = self.rgb
            M  = max (rgb)
            m  = min (rgb)
            c  = M - m
            if c == 0 :
                h6 = 0
            elif M == r :
                h6 = ((g - b) / c) % 6
            elif M == g :
                h6 = ((b - r) / c) + 2
            elif M == b :
                h6 = ((r - g) / c) + 4
            else :
                raise RuntimeError ("Program should never arrive here")
            h  = h6 * 60.0
            l  = (M + m) / 2.0
            s  = c / (1.0 - abs (2.0 * l - 1.0)) if (c != 0) else 0.0
            result = _vmap ["hsl"] = HSL_Value (h, s, l)
        return result
    # end def hsl

    @Once_Property
    def husl (self) :
        HUSL_Value  = self.HUSL_Value
        _vmap       = self._vmap
        result      = _vmap.get ("husl")
        if result is None :
            h, s, l = husl.rgb_to_husl (* self.rgb)
            result  = _vmap ["husl"] = HUSL_Value (h, s / 100., l / 100.)
        return result
    # end def husl

    @Once_Property
    def rgb (self) :
        _vmap  = self._vmap
        result = _vmap.get ("rgb")
        if result is None :
            v = self.preferred_value
            if husl is not None and isinstance (v, HUSL_Value) :
                h, s, l = v
                result  = RGB_Value \
                    (* husl.husl_to_rgb (float (h), s * 100., l * 100.))
            elif isinstance (v, HSL_Value) :
                h, s, l   = _vmap ["hsl"]
                c  = (1.0 - abs (2.0 * l - 1.0)) * s
                h6 = h / 60.0
                x  = c * (1 - abs (h6 % 2 - 1))
                m  = l - 0.5 * c
                if h6 < 1 :
                    r, g, b = c, x, 0
                elif h6 < 2 :
                    r, g, b = x, c, 0
                elif h6 < 3 :
                    r, g, b = 0, c, x
                elif h6 < 4 :
                    r, g, b = 0, x, c
                elif h6 < 5 :
                    r, g, b = x, 0, c
                elif h6 < 6 :
                    r, g, b = c, 0, x
                else :
                    raise ValueError ("Invalid hue: %s" % h)
                result = RGB_Value (r + m, g + m, b + m)
            _vmap ["rgb"] = result
        return result
    # end def rgb

    def CSS_hex_tuple (self, * values) :
        result = values
        if all (x [0] == x [1] for x in values) :
            result = tuple (x [0] for x in values)
        return result
    # end def CSS_hex_tuple

# end class Value

class M_Color (TFL.Meta.Object.__class__) :
    """Meta class for `_Color_`."""

# end class M_Color

class _Base_Color_ (TFL.Meta.Object, metaclass = M_Color) :
    """Base class modelling a mutable color."""

    alpha         = None
    formatter     = None

    def __init__ (self, values, alpha = None) :
        Value = self.Value
        if not isinstance (values, Value) :
            values = Value (self.P_Type (* (float (v) for v in values)))
        self.value = values
        if alpha is not None :
            assert 0.0 <= alpha <= 1.0
            self.alpha = float (alpha)
    # end def __init__

    @classmethod
    def cast (cls, v, alpha = None) :
        result = cls.__new__ (cls)
        result.value = v.value
        if alpha is None :
            alpha = v.alpha
        if alpha is not None :
            result.alpha = alpha
        return result
    # end def cast

    @classmethod
    def from_value (cls, value, alpha = None) :
        result = cls.__new__ (cls)
        result.value = value
        if alpha is not None :
            result.alpha = alpha
        return result
    # end def from_value

    @classmethod
    def _normalized_hue (cls, hue) :
        result  = hue % 360.0
        if result < 0.0 :
            result += 360.0
        return result
    # end def _normalized_hue

    @property
    def no_alpha (self) :
        """Return a color instance without `alpha`."""
        return self if self.alpha is None else self.from_value (self.value)
    # end def no_alpha

    def copy (self, ** kwds) :
        """Return a copy with values changed by `kwds`"""
        result = self.from_value (self.value, self.alpha)
        for k, v in kwds.items () :
            setattr (result, k, v)
        return result
    # end def copy

    def formatted (self) :
        v = self._formatted_values ()
        if self.alpha is not None :
            return "%sa(%s, %s)" % (self.name, v, self.alpha)
        else :
            return "%s(%s)" % (self.name, v)
    # end def formatted

    def reprified (self) :
        v = self._formatted_values ()
        if v.startswith ("#") :
            v = portable_repr (v)
        else :
            v = v.replace ("%", "")
        alpha = self.alpha
        args  = (v, ) if alpha is None else (v, portable_repr (alpha))
        return "%s (%s)" % (self.__class__.__name__, ", ".join (args))
    # end def reprified

    def with_alpha (self, alpha) :
        return self.cast (self, alpha)
    # end def with_alpha

    def __add__ (self, rhs) :
        return str (self) + rhs
    # end def __add__

    def __radd__ (self, rhs) :
        return rhs + str (self)
    # end def __radd__

    def __repr__ (self) :
        if self.formatter is not None :
            self = self.formatter.cast (self)
        return self.reprified ()
    # end def __repr__

    def __str__ (self) :
        if self.formatter is not None :
            self = self.formatter.cast (self)
        return self.formatted ()
    # end def __str__

# end class _Base_Color_

class _Color_ (_Base_Color_) :
    """Base class modelling a mutable color."""

    Value       = Value

    @property
    def as_HSL (self) :
        return HSL.cast (self)
    # end def as_HSL

    @property
    def as_HUSL (self) :
        return HUSL.cast (self)
    # end def as_HUSL

    @property
    def as_RGB (self) :
        return RGB.cast (self)
    # end def as_RGB

    @property
    def as_RGB_8 (self) :
        return RGB_8.cast (self)
    # end def as_RGB_8

    @property
    def as_RGB_P (self) :
        return RGB_P.cast (self)
    # end def as_RGB_P

    @property
    def as_RGB_X (self) :
        return RGB_X.cast (self)
    # end def as_RGB_X

    @property
    def blue (self) :
        return self.value.rgb.blue
    # end def blue

    @blue.setter
    def blue (self, value) :
        assert 0.0 <= value <= 1.0
        r, g, b = self.value.rgb
        self.value = self.Value.from_rgb ((r, g, float (value)))
    # end def blue

    @property
    def green (self) :
        return self.value.rgb.green
    # end def green

    @green.setter
    def green (self, value) :
        assert 0.0 <= value <= 1.0
        r, g, b = self.value.rgb
        self.value = self.Value.from_rgb ((r, float (value), b))
    # end def green

    @property
    def hsl (self) :
        return self.value.hsl
    # end def hsl

    @hsl.setter
    def hsl (self, value) :
        if not isinstance (value, self.Value) :
            value  = self.Value.from_hsl (value)
        self.value = value
    # end def hsl

    @property
    def hue (self) :
        return self.value.hsl.hue
    # end def hue

    @hue.setter
    def hue (self, value) :
        value   = self._normalized_hue (value)
        h, s, l = self.value.hsl
        self.value = self.Value.from_hsl ((float (value), s, l))
    # end def hue

    @property
    def husl (self) :
        return self.value.husl
    # end def husl

    @hsl.setter
    def husl (self, value) :
        if not isinstance (value, self.Value) :
            value  = self.Value.from_husl (value)
        self.value = value
    # end def husl

    @property
    def lightness (self) :
        return self.value.hsl.lightness
    # end def lightness

    @lightness.setter
    def lightness (self, value) :
        assert 0.0 <= value <= 1.0
        h, s, l = self.value.hsl
        self.value = self.Value.from_hsl ((h, s, float (value)))
    # end def lightness

    @property
    def red (self) :
        return self.value.rgb.red
    # end def red

    @red.setter
    def red (self, value) :
        assert 0.0 <= value <= 1.0
        r, g, b = self.value.rgb
        self.value = self.Value.from_rgb ((float (value), g, b))
    # end def red

    @property
    def relative_luminance (self) :
        """Relative brightness, normalized to 0 for darkest black and 1 for
           lightest white.

           https://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
        """
        def normalized (x) :
            return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
        red   = self.red
        green = self.green
        blue  = self.blue
        r     = normalized (red)
        g     = normalized (green)
        b     = normalized (blue)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    # end def relative_luminance

    @property
    def rgb (self) :
        return self.value.rgb
    # end def rgb

    @rgb.setter
    def rgb (self, value) :
        if not isinstance (value, self.Value) :
            value  = self.Value.from_rgb (value)
        self.value = value
    # end def rgb

    @property
    def saturation (self) :
        return self.value.hsl.saturation
    # end def saturation

    @saturation.setter
    def saturation (self, value) :
        assert 0.0 <= value <= 1.0
        h, s, l = self.value.hsl
        self.value = self.Value.from_hsl ((h, float (value), l))
    # end def saturation

    def contrast_ratio (self, other) :
        """Contrast ratio between `self` and `other`.

           https://www.w3.org/TR/WCAG20/#contrast-ratiodef
        """
        l1 = self.relative_luminance
        l2 = other.relative_luminance
        if l1 < l2 :
            l1, l2 = l2, l1
        return (l1 + 0.05) / (l2 + 0.05)
    # end def contrast_ratio

    def __eq__ (self, rhs) :
        try :
            rhs = getattr (rhs, "rgb"), getattr (rhs, "alpha")
        except AttributeError :
            return False
        else :
            return (self.rgb, self.alpha) == rhs
    # end def __eq__

    def __hash__ (self) :
        return hash (self.rgb, self.alpha)
    # end def __hash__

    def __invert__ (self) :
        return self.__class__.from_value \
            ( self.Value.from_rgb (tuple (1.0 - v for v in self.rgb))
            , self.alpha
            )
    # end def __invert__

    def __mul__ (self, rhs) :
        assert 0.0 <= rhs
        return self.__class__.from_value \
            ( self.Value.from_rgb (tuple (min (v * rhs, 1.0) for v in self.rgb))
            , self.alpha
            )
    # end def __mul__

# end class _Color_

class HSL (_Color_) :
    """Model a color specified by hue/saturation/lightness values."""

    name   = "hsl"
    P_Type = HSL_Value

    def __init__ (self, hue, saturation, lightness, alpha = None) :
        hue = self._normalized_hue (hue)
        self.__super.__init__ \
            ((hue, saturation / 100.0, lightness / 100.0), alpha)
    # end def __init__

    @property
    def as_HSL (self) :
        return self
    # end def as_HSL

    def _formatted_values (self) :
        h, s, l = self.value.hsl
        return "%d, %d%%, %d%%" % (h, s * 100, l * 100)
    # end def _formatted_values

# end class HSL

class HUSL (_Color_) :
    """Model a color specified by human-friendly hue/saturation/lightness values.

       http://www.husl-colors.org/
    """

    name      = "husl"
    P_Type    = HUSL_Value

    def __init__ (self, hue, saturation, lightness, alpha = None) :
        hue = self._normalized_hue (hue)
        self.__super.__init__ \
            ((hue, saturation / 100.0, lightness / 100.0), alpha)
    # end def __init__

    @TFL.Meta.Class_Property
    def HUSL_Value (cls) :
        return cls.Value.HUSL_Value
    # end def HUSL_Value

    @property
    def as_HUSL (self) :
        return self
    # end def as_HUSL

    def _formatted_values (self) :
        h, s, l = self.value.husl
        return "%d, %d%%, %d%%" % (h, s * 100, l * 100)
    # end def _formatted_values

# end class HUSL

class _RGB_ (_Color_) :
    """Model a color specified by red/green/blue values."""

    name   = "rgb"
    P_Type = RGB_Value

    def __init__ (self, red, green, blue, alpha = None) :
        self.__super.__init__ ((red, green, blue), alpha)
    # end def __init__

    def _formatted_values (self) :
        return "%d%%, %d%%, %d%%" % \
            tuple (int (v * 100) for v in self.value.rgb)
    # end def _formatted_values

# end class _RGB_

class RGB (_RGB_) :
    """Model a color specified by red/green/blue values."""

    @property
    def as_RGB (self) :
        return self
    # end def as_RGB

# end class RGB

class RGB_8 (_RGB_) :
    """Model a color specified by 8-bit values for red/green/blue."""

    def __init__ (self, red, green, blue, alpha = None) :
        self.__super.__init__ \
            ( * tuple (v / 255.0 for v in (red, green, blue))
            , alpha = alpha
            )
    # end def __init__

    @property
    def as_RGB_8 (self) :
        return self
    # end def as_RGB_8

    def _formatted_values (self) :
        return "%d, %d, %d" % tuple (int (v * 255) for v in self.value.rgb)
    # end def _formatted_values

# end class RGB_8

class RGB_P (_RGB_) :
    """Model a color specified by percent values for red/green/blue."""

    def __init__ (self, red, green, blue, alpha = None) :
        self.__super.__init__ \
            ( * tuple (v / 100.0 for v in (red, green, blue))
            , alpha = alpha
            )
    # end def __init__

    @property
    def as_RGB_P (self) :
        return self
    # end def as_RGB_P

# end class RGB_P

class RGB_X (_RGB_) :
    """Model a color specified by a hexadecimal string for RGB."""

    _fmt = \
        ( r"^#"
          r"(?P<red>[0-9a-zA-Z]%(q)s)"
          r"(?P<green>[0-9a-zA-Z]%(q)s)"
          r"(?P<blue>[0-9a-zA-Z]%(q)s)"
          r"(?P<alpha>[0-9a-zA-Z]%(q)s)?"
          r"$"
        )
    _pat = TFL.Multi_Regexp (_fmt % dict (q = "{2}"), _fmt % dict (q = ""))

    def __init__ (self, s, alpha = None) :
        pat = self._pat
        if pat.match (s) :
            r, g, b = pat.red, pat.green, pat.blue
            if len (r) == 1 :
                r, g, b = r*2, g*2, b*2
            if a := pat.alpha :
                if len (a) == 1 :
                    a   = a*2
                alpha   = int (a, 16) / 255.0
            self.__super.__init__ \
                ( * tuple ((int (x, 16) / 255.0) for x in (r, g, b))
                , alpha = alpha
                )
        else :
            raise ValueError \
                ( "Need a hexadecimal color specification like "
                  "'#ABCDEF' or '#ABC', got '%s' instead"
                % (s, )
                )
    # end def __init__

    @property
    def as_RGB_X (self) :
        return self
    # end def as_RGB_X

    def formatted (self) :
        return self._formatted_values ()
    # end def formatted

    def reprified (self) :
        return "%s (%s)" % \
            ( self.__class__.__name__
            , portable_repr (self._formatted_values ())
            )
    # end def reprified

    def _formatted_values (self) :
        values = self.value.hex_tuple
        if (alpha := self.alpha) is not None :
            values += ("%2.2X" % (int (alpha*255), ), )
        return "#" + "".join (self.value.CSS_hex_tuple (* values))
    # end def _formatted_values

# end class RGB_X

class SVG_Color (RGB_X) :
    """Model a color named as specified by SVG 1.0 and CSS-3."""

    ### http://www.w3.org/TR/css3-color/#rgb-color
    Map = dict \
        ( aliceblue               = "#F0F8FF"
        , antiquewhite            = "#FAEBD7"
        , aqua                    = "#00FFFF"
        , aquamarine              = "#7FFFD4"
        , azure                   = "#F0FFFF"
        , beige                   = "#F5F5DC"
        , bisque                  = "#FFE4C4"
        , black                   = "#000000"
        , blanchedalmond          = "#FFEBCD"
        , blue                    = "#0000FF"
        , blueviolet              = "#8A2BE2"
        , brown                   = "#A52A2A"
        , burlywood               = "#DEB887"
        , cadetblue               = "#5F9EA0"
        , chartreuse              = "#7FFF00"
        , chocolate               = "#D2691E"
        , coral                   = "#FF7F50"
        , cornflowerblue          = "#6495ED"
        , cornsilk                = "#FFF8DC"
        , crimson                 = "#DC143C"
        , cyan                    = "#00FFFF"
        , darkblue                = "#00008B"
        , darkcyan                = "#008B8B"
        , darkgoldenrod           = "#B8860B"
        , darkgray                = "#A9A9A9"
        , darkgreen               = "#006400"
        , darkgrey                = "#A9A9A9"
        , darkkhaki               = "#BDB76B"
        , darkmagenta             = "#8B008B"
        , darkolivegreen          = "#556B2F"
        , darkorange              = "#FF8C00"
        , darkorchid              = "#9932CC"
        , darkred                 = "#8B0000"
        , darksalmon              = "#E9967A"
        , darkseagreen            = "#8FBC8F"
        , darkslateblue           = "#483D8B"
        , darkslategray           = "#2F4F4F"
        , darkslategrey           = "#2F4F4F"
        , darkturquoise           = "#00CED1"
        , darkviolet              = "#9400D3"
        , deeppink                = "#FF1493"
        , deepskyblue             = "#00BFFF"
        , dimgray                 = "#696969"
        , dimgrey                 = "#696969"
        , dodgerblue              = "#1E90FF"
        , firebrick               = "#B22222"
        , floralwhite             = "#FFFAF0"
        , forestgreen             = "#228B22"
        , fuchsia                 = "#FF00FF"
        , gainsboro               = "#DCDCDC"
        , ghostwhite              = "#F8F8FF"
        , gold                    = "#FFD700"
        , goldenrod               = "#DAA520"
        , gray                    = "#808080"
        , green                   = "#008000"
        , greenyellow             = "#ADFF2F"
        , grey                    = "#808080"
        , honeydew                = "#F0FFF0"
        , hotpink                 = "#FF69B4"
        , indianred               = "#CD5C5C"
        , indigo                  = "#4B0082"
        , ivory                   = "#FFFFF0"
        , khaki                   = "#F0E68C"
        , lavender                = "#E6E6FA"
        , lavenderblush           = "#FFF0F5"
        , lawngreen               = "#7CFC00"
        , lemonchiffon            = "#FFFACD"
        , lightblue               = "#ADD8E6"
        , lightcoral              = "#F08080"
        , lightcyan               = "#E0FFFF"
        , lightgoldenrodyellow    = "#FAFAD2"
        , lightgray               = "#D3D3D3"
        , lightgreen              = "#90EE90"
        , lightgrey               = "#D3D3D3"
        , lightpink               = "#FFB6C1"
        , lightsalmon             = "#FFA07A"
        , lightseagreen           = "#20B2AA"
        , lightskyblue            = "#87CEFA"
        , lightslategray          = "#778899"
        , lightslategrey          = "#778899"
        , lightsteelblue          = "#B0C4DE"
        , lightyellow             = "#FFFFE0"
        , lime                    = "#00FF00"
        , limegreen               = "#32CD32"
        , linen                   = "#FAF0E6"
        , magenta                 = "#FF00FF"
        , maroon                  = "#800000"
        , mediumaquamarine        = "#66CDAA"
        , mediumblue              = "#0000CD"
        , mediumorchid            = "#BA55D3"
        , mediumpurple            = "#9370DB"
        , mediumseagreen          = "#3CB371"
        , mediumslateblue         = "#7B68EE"
        , mediumspringgreen       = "#00FA9A"
        , mediumturquoise         = "#48D1CC"
        , mediumvioletred         = "#C71585"
        , midnightblue            = "#191970"
        , mintcream               = "#F5FFFA"
        , mistyrose               = "#FFE4E1"
        , moccasin                = "#FFE4B5"
        , navajowhite             = "#FFDEAD"
        , navy                    = "#000080"
        , oldlace                 = "#FDF5E6"
        , olive                   = "#808000"
        , olivedrab               = "#6B8E23"
        , orange                  = "#FFA500"
        , orangered               = "#FF4500"
        , orchid                  = "#DA70D6"
        , palegoldenrod           = "#EEE8AA"
        , palegreen               = "#98FB98"
        , paleturquoise           = "#AFEEEE"
        , palevioletred           = "#DB7093"
        , papayawhip              = "#FFEFD5"
        , peachpuff               = "#FFDAB9"
        , peru                    = "#CD853F"
        , pink                    = "#FFC0CB"
        , plum                    = "#DDA0DD"
        , powderblue              = "#B0E0E6"
        , purple                  = "#800080"
        , red                     = "#FF0000"
        , rosybrown               = "#BC8F8F"
        , royalblue               = "#4169E1"
        , saddlebrown             = "#8B4513"
        , salmon                  = "#FA8072"
        , sandybrown              = "#F4A460"
        , seagreen                = "#2E8B57"
        , seashell                = "#FFF5EE"
        , sienna                  = "#A0522D"
        , silver                  = "#C0C0C0"
        , skyblue                 = "#87CEEB"
        , slateblue               = "#6A5ACD"
        , slategray               = "#708090"
        , snow                    = "#FFFAFA"
        , springgreen             = "#00FF7F"
        , steelblue               = "#4682B4"
        , tan                     = "#D2B48C"
        , teal                    = "#008080"
        , thistle                 = "#D8BFD8"
        , tomato                  = "#FF6347"
        , turquoise               = "#40E0D0"
        , violet                  = "#EE82EE"
        , wheat                   = "#F5DEB3"
        , white                   = "#FFFFFF"
        , whitesmoke              = "#F5F5F5"
        , yellow                  = "#FFFF00"
        , yellowgreen             = "#9ACD32"
        )

    _Pam = None

    def __init__ (self, name, alpha = None) :
        key = name.lower ().replace (" ", "")
        self.__super.__init__ (self.Map [key], alpha)
    # end def __init__

    @property
    def as_RGB_X (self) :
        return RGB_X.cast (self)
    # end def as_RGB_X

    def formatted (self) :
        if self.alpha is None :
            name = self.Pam.get (self.value.hex)
            if name is not None :
                return name
            else :
                return self._formatted_values ()
        else :
            return self.as_RGB_8.formatted ()
    # end def formatted

    def reprified (self) :
        name = self.Pam.get (self.value.hex)
        if name is not None :
            alpha = self.alpha
            args  = (name, ) if alpha is None else (name, alpha)
            return "%s (%s)" % \
                ( self.__class__.__name__
                , ", ".join (portable_repr (a) for a in args)
                )
        else :
            return self.__super.reprified ()
    # end def reprified

    @property
    def Pam (self) :
        if self._Pam is None :
            self.__class__._Pam = dict \
                ((v, k) for (k, v) in sorted (pyk.iteritems (self.Map)))
        return self._Pam
    # end def Pam

# end class SVG_Color

class _Ok_Color_ (_Base_Color_) :
    """Base class modelling a mutable Ok-color."""

    Value       = Ok_Value
    formatter   = None
    _format     = "%s %s %s"

    @property
    def as_OKLab (self) :
        return OKLab.cast (self)
    # end def as_OKLab

    @property
    def as_OKLab_P (self) :
        return OKLab_P.cast (self)
    # end def as_OKLab_P

    @property
    def as_OKLCh (self) :
        return OKLCh.cast (self)
    # end def as_OKLCh

    @property
    def as_OKLCh_P (self) :
        return OKLCh_P.cast (self)
    # end def as_OKLCh_P

    @property
    def as_rgb (self) :
        xyz = XYZ_D65.from_oklab (* self.value.oklab)
        rgb = xyz.as_rgb
        return RGB (* rgb, alpha = self.alpha)
    # end def as_rgb

    @property
    def chroma (self) :
        return self.value.oklch.C
    # end def chroma

    @chroma.setter
    def chroma (self, v) :
        L, C, H = self.value.oklch
        self.value = self.Value.from_oklch (L, v, H)
    # end def chroma

    @property
    def hue (self) :
        return self.value.oklch.H
    # end def hue

    @hue.setter
    def hue (self, v) :
        L, C, H = self.value.oklch
        self.value = self.Value.from_oklch (L, C, v)
    # end def hue

    @property
    def lightness (self) :
        return self.value.oklch.L
    # end def lightness

    @lightness.setter
    def lightness (self, v) :
        L, C, H = self.value.oklch
        self.value = self.Value.from_oklch (v, C, H)
    # end def lightness

    def copy (self, ** kwds) :
        """Return a copy with values changed by `kwds`. `d*` are deltas."""
        result = super ().copy ()
        result.set (** kwds)
        return result
    # end def copy

    def formatted (self) :
        v = self._formatted_values ()
        if self.alpha is not None :
            return "%s(%s / %s)" % (self.name, v, self.alpha)
        else :
            return "%s(%s)" % (self.name, v)
    # end def formatted

    def set (self, ** kwds) :
        """Set attributes passed as `kwds`. `dl`··· are deltas."""
        for k in "lightness", "chroma", "hue", "alpha" :
            c   = k [0]
            v   = kwds.pop (k, None)
            dv  = kwds.pop ("d"+c, 0)
            if v is None :
                v   = kwds.pop (c, None)
            if v is not None or dv :
                if v is None :
                    v = getattr (self, k)
                setattr (self, k, v + dv)
        if kwds :
            raise TypeError \
                ( ( "Unknown keyword arguments: %s. Supported keywords are:\n"
                    "lightness, chroma, hue, alpha, l, c, h, a, dl, dc, dh, da"
                  )
                % (sorted (kwds), )
                )
        return self
    # end def set

    def _formatted_values (self) :
        rvs = self._rep_values (getattr (self.value, self.name))
        return self._format % rvs
    # end def _formatted_values

    def _rep_values (self, values) :
        return tuple (portable_repr (v) for v in values)
    # end def _rep_values

    def __eq__ (self, rhs) :
        try :
            rhs = getattr (rhs.value, "oklch"), getattr (rhs, "alpha")
        except AttributeError :
            return False
        else :
            return (self.value.oklch, self.alpha) == rhs
    # end def __eq__

    def __hash__ (self) :
        return hash (self.value.oklch, self.alpha)
    # end def __hash__

    def __invert__ (self) :
        L, C, H = self.value.oklch
        if L in (0, 1) or C == 0 :
            L = 1 - L
        else :
            H = self._normalized_hue (H + 180)
        return self.__class__.from_value \
            ( self.Value.from_oklch (L, C, H)
            , self.alpha
            )
    # end def __invert__

# end class _Ok_Color_

class _OKLab_ (_Ok_Color_) :

    name        = "oklab"
    P_Type      = OKLab_Value

    def __init__ (self, lightness, a, b, alpha = None) :
        super ().__init__ ((lightness, a, b), alpha)
    # end def __init__

# end class _OKLab_

class OKLab (_OKLab_) :
    """Model a color specified in the Oklab color system."""

    @property
    def as_OKLab (self) :
        return self
    # end def as_OKLab

# end class OKLab

class OKLab_P (_OKLab_) :
    """Model a color specified in Oklab color system, lightness in Percent.

    >>> _Color_.formatter = None ### ensure consistent formatting

    From https://colorjs.io/tests/conversions.html
    >>> srgb_black      = OKLab_P (  0, 0, 0)
    >>> srgb_white      = OKLab_P (100, 0, 0)

    >>> srgb_red        = OKLab_P (62.7955,  0.224863,  0.125846)
    >>> srgb_lime       = OKLab_P (86.644,  -0.233888,  0.179498)
    >>> srgb_blue       = OKLab_P (45.2014, -0.032457, -0.311528)
    >>> srgb_cyan       = OKLab_P (90.5399, -0.149444, -0.039398)
    >>> srgb_magenta    = OKLab_P (70.1674,  0.274566, -0.169156)
    >>> srgb_yellow     = OKLab_P (96.7983, -0.071369,  0.198570)

    >>> print ("srgb_black:", srgb_black, srgb_black.as_OKLCh_P)
    srgb_black: oklab(0% 0 0) oklch(0% 0 0)

    >>> print ("srgb_white:", srgb_white, srgb_white.as_OKLCh_P)
    srgb_white: oklab(100% 0 0) oklch(100% 0 0)

    >>> print ("srgb_red:", srgb_red, srgb_red.as_OKLCh_P)
    srgb_red: oklab(62.7955% 0.224863 0.125846) oklch(62.7955% 0.257683108653 29.2338338996)

    >>> print ("srgb_lime:", srgb_lime, srgb_lime.as_OKLCh_P)
    srgb_lime: oklab(86.644% -0.233888 0.179498) oklch(86.644% 0.294827285962 142.495463253)

    >>> print ("srgb_blue:", srgb_blue, srgb_blue.as_OKLCh_P)
    srgb_blue: oklab(45.2014% -0.032457 -0.311528) oklch(45.2014% 0.313214226422 264.052014958)

    >>> print ("srgb_cyan:", srgb_cyan, srgb_cyan.as_OKLCh_P)
    srgb_cyan: oklab(90.5399% -0.149444 -0.039398) oklch(90.5399% 0.154550029246 194.768885677)

    >>> print ("srgb_magenta:", srgb_magenta, srgb_magenta.as_OKLCh_P)
    srgb_magenta: oklab(70.1674% 0.274566 -0.169156) oklch(70.1674% 0.322490683109 328.36339946)

    >>> print ("srgb_yellow:", srgb_yellow, srgb_yellow.as_OKLCh_P)
    srgb_yellow: oklab(96.7983% -0.071369 0.19857) oklch(96.7983% 0.21100611143 109.769189006)

    >>> print ("srgb_yellow:", srgb_yellow.as_OKLab, srgb_yellow.as_OKLCh)
    srgb_yellow: oklab(0.967983 -0.071369 0.19857) oklch(0.967983 0.21100611143 109.769189006)

    >>> print ("srgb_black:", srgb_black.as_rgb)
    srgb_black: rgb(0%, 0%, 0%)

    >>> print ("srgb_white:", srgb_white.as_rgb)
    srgb_white: rgb(100%, 99%, 99%)

    >>> print ("srgb_red:", srgb_red.as_rgb)
    srgb_red: rgb(99%, 0%, 0%)

    >>> print ("srgb_lime:", srgb_lime.as_rgb)
    srgb_lime: rgb(0%, 100%, 0%)

    >>> print ("srgb_blue:", srgb_blue.as_rgb)
    srgb_blue: rgb(0%, 0%, 100%)

    >>> print ("srgb_cyan:", srgb_cyan.as_rgb)
    srgb_cyan: rgb(0%, 99%, 99%)

    >>> print ("srgb_magenta:", srgb_magenta.as_rgb)
    srgb_magenta: rgb(99%, 0%, 100%)

    >>> print ("srgb_yellow:", srgb_yellow.as_rgb)
    srgb_yellow: rgb(100%, 100%, 0%)

    >>> _OKLab_.formatter = OKLCh_P
    >>> print (srgb_black, ~ srgb_black)
    oklch(0% 0 0) oklch(100% 0 0)

    >>> print (srgb_white, ~ srgb_white)
    oklch(100% 0 0) oklch(0% 0 0)

    >>> print (srgb_red, ~ srgb_red)
    oklch(62.7955% 0.257683108653 29.2338338996) oklch(62.7955% 0.257683108653 209.2338339)

    """

    _format         = "%s%% %s %s"

    def __init__ (self, lightness, chroma, hue, alpha = None) :
        super ().__init__ (lightness / 100, chroma, hue, alpha)
    # end def __init__

    @property
    def as_OKLab_P (self) :
        return self
    # end def as_OKLab_P

    def _rep_values (self, values) :
        l, a, b = values
        return super ()._rep_values ((l * 100, a, b))
    # end def _rep_values

# end class OKLab_P

class _OKLCh_ (_Ok_Color_) :

    name        = "oklch"
    P_Type      = OKLCh_Value

    def __init__ (self, lightness, chroma, hue, alpha = None) :
        hue = self._normalized_hue (hue)
        super ().__init__ ((lightness, chroma, hue), alpha)
    # end def __init__

# end class _OKLCh_

class OKLCh (_OKLCh_) :
    """Model a color specified in Oklch color system.    """

    @property
    def as_OKLCh (self) :
        return self
    # end def as_OKLCh

# end class OKLCh

class OKLCh_P (_OKLCh_) :
    """Model a color specified in Oklch color system, lightness in Percent.

    >>> _Color_.formatter = None ### ensure consistent formatting

    >>> black   = OKLCh_P (  0, 0,       0)
    >>> white   = OKLCh_P (100, 0,       0)

    >>> red     = OKLCh_P ( 50, 0.37,   30)
    >>> yellow  = OKLCh_P ( 99, 0.37,   90)
    >>> orange  = OKLCh_P ( 70, 0.19,   60)
    >>> green   = OKLCh_P ( 73, 0.37,  140)
    >>> green_2 = OKLCh_P ( 73, 0.37,  140, alpha = 0.5)
    >>> cyan    = OKLCh_P ( 90, 0.37,  195)
    >>> blue    = OKLCh_P ( 69, 0.26,  260)
    >>> magenta = OKLCh_P ( 75, 0.37,  330)

    from https://colorjs.io/tests/conversions.html
    >>> srgb_red    = OKLCh_P (62.7954, 0.257627,  29.2271)
    >>> srgb_lime   = OKLCh_P (86.6439, 0.294803, 142.5112)
    >>> srgb_blue   = OKLCh_P (45.2013, 0.313319, 264.05854)

    >>> print ("black:", black, black.as_OKLab_P)
    black: oklch(0% 0 0) oklab(0% 0 0)

    >>> print ("white:", white, white.as_OKLab_P)
    white: oklch(100% 0 0) oklab(100% 0 0)

    >>> print ("Black:", black, "White:", white)
    Black: oklch(0% 0 0) White: oklch(100% 0 0)

    >>> print ("Red:", red, "Green:", green, "Blue:", blue)
    Red: oklch(50% 0.37 30) Green: oklch(73% 0.37 140) Blue: oklch(69% 0.26 260)

    >>> print ("Green with 1/2 opacity:", green_2)
    Green with 1/2 opacity: oklch(73% 0.37 140 / 0.5)

    >>> print ("White as_OKLab:", white.as_OKLab_P)
    White as_OKLab: oklab(100% 0 0)

    >>> print ("Red as_OKLab:", red.as_OKLab_P)
    Red as_OKLab: oklab(50% 0.3204293994 0.185)

    >>> print ("srgb red:", srgb_red, srgb_red.as_OKLab_P)
    srgb red: oklch(62.7954% 0.257627 29.2271) oklab(62.7954% 0.224828823437 0.125792174959)

    >>> print ("srgb lime:", srgb_lime, srgb_lime.as_OKLab_P)
    srgb lime: oklch(86.6439% 0.294803 142.5112) oklab(86.6439% -0.233918021507 0.17941897342)

    >>> print ("srgb blue:", srgb_blue, srgb_blue.as_OKLab_P)
    srgb blue: oklch(45.2013% 0.313319 264.05854) oklab(45.2013% -0.0324323672555 -0.311635905048)

    >>> print ("srgb blue:", srgb_blue.as_OKLCh, srgb_blue.as_OKLab)
    srgb blue: oklch(0.452013 0.313319 264.05854) oklab(0.452013 -0.0324323672555 -0.311635905048)

    >>> print ("srgb blue", srgb_blue.as_rgb)
    srgb blue rgb(0%, 0%, 100%)

    >>> grey = OKLCh_P (50, 0, 0)
    >>> print ("grey 50%:", grey)
    grey 50%: oklch(50% 0 0)

    >>> grey.set (dl = +0.1)
    OKLCh_P (60 0 0)
    >>> print ("grey 50% + 10%:", grey)
    grey 50% + 10%: oklch(60% 0 0)

    >>> print ("grey 30%, alpha = 0.7:", grey.copy (lightness = 0.3, a= 0.7))
    grey 30%, alpha = 0.7: oklch(30% 0 0 / 0.7)

    """

    ### L/C pairings that are defined for all values of H in P3
    ### - found by playing with https://oklch.com/ in Safari
    ###   * 2024-03-17 FF doesn't support P3 for my display
    L_C_in_P3 = \
        { 95 : 0.02
        , 90 : 0.05
        , 85 : 0.08
        , 80 : 0.10
        , 75 : 0.13
        , 70 : 0.16
        , 65 : 0.14
        , 60 : 0.13
        , 55 : 0.12
        , 50 : 0.11
        , 45 : 0.10
        , 40 : 0.09
        , 35 : 0.07
        , 30 : 0.06
        , 25 : 0.05
        }

    _format         = "%s%% %s %s"

    def __init__ (self, lightness, chroma, hue, alpha = None) :
        super ().__init__ (lightness / 100, chroma, hue, alpha)
    # end def __init__

    @property
    def as_OKLCh_P (self) :
        return self
    # end def as_OKLCh_P

    def _rep_values (self, values) :
        l, c, h = values
        return super ()._rep_values ((l * 100, c, h))
    # end def _rep_values

# end class OKLCh_P

class XYZ_D65 (TFL.Meta.Object) :
    """CIE XYZ color space

    >>> xyz_rgb = XYZ_D65.from_rgb (1, 1, 1)

    >>> print (portable_repr (xyz_rgb.values))
    (0.950455927052, 1, 1.08905775076)

    >>> print (portable_repr (xyz_rgb.as_rgb))
    (1, 1, 1)

    >>> print (portable_repr (xyz_rgb.as_OKLab))
    (1, -4.99600361081e-16, 0)

    >>> xyz_oklab = XYZ_D65.from_oklab (1, 0, 0)

    >>> print (portable_repr (xyz_oklab.values))
    (0.950455927052, 1, 1.08905775076)

    >>> print (portable_repr (xyz_oklab.as_rgb))
    (1, 1, 1)

    """

    ### https://bottosson.github.io/posts/oklab/
    ### https://colorjs.io ··· oklab.js
    oklab_to_lms    = Mx \
        ( [  1.0000000000000000,  0.3963377773761749,  0.2158037573099136 ]
        , [  1.0000000000000000, -0.1055613458156586, -0.0638541728258133 ]
        , [  1.0000000000000000, -0.0894841775298119, -1.2914855480194092 ]
        )
    lms_to_xyz      = Mx \
        ( [  1.2268798758459243, -0.5578149944602171,  0.2813910456659647 ]
        , [ -0.0405757452148008,  1.1122868032803170, -0.0717110580655164 ]
        , [ -0.0763729366746601, -0.4214933324022432,  1.5869240198367816 ]
        )

    xyz_to_lms      = Mx \
        ( [  0.8190224379967030,  0.3619062600528904, -0.1288737815209879 ]
        , [  0.0329836539323885,  0.9292868615863434,  0.0361446663506424 ]
        , [  0.0481771893596242,  0.2642395317527308,  0.6335478284694309 ]
        )
    lms_to_oklab    = Mx \
        ( [  0.2104542683093140,  0.7936177747023054, -0.0040720430116193 ]
        , [  1.9779985324311684, -2.4285922420485799,  0.4505937096174110 ]
        , [  0.0259040424655478,  0.7827717124575296, -0.8086757549230774 ]
        )

    ### https://en.wikipedia.org/wiki/SRGB
    ### https://colorjs.io ··· srgb-linear.js
    rgb_to_xyz      = Mx \
        ( [  0.41239079926595934,  0.357584339383878,    0.1804807884018343  ]
        , [  0.21263900587151027,  0.715168678767756,    0.07219231536073371 ]
        , [  0.01933081871559182,  0.11919477979462598,  0.9505321522496607  ]
        )

    xyz_to_rgb      = Mx \
        ( [  3.2409699419045226,  -1.537383177570094,   -0.4986107602930034  ]
        , [ -0.9692436362808796,   1.8759675015077202,   0.04155505740717559 ]
        , [  0.05563007969699366, -0.20397695888897652,  1.0569715142428786  ]
        )

    def __init__ (self, * xyz) :
        self.values = x, y, z = xyz
        self.matrix = Mx.CV (xyz)
    # end def __init__

    @classmethod
    def from_oklab (cls, * Lab) :
        L, a, b     = Lab
        lms_cbrt    = cls.oklab_to_lms * Mx.CV (Lab)
        lms         = Mx.CV (v ** 3 for v in lms_cbrt.cv)
        xyz         = cls.lms_to_xyz * lms
        return cls (* xyz.cv)
    # end def from_oklab

    @classmethod
    def from_rgb (cls, * rgb) :
        r, g, b     = rgb
        rgb_linear  = Mx.CV \
            (   (v / 12.92) if v <= 0.04045
                  else (((v + 0.055) / 1.055) ** 2.4)
            for v in rgb
            )
        xyz = cls.rgb_to_xyz * rgb_linear
        return cls (* xyz.cv)
    # end def from_rgb

    @property
    def as_OKLab (self) :
        lms         = self.xyz_to_lms * self.matrix
        lms_cbrt    = Mx.CV (cbrt (v) for v in lms.cv)
        result      = self.lms_to_oklab * lms_cbrt
        return result.cv
    # end def as_OKLab

    @property
    def as_rgb (self) :
        rgb_linear  = self.xyz_to_rgb * self.matrix
        result      = tuple \
            (   12.92 * v if v <= 0.0031308
                    else (1.055 * (v ** (1 / 2.4)) - 0.055)
            for v in rgb_linear.cv
            )
        return result
    # end def as_rgb

# end class XYZ_D65

__all__ = tuple \
    ( k for (k, v) in pyk.iteritems (globals ())
    if k != "_Color_" and isinstance (v, M_Color)
    )

__doc__ = """
Classes modelling modern color representations::

    >>> c = OKLCh_P (50, 0.37, 30)
    >>> print (c, c.as_OKLab_P)
    oklch(50% 0.37 30) oklab(50% 0.3204293994 0.185)

    >>> print (c.as_OKLCh, c.as_OKLab)
    oklch(0.5 0.37 30) oklab(0.5 0.3204293994 0.185)

    >>> c.lightness += 0.2
    >>> print (c, c.as_OKLab_P)
    oklch(70% 0.37 30) oklab(70% 0.3204293994 0.185)

    >>> c.chroma -= 0.25
    >>> print (c, c.as_OKLab_P)
    oklch(70% 0.12 30) oklab(70% 0.103923048454 0.06)

    >>> c.hue += 60
    >>> print (c, c.as_OKLab_P)
    oklch(70% 0.12 90) oklab(70% 0 0.12)


Classes modelling various traditional color representations::

    >>> c = RGB_8 (255, 0, 0)
    >>> d = c.as_RGB_X
    >>> h = c.as_HSL
    >>> u = c.as_HUSL
    >>> print (c, d, h, u)
    rgb(255, 0, 0) #F00 hsl(0, 100%, 50%) husl(12, 100%, 53%)
    >>> print (HUSL (12, 100, 53))
    husl(12, 100%, 53%)
    >>> (c, d, h, u)
    (RGB_8 (255, 0, 0), RGB_X ('#F00'), HSL (0, 100, 50), HUSL (12, 100, 53))

    >>> cn = ~ c
    >>> hn = ~ h
    >>> un = ~ u
    >>> print (cn, hn, un)
    rgb(0, 255, 255) hsl(180, 100%, 50%) husl(192, 99%, 91%)
    >>> (cn, hn, un)
    (RGB_8 (0, 255, 255), HSL (180, 100, 50), HUSL (192, 99, 91))

    >>> ca = RGB (* c.rgb, alpha = 0.25).as_RGB_8
    >>> da = ca.as_RGB_X
    >>> ha = ca.as_HSL
    >>> ua = ca.as_HUSL
    >>> print (ca, da, ha, ua)
    rgba(255, 0, 0, 0.25) #FF00003F hsla(0, 100%, 50%, 0.25) husla(12, 100%, 53%, 0.25)
    >>> (ca, da, ha, ua)
    (RGB_8 (255, 0, 0, 0.25), RGB_X ('#FF00003F'), HSL (0, 100, 50, 0.25), HUSL (12, 100, 53, 0.25))

    >>> b  = RGB (0, 0, 0)
    >>> hb = b.as_HSL
    >>> ub = b.as_HUSL
    >>> w  = RGB (1, 1, 1)
    >>> hw = w.as_HSL
    >>> uw = w.as_HUSL
    >>> print (b, ~b, hb, ~hb, ub, ~ub)
    rgb(0%, 0%, 0%) rgb(100%, 100%, 100%) hsl(0, 0%, 0%) hsl(0, 0%, 100%) husl(0, 0%, 0%) husl(19, 0%, 100%)
    >>> print (~w, w, ~hw, hw, uw, ~ uw)
    rgb(0%, 0%, 0%) rgb(100%, 100%, 100%) hsl(0, 0%, 0%) hsl(0, 0%, 100%) husl(19, 0%, 100%) husl(0, 0%, 0%)
    >>> (b, ~b, hb, ~hb, ub, ~ub)
    (RGB (0, 0, 0), RGB (100, 100, 100), HSL (0, 0, 0), HSL (0, 0, 100), HUSL (0, 0, 0), HUSL (19, 0, 100))
    >>> (~w, w, ~hw, hw, uw, ~ uw)
    (RGB (0, 0, 0), RGB (100, 100, 100), HSL (0, 0, 0), HSL (0, 0, 100), HUSL (19, 0, 100), HUSL (0, 0, 0))

    >>> print (c * 0.5, w * 0.8)
    rgb(127, 0, 0) rgb(80%, 80%, 80%)
    >>> (c * 0.5, w * 0.8)
    (RGB_8 (127, 0, 0), RGB (80, 80, 80))

    >>> _Color_.formatter = RGB_X
    >>> print (b, ~b, hb, ~hb, ub, ~ub)
    #000 #FFF #000 #FFF #000 #FFF
    >>> (b, ~b, hb, ~hb, ub, ~ub)
    (RGB_X ('#000'), RGB_X ('#FFF'), RGB_X ('#000'), RGB_X ('#FFF'), RGB_X ('#000'), RGB_X ('#FFF'))
    >>> print (cn, hn, un)
    #0FF #0FF #0FF
    >>> (cn, hn, un)
    (RGB_X ('#0FF'), RGB_X ('#0FF'), RGB_X ('#0FF'))
    >>> print (ca, da, ha, ua)
    #FF00003F #FF00003F #FF00003F #FF00003F
    >>> (ca, da, ha, ua)
    (RGB_X ('#FF00003F'), RGB_X ('#FF00003F'), RGB_X ('#FF00003F'), RGB_X ('#FF00003F'))

    >>> _Color_.formatter = HSL
    >>> print (b, ~b, hb, ~hb, ub, ~ub)
    hsl(0, 0%, 0%) hsl(0, 0%, 100%) hsl(0, 0%, 0%) hsl(0, 0%, 100%) hsl(0, 0%, 0%) hsl(0, 0%, 100%)
    >>> print (cn, hn, un)
    hsl(180, 100%, 50%) hsl(180, 100%, 50%) hsl(180, 100%, 50%)
    >>> print (ca, da, ha, ua)
    hsla(0, 100%, 50%, 0.25) hsla(0, 100%, 50%, 0.25) hsla(0, 100%, 50%, 0.25) hsla(0, 100%, 50%, 0.25)

    >>> _Color_.formatter = RGB_X
    >>> print (SVG_Color ("Gray"), SVG_Color ("Dark red"), SVG_Color ("blue", 0.5))
    #808080 #8B0000 #0000FF7F

    >>> _Color_.formatter = None
    >>> print (SVG_Color ("Gray"), SVG_Color ("Dark red"), SVG_Color ("blue", 0.5))
    grey darkred rgba(0, 0, 255, 0.5)
    >>> (SVG_Color ("Gray"), SVG_Color ("Dark red"), SVG_Color ("blue", 0.5))
    (SVG_Color ('grey'), SVG_Color ('darkred'), SVG_Color ('blue', 0.5))

    >>> _Color_.formatter = RGB_X
    >>> print (w, w.relative_luminance)
    #FFF 1.0
    >>> print (b, b.relative_luminance)
    #000 0.0

    >>> print (w, b, w.contrast_ratio (b), b.contrast_ratio (w))
    #FFF #000 21.0 21.0

    >>> print (w, b, w.contrast_ratio (w), b.contrast_ratio (b))
    #FFF #000 1.0 1.0

"""

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.Color
