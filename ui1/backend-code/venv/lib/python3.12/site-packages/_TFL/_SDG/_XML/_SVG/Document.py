# -*- coding: utf-8 -*-
# Copyright (C) 2005-2024 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.XML.SVG.Document
#
# Purpose
#    Model a SVG document
#
#    See: https://www.w3.org/TR/SVG11/expanded-toc.html
#
# Revision Dates
#     5-Sep-2005 (CT) Creation
#     6-Sep-2005 (CT) Creation continued
#    29-Aug-2008 (CT) Doctest corrected
#    27-Aug-2012 (CT) Add lots of Elem_Types and attributes
#    31-Aug-2012 (RS) Add `**kw` in `cls` instantiation of `Marker.Plug`
#    19-Sep-2012 (RS) Add `Arrow_Head_A`
#    20-Sep-2012 (RS) marker `size` is now `design_size` use
#                     `marker_width`, `marker_height` for scaling
#    20-Sep-2012 (RS) Add `Arrow_Head_Bar`
#    26-Sep-2012 (CT) Add `klass` to `Root`
#    27-Sep-2012 (CT) Add `preserve_aspect_ratio` to `Root`
#    13-Feb-2017 (CT) Add `Gradient_Stop`, `Radial_Gradient`, and `SVG` elements
#    17-Feb-2017 (CT) Add `vector_effect`
#    17-Feb-2017 (CT) Change `_convert_points` to use `%s`, not `%d`
#                     + Ditto for `_convert_points_path`
#     4-Mar-2017 (CT) Add and use `_convert_view_box`
#     5-Nov-2022 (CT) Add `Linear_Gradient`
#    18-Nov-2022 (CT) Add `Style`
#    18-Nov-2022 (CT) Add support for `closepath` to `_convert_points_path`
#    12-Dec-2022 (CT) Fix support for `closepath` in `_convert_points_path`
#    17-Dec-2022 (CT) Add `dominant_baseline`
#    19-Mar-2024 (CT) Derive `Title` from `Element_Compact`, not `Element`
#    20-Apr-2024 (CT) Add missing attributes to `SVG` and `Symbol`
#    20-Apr-2024 (CT) Add `href` attribute to `Use`
#    24-Apr-2024 (CT) Derive `Text` from `Element_Compact`, not `Element`
#                     + Ditto for `Text_Path`
#    ««revision-date»»···
#--

"""
    >>> svg = Document (Root (width="12cm", height="4cm", view_box="0 0 1200 400"))
    >>> svg.add (Rect
    ...   (x="1", y="1", width="1198", height="398", fill="none", stroke="blue"))
    >>> svg.add (Rect
    ...   (x="100", y="100", width="400", height="200", rx="50", fill="green"))
    >>> svg.add (Group
    ...   (Rect (x="0", y="0", width="400", height="200", rx="50", fill="none", stroke="purple"), elid = 1, transform="translate(700 210) rotate(-30)"))
    >>> svg.add (Circle (cx="600", cy="200", r="100", fill="red", stroke="blue"))
    >>> svg.add (Ellipse (rx="250", ry="100", fill="red"))
    >>> svg.add (Ellipse
    ...   (transform="translate(900 200) rotate(-30)", rx="250", ry="100",
    ...   fill="none", stroke="blue"))
    >>> svg.add (Line (x1="100", y1="300", x2="300", y2="100"))
    >>> svg.add (Polyline
    ...   (fill="none", stroke="blue",
    ...   points="50,375 150,375 150,325 250,325 250,375 350,375 350,250 "
    ...   "450,250 450,375 550,375 550,175 650,175 650,375 750,375 750,100 "
    ...   "850,100 850,375 950,375 950,25 1050,25 1050,375 1150,375"))
    >>> svg.add (Polygon
    ...   (fill="red", stroke="blue", fill_opacity="0.5",
    ...   points="350,75  379,161 469,161 397,215 423,301 350,250 277,301 "
    ...   "303,215 231,161 321,161"))
    >>> svg.write_to_xml_stream ()
    <?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <!DOCTYPE svg PUBLIC
        "-//W3C//DTD SVG 1.1//EN"
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg height="4cm" version="1.1" viewBox="0 0 1200 400" width="12cm"
         xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink"
    >
      <rect fill="none" height="398" stroke="blue" width="1198" x="1" y="1"/>
      <rect fill="green" height="200" rx="50" width="400" x="100" y="100"/>
      <g id="1" transform="translate(700 210) rotate(-30)">
        <rect fill="none" height="200" rx="50" stroke="purple" width="400" x="0"
              y="0"
        />
      </g>
      <circle cx="600" cy="200" fill="red" r="100" stroke="blue"/>
      <ellipse fill="red" rx="250" ry="100"/>
      <ellipse fill="none" rx="250" ry="100" stroke="blue"
               transform="translate(900 200) rotate(-30)"
      />
      <line x1="100" x2="300" y1="300" y2="100"/>
      <polyline fill="none"
                points="50,375 150,375 150,325 250,325 250,375 350,375 350,250 450,250 450,375 550,375 550,175 650,175 650,375 750,375 750,100 850,100 850,375 950,375 950,25 1050,25 1050,375 1150,375"
                stroke="blue"
      />
      <polygon fill="red" fill-opacity="0.5"
               points="350,75  379,161 469,161 397,215 423,301 350,250 277,301 303,215 231,161 321,161"
               stroke="blue"
      />
    </svg>

    >>> svg_n = Root (view_box="10 60 450 260", width="100%", height="100%")
    >>> svg_n.write_to_xml_stream (output_width = 65)
    <svg height="100%" version="1.1" viewBox="10 60 450 260"
         width="100%" xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink"
    >
    </svg>

    >>> svg_x = Root (x_attrs = {})
    >>> svg_x.write_to_xml_stream (output_width = 65)
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg">
    </svg>

"""

from   _TFL                   import TFL

from   _TFL.Caller            import Scope
from   _TFL._SDG._XML.Cdata   import Cdata

import _TFL.Decorator
import _TFL._SDG._XML.Document
import _TFL._SDG._XML.Elem_Type
import _TFL._SDG._XML.Node
import _TFL._SDG._XML._SVG

TFL.SDG.XML.Node.attr_name_translate.update \
    ( alignment_baseline      = "alignment-baseline"
    , baseline_shift          = "baseline-shift"
    , base_profile            = "baseProfile"
    , clip_path               = "clip-path"
    , clip_rule               = "clip-rule"
    , dominant_baseline       = "dominant-baseline"
    , elid                    = "id"
    , fill_opacity            = "fill-opacity"
    , fill_rule               = "fill-rule"
    , font_family             = "font-family"
    , font_size               = "font-size"
    , font_stretch            = "font-stretch"
    , font_style              = "font-style"
    , font_variant            = "font-variant"
    , font_weight             = "font-weight"
    , klass                   = "class"
    , marker_end              = "marker-end"
    , marker_height           = "markerHeight"
    , marker_mid              = "marker-mid"
    , marker_start            = "marker-start"
    , marker_units            = "markerUnits"
    , marker_width            = "markerWidth"
    , path_length             = "pathLength"
    , preserve_aspect_ratio   = "preserveAspectRatio"
    , ref_x                   = "refX"
    , ref_y                   = "refY"
    , start_offset            = "startOffset"
    , stop_color              = "stop-color"
    , stroke_dasharray        = "stroke-dasharray"
    , stroke_dashoffset       = "stroke-dashoffset"
    , stroke_linecap          = "stroke-linecap"
    , stroke_linejoin         = "stroke-linejoin"
    , stroke_miterlimit       = "stroke-miterlimit"
    , stroke_opacity          = "stroke-opacity"
    , stroke_width            = "stroke-width"
    , text_anchor             = "text-anchor"
    , text_decoration         = "text-decoration"
    , vector_effect           = "vector-effect"
    , view_box                = "viewBox"
    , word_spacing            = "word-spacing"
    , xlink_href              = "xlink:href"
    , xlink_title             = "xlink:title"
    )

class _SVG_Document_ (TFL.SDG.XML.Document) :
    """Model a SVG document.

    >>> svg = Document (Root ())
    >>> svg.write_to_xml_stream ()
    <?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <!DOCTYPE svg PUBLIC
        "-//W3C//DTD SVG 1.1//EN"
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink"
    >
    </svg>
    >>> svg = Document (
    ...     Root (view_box="10 60 450 260", width="100%", height="100%"))
    >>> svg.write_to_xml_stream (output_width = 65)
    <?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <!DOCTYPE svg PUBLIC
        "-//W3C//DTD SVG 1.1//EN"
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg height="100%" version="1.1" viewBox="10 60 450 260"
         width="100%" xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink"
    >
    </svg>

    >>> svg = Document (
    ...     Root (view_box="10 60 450 260", width="100%", height="100%"))
    >>> styl = Style   ("rect { fill: yellow; stroke: blue; }")
    >>> defs = svg.add (Defs  (styl))
    >>> svg.write_to_xml_stream (output_width = 65)
    <?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <!DOCTYPE svg PUBLIC
        "-//W3C//DTD SVG 1.1//EN"
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg height="100%" version="1.1" viewBox="10 60 450 260"
         width="100%" xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink"
    >
      <defs>
        <style type="text/css">
          <![CDATA[
            rect { fill: yellow; stroke: blue; }
          ]]>
        </style>
      </defs>
    </svg>

    """

    _real_name           = "Document"

    init_arg_defaults    = dict \
        ( doctype        = TFL.SDG.XML.Doctype
            ( "svg"
            , dtd = TFL.SDG.XML.External_Id_Public
                ( "-//W3C//DTD SVG 1.1//EN"
                , "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"
                )
            )
        )

    _autoconvert         = dict \
        ( root_element   = lambda s, k, v
                         : s._convert (v, TFL.SDG.XML.SVG.Root)
        ,
        )

Document = _SVG_Document_ # end class _SVG_Document_

_marker_use_attr            = dict \
    ( marker_end            = None
    , marker_mid            = None
    , marker_start          = None
    )

_shape_attr                 = dict \
    ( clip_path             = None
    , clip_rule             = None
    , color                 = None
    , cursor                = None
    , display               = None
    , fill                  = None
    , fill_opacity          = None
    , fill_rule             = None
    , elid                  = None
    , klass                 = None
    , opacity               = None
    , stroke                = None
    , stroke_dasharray      = None
    , stroke_dashoffset     = None
    , stroke_linecap        = None
    , stroke_linejoin       = None
    , stroke_miterlimit     = None
    , stroke_opacity        = None
    , stroke_width          = None
    , style                 = None
    , transform             = None
    , vector_effect         = None
    , visibility            = None
    , x                     = None
    , y                     = None
    )

_text_attr                  = dict \
    ( alignment_baseline    = None
    , baseline_shift        = None
    , dominant_baseline     = None
    , dx                    = None
    , dy                    = None
    , font                  = None
    , font_family           = None
    , font_size             = None
    , font_stretch          = None
    , font_style            = None
    , font_variant          = None
    , font_weight           = None
    , rotate                = None
    , text_anchor           = None
    , text_decoration       = None
    , word_spacing          = None
    )

_shape_text_attr            = dict (_text_attr, ** _shape_attr)

_viewport_attr              = dict \
    ( clip                  = None
    , overflow              = None
    )

def _convert_view_box (self, k, value) :
    result = value
    if isinstance (value, (list, tuple)) :
        result = " ".join ("%s" % (x, ) for x in value)
    return result
# end def _convert_view_box

def _convert_points (self, k, value) :
    result = value
    if isinstance (value, (list, tuple)) :
        result = " ".join ("%s,%s" % (x, y) for x, y in value)
    return result
# end def _convert_points

def _convert_points_path (self, k, value) :
    result = value
    if isinstance (value, (list, tuple)) :
        close = value [-1] if value [-1] in ("z", "Z") else None
        x, y  = value [0]
        parts = ["M %s,%s" % (x, y)]
        parts.extend \
            (   "%s,%s" % (x, y)
            for x, y in (value [1:-1] if close else value [1:])
            )
        if close :
            parts.append (close)
        result = " ".join (parts)
    return result
# end def _convert_points_path

def _convert_style_sheet (self, k, value) :
    sheet = value
    if isinstance (value, (list, tuple)) :
        sheet = "\n".join ("%s" % (x, ) for x in value)
    result = sheet if isinstance (sheet, Cdata) else Cdata (sheet)
    return result
# end def _convert_style_sheet

Circle                      = TFL.SDG.XML.Elem_Type \
    ( "circle"
    , (TFL.SDG.XML.Empty, )
    , cx                    = None
    , cy                    = None
    , r                     = None
    , ** _shape_attr
    )

Defs                        = TFL.SDG.XML.Elem_Type \
    ( "defs"
    , ** _shape_text_attr
    )

Desc                        = TFL.SDG.XML.Elem_Type \
    ( "desc"
    , elid                  = None
    , klass                 = None
    , style                 = None
    )

Ellipse                     = TFL.SDG.XML.Elem_Type \
    ( "ellipse"
    , (TFL.SDG.XML.Empty, )
    , cx                    = None
    , cy                    = None
    , rx                    = None
    , ry                    = None
    , ** _shape_attr
    )

Gradient_Stop               = TFL.SDG.XML.Elem_Type \
    ( "stop"
    , (TFL.SDG.XML.Empty, )
    , offset                = None
    , stop_color            = None
    , stop_opacity          = None
    )

Group                       = TFL.SDG.XML.Elem_Type \
    ( "g"
    , ** _shape_text_attr
    )

Image                       = TFL.SDG.XML.Elem_Type \
    ( "image"
    , height                = None
    , preserve_aspect_ratio = None
    , width                 = None
    , xlink_href            = None
    , xlink_title           = None
    , ** dict (_shape_text_attr, ** _viewport_attr)
    )
Line                        = TFL.SDG.XML.Elem_Type \
    ( "line"
    , (TFL.SDG.XML.Empty, )
    , x1                    = None
    , x2                    = None
    , y1                    = None
    , y2                    = None
    , ** dict (_shape_attr, ** _marker_use_attr)
    )

Linear_Gradient             = TFL.SDG.XML.Elem_Type \
    ( "linearGradient"
    , elid                  = None
    , gradientTransform     = None
    , gradientUnits         = "userSpaceOnUse"
    , spreadMethod          = None
    , x1                    = None
    , x2                    = None
    , xlink_href            = None
    , y1                    = None
    , y2                    = None
    )

Marker                      = TFL.SDG.XML.Elem_Type \
    ( "marker"
    , marker_height         = None
    , marker_units          = None
    , marker_width          = None
    , orient                = None
    , preserve_aspect_ratio = None
    , ref_x                 = None
    , ref_y                 = None
    , view_box              = None
    , _autoconvert          = dict (view_box = _convert_view_box)
    , ** dict (_shape_attr, ** _viewport_attr)
    )

Path                        = TFL.SDG.XML.Elem_Type \
    ( "path"
    , d                     = None
    , path_length           = None
    , _autoconvert          = dict (d = _convert_points_path)
    , ** dict (_shape_attr, ** _marker_use_attr)
    )

Polygon                     = TFL.SDG.XML.Elem_Type \
    ( "polygon"
    , (TFL.SDG.XML.Empty, )
    , points                = None
    , _autoconvert          = dict (points = _convert_points)
    , ** dict (_shape_attr, ** _marker_use_attr)
    )

Polyline                    = TFL.SDG.XML.Elem_Type \
    ( "polyline"
    , (TFL.SDG.XML.Empty, )
    , points                = None
    , _autoconvert          = dict (points = _convert_points)
    , ** dict (_shape_attr, ** _marker_use_attr)
    )

Radial_Gradient             = TFL.SDG.XML.Elem_Type \
    ( "radialGradient"
    , cx                    = None
    , cy                    = None
    , elid                  = None
    , fx                    = None
    , fy                    = None
    , gradientTransform     = None
    , gradientUnits         = "userSpaceOnUse"
    , r                     = None
    , spreadMethod          = None
    , xlink_href            = None
    )

Rect                        = TFL.SDG.XML.Elem_Type \
    ( "rect"
    , (TFL.SDG.XML.Empty, )
    , height                = None
    , rx                    = None
    , ry                    = None
    , width                 = None
    , ** _shape_attr
    )

Root                        = TFL.SDG.XML.Elem_Type \
    ( "svg"
    , base_profile          = None
    , height                = None
    , init_arg_defaults     = dict
        (x_attrs            = { "xmlns:xlink" : "http://www.w3.org/1999/xlink"})
    , klass                 = None
    , preserve_aspect_ratio = None
    , version               = "1.1"
    , view_box              = None
    , width                 = None
    , xmlns                 = "http://www.w3.org/2000/svg"
    , x                     = None
    , y                     = None
    , _autoconvert          = dict (view_box = _convert_view_box)
    , ** _viewport_attr
    )

Style                       = TFL.SDG.XML.Elem_Type \
    ( "style"
    , type                  = "text/css"
    , _autoconvert          = dict (children = _convert_style_sheet)
    )

### nested `svg` element
SVG                         = TFL.SDG.XML.Elem_Type \
    ( "svg"
    , height                = None
    , preserve_aspect_ratio = None
    , view_box              = None
    , width                 = None
    , _autoconvert          = dict (view_box = _convert_view_box)
    , ** dict (_shape_text_attr, ** _viewport_attr)
    )

Symbol                      = TFL.SDG.XML.Elem_Type \
    ( "symbol"
    , preserve_aspect_ratio = None
    , view_box              = None
    , _autoconvert          = dict (view_box = _convert_view_box)
    , ** dict (_shape_text_attr, ** _viewport_attr)
    )

Text                        = TFL.SDG.XML.Elem_Type \
    ( "text"
    , bases                 = (TFL.SDG.XML.Element_Compact, )
    , ** _shape_text_attr
    )

Text_Path                   = TFL.SDG.XML.Elem_Type \
    ( "textPath"
    , bases                 = (TFL.SDG.XML.Element_Compact, )
    , method                = None
    , start_offset          = None
    , xlink_href            = None
    , ** _shape_text_attr
    )

Title                       = TFL.SDG.XML.Elem_Type \
    ( "title"
    , bases                 = (TFL.SDG.XML.Element_Compact, )
        ### Element_Compact forces 1-line XML output for title
        ### to avoid leading whitespace in browser display of title text
    , elid                  = None
    , klass                 = None
    , style                 = None
    )

Tref                        = TFL.SDG.XML.Elem_Type \
    ( "tref"
    , xlink_href            = None
    )

Tspan                       = TFL.SDG.XML.Elem_Type \
    ( "tspan"
    , ** _shape_text_attr
    )

Use                         = TFL.SDG.XML.Elem_Type \
    ( "use"
    , height                = None
    , href                  = None
    , width                 = None
    , xlink_href            = None
    , ** _shape_text_attr
    )

@TFL.Add_New_Method (Marker, decorator = classmethod)
def Arrow_Head (cls, elid = "SVG:Arrow_Head", design_size = 10, ref_x = None, stroke = "black", marker_height = 3, marker_width = 3, ** kw) :
    """Return a marker that is an arrow head.

    >>> mrk = Marker.Arrow_Head ()

    >>> svg = Document (Root (view_box="0 0 1000 500"))
    >>> svg.add (Defs (mrk))
    >>> svg.add (Rect (x = 5, y = 5, width = 990, height = 490, fill = "none", stroke = "orange", stroke_width = 5))
    >>> svg.add (Path (fill = "none", stroke = "red", stroke_width = 25, marker_end = "url(#SVG:Arrow_Head)", d = "M 100 200 500 200 900 400"))
    >>> svg.add (Path (fill = "none", stroke = "blue", stroke_width =10, marker_start = "url(#SVG:Arrow_Head)", d = "M 100 100 500 100 900 50"))
    >>> svg.write_to_xml_stream ()
    <?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <!DOCTYPE svg PUBLIC
        "-//W3C//DTD SVG 1.1//EN"
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg version="1.1" viewBox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink"
    >
      <defs>
        <marker id="SVG:Arrow_Head" fill="none" markerHeight="3"
                markerUnits="strokeWidth" markerWidth="3" orient="auto"
                refX="10" refY="5" stroke="black" viewBox="0 0 10 10"
        >
          <path d="M 0,0 10,5 0,2 z">
          </path>
          <path d="M 0,10 10,5 0,8 z">
          </path>
        </marker>
      </defs>
      <rect fill="none" height="490" stroke="orange" stroke-width="5"
            width="990" x="5" y="5"
      />
      <path d="M 100 200 500 200 900 400" fill="none"
            marker-end="url(#SVG:Arrow_Head)" stroke="red" stroke-width="25"
      >
      </path>
      <path d="M 100 100 500 100 900 50" fill="none"
            marker-start="url(#SVG:Arrow_Head)" stroke="blue" stroke-width="10"
      >
      </path>
    </svg>

    """
    size   = design_size
    size_2 = size // 2
    scope  = Scope ()
    if ref_x is None :
        ref_x = size
    result = cls \
        ( Path (d = ((0, 0),    (size, size_2), (0, 2),        "z"))
        , Path (d = ((0, size), (size, size_2), (0, size - 2), "z"))
        , elid          = elid
        , fill          = "none"
        , marker_units  = "strokeWidth"
        , marker_height = marker_height
        , marker_width  = marker_width
        , orient        = "auto"
        , ref_x         = ref_x
        , ref_y         = size_2
        , stroke        = stroke
        , view_box      = (0, 0, size, size)
        , ** kw
        )
    return result
# end def Arrow_Head

@TFL.Add_New_Method (Marker, decorator = classmethod)
def Arrow_Head_A (cls, elid = "SVG:Arrow_Head_A", design_size = 12, ref_x = None, stroke = "black", marker_height = 6, marker_width = 6, fill = "white", fill_opacity = 1,  ** kw) :
    """Return a marker that is an arrow head with an A-Shape.

    >>> mrk = Marker.Arrow_Head_A ()

    >>> svg = Document (Root (view_box="0 0 1000 500"))
    >>> svg.add (Defs (mrk))
    >>> svg.add (Rect (x = 5, y = 5, width = 990, height = 490, fill = "none", stroke = "orange", stroke_width = 5))
    >>> svg.add (Path (fill = "none", stroke = "red", stroke_width = 25, marker_end = "url(#SVG:Arrow_Head_A)", d = "M 100 200 500 200 900 400"))
    >>> svg.add (Path (fill = "none", stroke = "blue", stroke_width =10, marker_start = "url(#SVG:Arrow_Head_A)", d = "M 100 100 500 100 900 50"))
    >>> svg.write_to_xml_stream ()
    <?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <!DOCTYPE svg PUBLIC
        "-//W3C//DTD SVG 1.1//EN"
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg version="1.1" viewBox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink"
    >
      <defs>
        <marker id="SVG:Arrow_Head_A" fill="none" markerHeight="6"
                markerUnits="strokeWidth" markerWidth="6" orient="auto" refX="0"
                refY="6" stroke="black" viewBox="0 0 12 12"
        >
          <path d="m 0,9.0 0,-6.0 6.0,3.0 -6.0,3.0 z" fill="white"
                fill-opacity="1" stroke="none"
          >
          </path>
          <path d="m 0,9.0 5.0,-3.0 -5.0,-3.0">
          </path>
          <path d="m 2.0,4.0 0,4.0">
          </path>
        </marker>
      </defs>
      <rect fill="none" height="490" stroke="orange" stroke-width="5"
            width="990" x="5" y="5"
      />
      <path d="M 100 200 500 200 900 400" fill="none"
            marker-end="url(#SVG:Arrow_Head_A)" stroke="red" stroke-width="25"
      >
      </path>
      <path d="M 100 100 500 100 900 50" fill="none"
            marker-start="url(#SVG:Arrow_Head_A)" stroke="blue"
            stroke-width="10"
      >
      </path>
    </svg>

    """
    # modifying design size will draw with different line-strength
    # compared to the shape
    size   = design_size
    size_2 = size // 2
    scope  = Scope ()
    if ref_x is None :
        ref_x = 0
    result = cls \
        ( Path
            ( d = "m %s,%s 0,%s %s,%s %s,%s z" %
                ( 0
                , size * 3 / 4.
                , -(size / 2.)
                , size / 2.
                , size / 4.
                , -(size / 2.)
                , size / 4.
                )
            , fill         = fill
            , fill_opacity = fill_opacity
            , stroke       = "none"
            )
        , Path
            ( d = "m %s,%s %s,%s %s,%s" %
                ( 0
                , size * 3 / 4.
                , size * 5 / 12.
                , -(size / 4.)
                , -(size * 5 / 12.)
                , -(size / 4.)
                )
            )
        , Path
            ( d = "m %s,%s 0,%s" %
                ( size / 6.
                , size / 3.
                , size / 3.
                )
            )
        , elid          = elid
        , fill          = "none"
        , marker_units  = "strokeWidth"
        , marker_height = marker_height
        , marker_width  = marker_width
        , orient        = "auto"
        , ref_x         = ref_x
        , ref_y         = size_2
        , stroke        = stroke
        , view_box      = (0, 0, size, size)
        , ** kw
        )
    return result
# end def Arrow_Head_A

@TFL.Add_New_Method (Marker, decorator = classmethod)
def Arrow_Head_Bar (cls, elid = "SVG:Arrow_Head_Bar", design_size = 70, fill = "white", fill_opacity = 1, ref_x = None, stroke = "black", stroke_opacity = 1, size = 9, marker_height = 9, marker_width = 9, ** kw) :
    """Return a marker that is an arrow head with a background bar.

    >>> mrk = Marker.Arrow_Head_Bar ()

    >>> svg = Document (Root (view_box="0 0 1000 500"))
    >>> svg.add (Defs (mrk))
    >>> svg.add (Rect (x = 5, y = 5, width = 990, height = 490, fill = "none", stroke = "orange", stroke_width = 5))
    >>> svg.add (Path (fill = "none", stroke = "red", stroke_width = 25, marker_end = "url(#SVG:Arrow_Head_Bar)", d = "M 100 200 L 500 200 900 400"))
    >>> svg.add (Path (fill = "none", stroke = "blue", stroke_width =10, marker_start = "url(#SVG:Arrow_Head_Bar)", d = "M 100 100 L 500 100 900 50"))
    >>> svg.write_to_xml_stream ()
    <?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <!DOCTYPE svg PUBLIC
        "-//W3C//DTD SVG 1.1//EN"
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg version="1.1" viewBox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink"
    >
      <defs>
        <marker id="SVG:Arrow_Head_Bar" fill="none" markerHeight="9"
                markerUnits="strokeWidth" markerWidth="9" orient="auto" refX="0"
                refY="35" stroke="black" viewBox="0 0 70 70"
        >
          <path d="m 0,0 0,70 25.0,-15.0 0,-40.0 -25.0,-15.0 z" fill="black"
                fill-opacity="1" stroke="none"
          >
          </path>
          <path d="m 35.0,20.0 0,30.0 25.0,-15.0 -25.0,-15.0 z" fill="black"
                fill-opacity="1" stroke="none"
          >
          </path>
          <path d="m 25.0,15.0 10.0,5.0 0,30.0 -10.0,5.0 0,-40.0 z" fill="white"
                fill-opacity="1" stroke="none"
          >
          </path>
        </marker>
      </defs>
      <rect fill="none" height="490" stroke="orange" stroke-width="5"
            width="990" x="5" y="5"
      />
      <path d="M 100 200 L 500 200 900 400" fill="none"
            marker-end="url(#SVG:Arrow_Head_Bar)" stroke="red" stroke-width="25"
      >
      </path>
      <path d="M 100 100 L 500 100 900 50" fill="none"
            marker-start="url(#SVG:Arrow_Head_Bar)" stroke="blue"
            stroke-width="10"
      >
      </path>
    </svg>

    """
    size   = design_size
    size_2 = size // 2
    scope  = Scope ()
    if ref_x is None :
        ref_x = 0
    result = cls \
        ( Path
            ( d = "m 0,0 0,%s %s,%s 0,%s %s,%s z" %
                ( size
                , size / 70. * 25.
                , -(size / 70. * 15.)
                , -(size / 70. * 40.)
                , -(size / 70. * 25.)
                , -(size / 70. * 15.)
                )
            , fill         = stroke
            , fill_opacity = stroke_opacity
            , stroke       = "none"
            )
        , Path
            ( d = "m %s,%s 0,%s %s,%s %s,%s z" %
                ( size /  2.
                , size /  7. * 2.
                , size / 70. * 30.
                , size / 70. * 25.
                , -(size / 70. * 15.)
                , -(size / 70. * 25.)
                , -(size / 70. * 15.)
                )
            , fill         = stroke
            , fill_opacity = stroke_opacity
            , stroke       = "none"
            )
        , Path
            ( d = "m %s,%s %s,%s 0,%s %s,%s 0,%s z" %
                ( size / 14. * 5.
                , size / 14. * 3.
                , size /  7.
                , size / 14.
                , size /  7. * 3.
                , -(size / 7.)
                , size / 14.
                , -(size / 7. * 4.)
                )
            , fill         = fill
            , fill_opacity = fill_opacity
            , stroke       = "none"
            )
        , elid          = elid
        , fill          = "none"
        , marker_units  = "strokeWidth"
        , marker_height = marker_height
        , marker_width  = marker_width
        , orient        = "auto"
        , ref_x         = ref_x
        , ref_y         = size_2
        , stroke        = stroke
        , view_box      = (0, 0, size, size)
        , ** kw
        )
    return result
# end def Arrow_Head_Bar

@TFL.Add_New_Method (Marker, decorator = classmethod)
def Plug (cls, elid = "SVG:Plug", size = 2, stroke = "black", marker_height = 3, marker_width = 3, ** kw) :
    """Return a marker that is a plug.

    >>> mrk = Marker.Plug ()
    >>> svg = Document (Root (view_box="0 0 1000 500"))
    >>> svg.add (Defs (mrk))
    >>> svg.add (Rect (x = 5, y = 5, width = 990, height = 490, fill = "none", stroke = "orange", stroke_width = 5))
    >>> svg.add (Path (fill = "none", stroke = "red", stroke_width = 25, marker_start = "url(#SVG:Plug)", d = "M 100 200 L 500 200 900 400"))
    >>> svg.add (Path (fill = "none", stroke = "blue", stroke_width =10, marker_start = "url(#SVG:Plug)", d = "M 100 100 L 500 100 900 50"))
    >>> svg.add (Path (fill = "none", stroke = "blue", stroke_width = 2, marker_start = "url(#SVG:Plug)", d = "M 100 150 L 200 150 400 100"))
    >>> svg.write_to_xml_stream ()
    <?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <!DOCTYPE svg PUBLIC
        "-//W3C//DTD SVG 1.1//EN"
        "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg version="1.1" viewBox="0 0 1000 500" xmlns="http://www.w3.org/2000/svg"
         xmlns:xlink="http://www.w3.org/1999/xlink"
    >
      <defs>
        <marker id="SVG:Plug" fill="none" markerHeight="3"
                markerUnits="strokeWidth" markerWidth="3" orient="auto" refX="0"
                refY="2" stroke="black" viewBox="0 0 4 4"
        >
          <path d="M 4 0 L 0 0  0 4  4 4">
          </path>
        </marker>
      </defs>
      <rect fill="none" height="490" stroke="orange" stroke-width="5"
            width="990" x="5" y="5"
      />
      <path d="M 100 200 L 500 200 900 400" fill="none"
            marker-start="url(#SVG:Plug)" stroke="red" stroke-width="25"
      >
      </path>
      <path d="M 100 100 L 500 100 900 50" fill="none"
            marker-start="url(#SVG:Plug)" stroke="blue" stroke-width="10"
      >
      </path>
      <path d="M 100 150 L 200 150 400 100" fill="none"
            marker-start="url(#SVG:Plug)" stroke="blue" stroke-width="2"
      >
      </path>
    </svg>

    """
    size2  = size * 2
    scope  = Scope ()
    result = cls \
        ( Path
            ( d = "M %(size2)s 0 "
                  "L 0 0  0 %(size2)s  %(size2)s %(size2)s"
                % scope
            )
        , elid          = elid
        , fill          = "none"
        , marker_units  = "strokeWidth"
        , marker_height = marker_height
        , marker_width  = marker_width
        , orient        = "auto"
        , ref_x         = 0
        , ref_y         = size
        , stroke        = stroke
        , view_box      = (0, 0, size2, size2)
        , ** kw
        )
    return result
# end def Plug

if __name__ != "__main__" :
    TFL.SDG.XML.SVG._Export ("*")
### __END__ TFL.SDG.XML.SVG.Document
