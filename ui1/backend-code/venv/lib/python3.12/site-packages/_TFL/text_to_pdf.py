# -*- coding: utf-8 -*-
# Copyright (C) 2020-2022 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.text_to_pdf
#
# Purpose
#    Convert text file to pdf format using reportlab
#
# Revision Dates
#     3-Jun-2020 (CT) Creation
#    25-Jun-2020 (CT) Add module docstring
#    28-Jun-2020 (CT) Add support for `rows`
#     2-May-2021 (CT) Add function `create_file`
#    20-Jun-2022 (CT) Add macOS specific default for `display_program`
#    23-Oct-2022 (CT) Add `Subtitle` and `Extra_Info`
#    ««revision-date»»···
#--

"""
`TFL.text_to_pdf` converts plain text files, i.e., text files without
markup, to files in PDF format and optionally displays them or sends
them to a printer.

The conversion is similar to what the Unix programs `a2ps` and `enscript`
do, but supports unicode, provided the specified font supports all tbe
characters used in the input files.

The command ::

    python -m _TFL.text_to_pdf -help=details

explains the structure of the PDF generated and the options for
pagination, headers, and footers.

The command ::

    python -m _TFL.text_to_pdf -help=opts

explains the possible command options and their possible values and
defaults.

The option `-a2ps` results in output very similar to that of `a2ps`.

`TFL.text_to_pdf` assumes a fixed-width font for the body of the PDF
document; a variable-width font will not look good.

Option values can be specified on the command line or in
config files. A config file contains lines of the form::

    option = value

without leading white space. `value` must be given in valid Python
syntax. A config file can also include another config file like this::

    load_config ("<name-of--other-config-file")

The command ::

    python -m _TFL.text_to_pdf -help=config

explains the syntax and semantics of config files.

"""

_doc_page_structure = """
A PDF document has physical pages; a physical page comprises one or
more virtual pages arranged in columns and/or rows.

A text document is a series of lines comprising text without markup.
Formfeed characters in the text document can indicate page breaks.

`<VT><FF>` in a text document marks a strict page break that will start
a new physical page in the PDF document. `<FF>` marks a page break that
will start a new virtual page in the PDF document. `<VT>` marks a
conditional page break — if there are less than `-vt_limit` lines left
on the current virtual page.

Virtual pages can be further split into new virtual pages if they
contain more lines than fit into a single virtual page.

Each physical page of a PDF document comprises three parts: `header`,
`body`, and `footer`::

  +-------------------------------------------------------------------+
  |                                                                   |
  |   header-left             header-middle            header-right   |
  |   =============================================================   |
  |                                                                   |
  |   body line 1                     body line n+1                   |
  |   .                               .                               |
  |   .                               .                               |
  |   .                               .                               |
  |   body line n                     body line n+n                   |
  |                                                                   |
  |   $l#                             $l#                             |
  |   _____________________________________________________________   |
  |   footer-left             footer-middle            footer-right   |
  |                                                                   |
  +-------------------------------------------------------------------+

`$l#` is only displayed for non-cutable multi-column/row PDF documents
and shows the number of the current virtual page and the total number of
virtual pages, e.g, `3/42`.

In case of a cutable multi-column/row PDF document, each virtual page
will have its own `header` and `footer`.

The `left`, `middle`, and `right` components of `header` and `footer`
can be specified on the command line as by specifying a pattern of the
form `<left>|<middle>|<right>` for the options `-header` and `-footer`.

For example:

  -header 'Literal string for left|$t|:'
  -footer 'left footer value|right footer value'

Besides literal values, the following special values for `<left>`,
`<middle>`, and `<right>` are supported:

  ==========  =========================================================
  Specifier   Meaning
  ==========  =========================================================
    :         Default for the component (might be empty, see below)
    $b        Basename of the file containing the text document
    $c        Time of creation of PDF document
    $m        Time of last modification of the text document
    $n        Full name of the file containing the text document
    $p        Number of current page
    $p#       Number of current page and total number of pages
    $s        Subject
    $t        Title
    $u        Subtitle
    $x        Extra_Info
  ==========  =========================================================

The one-character `$` values can be combined, e.g., `$tsn`; the first
non-empty values will be used for the component, i.e., `$tsn` is
equivalent to `$t or $s or $n`.

  ================  ===================================================
  Component         Default meaning of `:`
  ================  ===================================================
  header-left       $t if defined, otherwise $n
  header-middle     $s
  header-right      $p#
  footer-left       $b if $t is defined, otherwise empty
  footer-middle     $m
  footer-right      $c
  ================  ===================================================

The option `-show_options` can be used to show the actually chosen
values  for the `header` and `footer` components for a specific
command invocation.

"""

from   _TFL                      import TFL

from   _TFL                      import sos
from   _TFL.Filename             import Filename
from   _TFL.predicate            import split_hst
from   _TFL.pyk                  import pyk
from   _TFL.Record               import Record
from   _TFL.Regexp               import Regexp, Re_Replacer, re, Untabified
from   _TFL.User_Config          import user_config

import _TFL.Command
import _TFL.Decorator
import _TFL._Meta.Object

from   reportlab.pdfgen.canvas   import Canvas
from   reportlab.lib             import pagesizes, units
from   reportlab.pdfbase         import pdfmetrics
from   reportlab.pdfbase.ttfonts import TTFont

import subprocess
import sys
import reportlab.lib.pagesizes
import time

is_macOS_p = "Darwin" == subprocess.run \
    (["uname"], capture_output = True, text = True).stdout.strip ()

media   = {k : ps for k, ps in pagesizes.__dict__.items () if k.isupper ()}

_2equal_sign_pat    = Regexp ("={2,}")
_4equal_sign_pat    = Regexp ("={4,}")
_minus_sign_pat     = Regexp ("-{4,}")
_underscore_pat     = Regexp ("_{3,}")
_underline_pat      = Regexp ("(?:.\b_)+")

class Color (TFL.Meta.Object) :

    black       = 0.000, 0.000, 0.000
    gray_10     = 0.100, 0.100, 0.100
    gray_20     = 0.200, 0.200, 0.200
    gray_30     = 0.300, 0.300, 0.300
    gray_40     = 0.400, 0.400, 0.400
    gray_50     = 0.500, 0.500, 0.500
    gray_60     = 0.600, 0.600, 0.600
    gray_70     = 0.700, 0.700, 0.700
    blue        = 0.285, 0.668, 0.902
    orange      = 1.000, 0.627, 0.133

# end class Color

class _Font_Family_ (TFL.Meta.Object) :

    Table           = dict \
        ( Courier               = Record
            ( body              = "Courier"
            , footer            = "Courier"
            , header            = "Courier"
            , overflow_symbol   = "···"
            )
        , Dejavu                = Record
            ( body              = "DejaVuSansMono.ttf"
            , footer            = "DejaVuSansMono.ttf"
            , header            = "DejaVuSansMono-Bold.ttf"
            , overflow_symbol   = "\u2026"
            )
        , JetBrainsMono = Record
            ( body              = "JetBrainsMono-Medium.ttf"
            , footer            = "JetBrainsMono-Medium.ttf"
            , header            = "JetBrainsMono-Bold.ttf"
            , overflow_symbol   = "\u2026"
            )
        )

    def __getitem__ (self, key) :
        try :
            result  = self.Table [key]
        except KeyError :
            ### assume that it's a font available in system fonts
            result  = Record \
                ( body              = key
                , footer            = key
                , header            = key
                , overflow_symbol   = "···"
                )
        return result
    # end def __getitem__

Font_Family = _Font_Family_ () # end class _Font_Family_

class Margins (TFL.Meta.Object) :

    def __init__ (self, left, right, top, bottom) :
        self.left   = left
        self.right  = right
        self.top    = top
        self.bottom = bottom
        self._tuple = (left, right, top, bottom)
    # end def __init__

    @property
    def horizontal (self) :
        return self.left + self.right
    # end def horizontal

    @property
    def vertical (self) :
        return self.top + self.bottom
    # end def vertical

    def __getitem__ (self, index) :
        return self._tuple [index]
    # end def __getitem__

    def __iter__ (self) :
        return iter (self._tuple)
    # end def __iter__

    def __repr__ (self) :
        return str (self._tuple)
    # end def __repr__

# end class Margins

class Page_Strict (TFL.Meta.Object) :
    """Model a strict page of a `PDF_Doc`.

    A strict page always starts in the left-most column of a physical page.

    A strict page exceeding the maximum lines per v_page `lpv`, will
    be split into several virtual pages; if the number of resulting
    virtual pages is larger than the number of virtual pages `vpp` per
    physical page, the strict page will by split into several physical
    pages.
    """

    def __init__ (self, txt) :
        self.txt = txt
    # end def __init__

    def pages (self, vpp, lpv, vt_limit = 5) :
        def _gen_vps (m_pages, lpv) :
            for mp in m_pages :
                lines   = mp.lstrip ("\v\n").rstrip ().split ("\n")
                l       = len (lines)
                if not l :
                    yield [""]
                else :
                    h   = 0
                    while h < l :
                        while h < l and not lines [h].strip () :
                            h += 1
                        t = h + lpv
                        try :
                            v = lines.index ("\v", t - vt_limit, t)
                        except ValueError :
                            pass
                        else :
                            t = v
                        col = lines [h:t]
                        if col :
                            yield col
                        h = t
        def _gen_pages (vps, vpp) :
            l   = len (vps)
            h   = 0
            while h < l :
                yield vps [h:h+vpp]
                h  += vpp
        m_pages     = self.txt.split ("\f")
        vps         = list (_gen_vps  (m_pages, lpv))
        return _gen_pages  (vps, vpp)
    # end def pages

# end class Page_Strict

class PDF_Doc (TFL.Meta.Object) :
    """PDF document generator: convert plain old text documents to PDF."""

    _font_cache     = {}

    _replacements   = \
        [ Record
            ( guard         = _4equal_sign_pat
            , pat           = _2equal_sign_pat
            , lh_off        = 0.25
            , line_color    = Color.gray_70
            , line_width    = 1.5
            )
        , Record
            ( guard         = None
            , pat           = _minus_sign_pat
            , lh_off        = 0.25
            , line_color    = Color.gray_50
            , line_width    = 0.75
            )
        , Record
            ( guard         = None
            , pat           = _underscore_pat
            , lh_off        = 0.0
            , line_color    = Color.gray_20
            , line_width    = 0.9
            )
        ]

    def __init__ \
            ( self, txt, output
            , body_color        = None
            , columns_per_page  = 1
            , cutable           = False
            , font_family       = "Courier"
            , font_size         = 12.0
            , footer_color      = None
            , footer_fields     = ("", "", "")
            , footer_font_size  = None
            , header_color      = None
            , header_fields     = ("", "", "$p#")
            , header_font_size  = 14.4
            , landscape         = False
            , line_height       = 14.0
            , margins           = [36] * 4
            , page_compression  = True
            , page_size         = media ["A4"]
            , rows_per_page     = 1
            , subject           = None
            , subtitle          = None
            , title             = None
            , vt_limit          = 5
            , extra_info        = None
            ) :
        self.txt                = txt
        self.output             = output
        self.body_color         = body_color or Color.gray_10
        self.columns_per_page   = columns_per_page
        self.cutable            = cutable
        self.font_family        = Font_Family [font_family]
        self.footer_color       = footer_color or Color.gray_50
        self.footer_fields      = footer_fields
        self.footer_font        = self._pdf_font (self.font_family.footer)
        self.footer_font_size   = footer_font_size \
            or min (font_size, header_font_size) * 0.8
        self.footer_p           = any (f.strip () for f in footer_fields)
        self.font               = self._pdf_font (self.font_family.body)
        self.font_size          = font_size
        self.header_color       = header_color or Color.gray_40
        self.header_fields      = header_fields
        self.header_font        = self._pdf_font (self.font_family.header)
        self.header_font_size   = header_font_size
        self.landscape          = landscape
        self.line_height        = line_height
        self.margins            = margins
        self.page_compression   = page_compression
        self.rows_per_page      = rows_per_page
        self.subject            = subject
        self.subtitle           = subtitle
        self.title              = title
        self.vt_limit           = vt_limit
        self.extra_info         = extra_info
        page_size               = \
            ( reportlab.lib.pagesizes.landscape if landscape else
                reportlab.lib.pagesizes.portrait
            ) (page_size)
        self.page_size          = (page_width, page_height) = page_size
        self.page_width         = page_width
        self.page_height        = page_height
        self.canvas             = canvas = self._canvas (output, page_size)
        self.char_width         = canvas.stringWidth ("M", self.font, font_size)
        self._setup_v_pages \
            ( columns_per_page, rows_per_page
            , page_height, page_width, line_height, margins
            )
        self._generate ()
    # end def __init__

    @TFL.Meta.Once_Property
    def footer_callables (self) :
        return self._hf_callables (self.footer_fields)
    # end def footer_callables

    @TFL.Meta.Once_Property
    def header_callables (self) :
        return self._hf_callables (self.header_fields)
    # end def header_callables

    def _add_footer (self, box, canvas, np, nop) :
        if self.footer_p :
            with self._footer_context (canvas) :
                f_bot   = box.bottom - 1.2 * self.line_height
                l_bot   = box.bottom - 0.3 * self.line_height
                self._add_page_hf \
                    (box, self.footer_callables, canvas, f_bot, np, nop)
                canvas.line (box.left, l_bot, box.right, l_bot)
    # end def _add_footer

    def _add_header (self, box, canvas, np, nop) :
        with self._header_context (canvas) :
            h_top = box.top + 2.0 * self.line_height
            l_top = box.top + 1.5 * self.line_height
            self._add_page_hf \
                (box, self.header_callables, canvas, h_top, np, nop)
            canvas.line (box.left, l_top, box.right, l_top)
    # end def _add_header

    def _add_line (self, canvas, col, line, txt_obj, cpl) :
        cw  = self.char_width
        pat = _underline_pat
        while pat.search (line) :
            l       = line.replace ("\b_", "")
            ps      = min (pat.start (0),                    cpl)
            pf      = min (ps + (len (line) - len (l)) // 2, cpl)
            left    = col.left + cw * ps
            right   = col.left + cw * pf
            y       = txt_obj._y - 2
            with self._underline_context (canvas, 0.25, Color.gray_50) :
                canvas.line (left, y, right, y)
            line    = l
        for rep in self._replacements :
            line    = self._add_line_replaced \
                (rep, canvas, col, line, txt_obj, cpl, cw)
        if line == "\v" :
            line = ""
        elif len (line) > cpl :
            line = line [:cpl] + self.font_family.overflow_symbol
        txt_obj.textLine (line)
    # end def _add_line

    def _add_line_replaced (self, rep, canvas, col, line, txt_obj, cpl, cw) :
        if rep.guard is None or rep.guard.search (line) :
            pat = rep.pat
            lh  = self.line_height
            y   = txt_obj._y + (lh * rep.lh_off)
            while pat.search (line) :
                nc      = len (pat.group (0))
                ps      = min (pat.start (0), cpl)
                pf      = min (ps + nc,       cpl)
                left    = col.left + cw * ps
                right   = col.left + cw * pf
                with self._underline_context \
                         (canvas, rep.line_width, rep.line_color) :
                    canvas.line (left, y, right, y)
                line    = pat.sub (" " * nc, line, 1)
        return line
    # end def _add_line_replaced

    def _add_page (self, canvas, page, np, nop, nc, noc) :
        vps_p   = len (self.v_pages) > 1 and noc > 1
        cutable = self.cutable
        if not cutable :
            self._add_header (self, canvas, np, nop)
            self._add_footer (self, canvas, np, nop)
        for vp, lines in zip (self.v_pages, page) :
            if cutable :
                self._add_header (vp, canvas, nc, noc)
                self._add_footer (vp, canvas, nc, noc)
            cpl = vp.chars_per_line
            with self._text_context (canvas, vp.left, vp.top) as txt_obj :
                for line in lines :
                    self._add_line  (canvas, vp, line, txt_obj, cpl)
            if vps_p and not cutable :
                with self._footer_context (canvas) :
                    nc_total = self._hf_number_total (nc, noc)
                    canvas.drawString (vp.left, self.bottom, nc_total)
            nc += 1
        canvas.showPage ()
    # end def _add_page

    def _add_page_hf (self, box, callables, canvas, y, np, nop) :
        lc, mc, rc  = callables
        if lc is not None :
            canvas.drawString        (box.left,   y, lc (np, nop))
        if mc is not None :
            canvas.drawCentredString (box.middle, y, mc (np, nop))
        if rc is not None :
            canvas.drawRightString   (box.right,  y, rc (np, nop))
    # end def _add_page_hf

    def _canvas (self, output, page_size) :
        result = Canvas \
            ( output
            , initialFontName        = self.header_font
            , initialFontSize        = self.header_font_size
            , pagesize               = page_size
            , pageCompression        = self.page_compression
            )
        if self.subject :
            result.setSubject    (self.subject)
        if self.title :
            result.setTitle      (self.title)
        result.setLineWidth      (0.05)
        result.setStrokeColorRGB (* self.body_color)
        result.setFillColorRGB   (* self.body_color)
        return result
    # end def _canvas

    @TFL.Contextmanager
    def _footer_context (self, canvas) :
        canvas.saveState ()
        try :
            canvas.setFont           (self.footer_font, self.footer_font_size)
            canvas.setLineWidth      (0.2)
            canvas.setFillColorRGB   (* self.footer_color)
            canvas.setStrokeColorRGB (* self.footer_color)
            yield
        finally :
            canvas.restoreState ()
    # end def _footer_context

    def _generate (self) :
        canvas  = self.canvas
        pages   = list (self._generate_pages ())
        nop     = self.number_of_pages   = len (pages)
        noc     = self.number_of_columns = sum (len (p) for p in pages)
        nc      = 1
        for np, page in enumerate (pages, 1) :
            if page :
                self._add_page (canvas, page, np, nop, nc, noc)
                nc += len (page)
        canvas.save ()
    # end def _generate

    def _generate_pages (self) :
        lpv         = self.lines_per_v_page
        vpp         = self.v_pages_per_page
        vt_limit    = self.vt_limit
        s_pages     = (Page_Strict (txt) for txt in self.txt.split ("\v\f"))
        for sp in s_pages :
            yield from sp.pages (vpp, lpv, vt_limit)
    # end def _generate_pages

    @TFL.Contextmanager
    def _header_context (self, canvas) :
        canvas.saveState ()
        try :
            canvas.setFont           (self.header_font, self.header_font_size)
            canvas.setLineWidth      (0.3)
            canvas.setFillColorRGB   (* self.header_color)
            canvas.setStrokeColorRGB (* self.header_color)
            yield
        finally :
            canvas.restoreState ()
    # end def _header_context

    def _hf_callables (self, fields) :
        def _gen () :
            map = \
                { "$p"    : self._hf_number
                , "$p#"   : self._hf_number_total
                }
            for f in fields :
                try :
                    c = map [f]
                except KeyError :
                    if f :
                        def c (i, nop, f = f) :
                            return f
                    else :
                        c = None
                yield c
        return tuple (_gen ())
    # end def _hf_callables

    def _hf_number (self, i, nop) :
        return str (i)
    # end def _hf_number

    def _hf_number_total (self, np, nop) :
        return "%d/%d" % (np, nop)
    # end def _hf_number_total

    def _pdf_font (self, font_name) :
        if font_name in ("Helvetica", "Courier", "Times Roman") :
            result = font_name
        else :
            cache  = self._font_cache
            result = Filename (font_name).base
            if result not in cache :
                cache [result] = font = TTFont (result, font_name)
                pdfmetrics.registerFont (font)
        return result
    # end def _pdf_font

    def _setup_v_pages (self, cpp, rpp, page_ht, page_wd, line_ht, margins) :
        vpp     = self.v_pages_per_page = cpp * rpp
        hf_corr = (2.5 + line_ht / margins.bottom) if self.footer_p else 0
        vp_ht   = page_ht / rpp
        vp_wd   = page_wd / cpp
        content_width   = vp_wd - margins.horizontal
        if self.cutable :
            content_height  = vp_ht     - margins.vertical * 1.5
        else :
            if rpp > 1 :
                vp_ht       = (page_ht  - margins.bottom) / rpp
            content_height  = vp_ht     - margins.top
            if cpp > 1 :
                vp_wd       = (page_wd  - margins.right)  / cpp
                content_width   = vp_wd - margins.left
        self.lines_per_v_page   = int \
            ((vp_ht - margins.vertical - hf_corr * line_ht) / line_ht)
        self.left   = margins.left
        self.right  = page_wd - margins.right
        self.middle = (self.right - self.left) / 2
        self.top    = page_ht - margins.top - 2 * line_ht
        self.bottom = margins.bottom
        chars_per_line  = int (content_width // self.char_width)
        self.v_pages    = tuple \
            ( Record
                ( chars_per_line = chars_per_line
                , content_height = content_height
                , content_width  = content_width
                , left           = margins.left + vp_wd * i
                , top            =
                    self.top - vp_ht * j - (line_ht if j else 0)
                )
            for i in range (cpp)
              for j in range (rpp)
            )
        for vp in self.v_pages :
            vp.bottom = vp.top  - content_height
            vp.right  = vp.left + content_width
            vp.middle = (vp.right - vp.left) / 2
    # end def _setup_v_pages

    @TFL.Contextmanager
    def _text_context (self, canvas, left, top) :
        canvas.saveState ()
        try :
            txt_obj = canvas.beginText (left, top)
            txt_obj.setFont \
                (self.font, self.font_size, leading = self.line_height)
            yield txt_obj
            canvas.drawText (txt_obj)
        finally :
            canvas.restoreState ()
    # end def _text_context

    @TFL.Contextmanager
    def _underline_context \
            (self, canvas, line_width = 0.1, color = Color.gray_50) :
        canvas.saveState ()
        try :
            canvas.setLineWidth      (line_width)
            canvas.setStrokeColorRGB (* color)
            yield
        finally :
            canvas.restoreState ()
    # end def _underline_context

# end class PDF_Doc

class TTP_Command (TFL.Command.Root_Command) :
    """Command converting text file(s) to pdf format using reportlab."""

    _rn_prefix              = "TTP_"

    explanation             = _doc_page_structure
    min_args                = 1
    time_fmt                = "%Y/%m/%d %H:%M"

    colors                  = \
        { c for c in Color.__dict__ if not c.startswith ("_") }

    _defaults               = dict \
        ( Baselineskip          = 1
        , columns               = 1
        , display_program       = "open" if is_macOS_p else "atril"
        , Body_color            = "black"
        , Font_Family           = "Courier"
        , font_size             = 11
        , footer                = "||:"
        , Footer_color          = "gray_20"
        , Footer_size_factor    = 0.8
        , header                = ":|:|:"
        , Header_color          = "gray_20"
        , Header_size_factor    = 1.0
        , margins               = "36:36:36:36"
        , medium                = "A4"
        , printer_name          = sos.environ.get ("PRINTER", "lp")
        , print_program         = "lp"
        , rows                  = 1
        , time_format           = time_fmt
        , vt_limit              = 5
        )

    _opts                   = \
        ( "-Baselineskip:F?Baselineskip in PostScript points"
        , "-columns:I?Number of columns per page"
        , "-Cutable:B?Allow columns to be cut into independent pages"
        , "-Display:B"
              "?Display pdf output with program by -display_program"
        , "-display_program:S"
        , "-Extra_Info:S"
            "?Extra information about the document that can be "
            "displayed in the header of footer"
        , "-Font_Family:S"
              "?Font family to use for body of pdf document "
              "(must be fixed width)"
        , "-font_size:F?Font size in points"
        , "-footer:U?Footer to use for each page"
            " (see `-help=details` for explanation)"
        , "-Footer_size_factor:F"
            "?Footer font size = font_size * Footer_size_factor"
        , "-Header_size_factor:F"
            "?Header font size = font_size * Header_size_factor"
        , "-header:U?Header to use for each page"
            " (see `-help=details` for explanation)"
        , "-landscape:B?Use landscape instead of portrait orientation"
        , "-margins:I:#4?Page margins in points for LEFT:RIGHT:TOP:BOTTOM"
        , "-Print:B?Print the file(s)"
        , "-printer_name:S?Name of printer to print to"
        , "-print_program:S"
        , "-purge_pdf:B?Remove pdf output file after displaying or printing"
        , "-rows:I?Number of rows per page"
        , "-Output:Q?Write output to specified file"
        , "-show_options:B?Show option values passed to pdf-converter"
        , "-Subject:S?Subject of document"
        , "-Subtitle:S?Subtitle of document"
        , "-time_format:S?Format used for time header"
        , "-Title:S?Title of document"
        , "-verbose:B"
        , "-vt_limit:I"
            "?Vertical tab will trigger page break it is closer than "
            "`vt_limit` to the end of a page/column"
        , TFL.CAO.Opt.Input_Encoding ()
        , TFL.CAO.Opt.Config_Bundle
            ( name          = "a2ps"
            , description   =
                "Set of option values to create PDF files resembling the "
                "style of the `a2ps` command"
            , config_dct    = dict
                ( Baselineskip  = 0.3
                , columns       = 2
                , Cutable       = True
                , Font_Family   = "Courier"
                , font_size     = "6.8"
                , footer        = " "
                , header        = "$m|$tsn|$p"
                , landscape     = True
                , margins       = "15:15:36:30"
                )
            )
        , TFL.CAO.Opt.Set
            ( name          = "Body_color"
            , description   = "Color used for page body"
            , choices       = colors
            )
        , TFL.CAO.Opt.Config_Bundle
            ( name          = "Courier"
            , description   = "Use font family Courier"
            , config_dct    = dict
                ( Font_Family   = "Courier"
                , Body_color    = "black"
                , Footer_color  = "gray_20"
                , Header_color  = "gray_20"
                )
            )
        , TFL.CAO.Opt.Config_Bundle
            ( name          = "Dejavu"
            , description   = "Use font family DejaVu"
            , config_dct    = dict
                ( Font_Family   = "Dejavu"
                , Body_color    = "black"
                , Footer_color  = "gray_20"
                , Header_color  = "gray_20"
                )
            )
        , TFL.CAO.Opt.Set
            ( name          = "Footer_color"
            , description   = "Color used for page footer"
            , choices       = colors
            )
        , TFL.CAO.Opt.Set
            ( name          = "Header_color"
            , description   = "Color used for page header"
            , choices       = colors
            )
        , TFL.CAO.Opt.Config_Bundle
            ( name          = "Jetbrainsmono"
            , description   = "Use font family JetBrainsMono"
            , config_dct    = dict
                ( Font_Family   = "JetBrainsMono"
                , Body_color    = "gray_20"
                , Footer_color  = "gray_40"
                , Header_color  = "gray_40"
                )
            )
        , TFL.CAO.Opt.Key
            ( name          = "medium"
            , description   = "Medium used for output"
            , dct           = media
            )
        )

    class Config_Dirs (TFL.Command.Root_Command.Config_Dirs) :

        _defaults           = ("~/", "./")

    # end class Config_Dirs

    class Config (TFL.Command.Root_Command.Config) :

        _default            = ".text_to_pdf"

    # end class Config

    def handler (self, cmd) :
        i_enc       = cmd.input_encoding
        tfmt        = self.time_fmt = cmd.time_format
        for arg in cmd.argv :
            if arg == "-" :
                arg = "STDIN"
            output = Filename (".pdf", cmd.Output or arg).name
            if arg == "STDIN" :
                file_time   = time.localtime ()
                fn          = output
                txt_in      = sys.stdin.read ()
            else :
                file_time   = time.localtime (sos.path.getmtime (arg))
                fn          = self._display_filename (cmd, arg)
                with open (arg, "rb") as fi :
                    txt_in  = fi.read ()
            txt     = Untabified \
                (pyk.decoded    (txt_in, i_enc).lstrip ("\n\f").rstrip ())
            ft      = time.strftime  (tfmt, file_time)
            options = self._pdf_opts (cmd, arg, fn, ft, output)
            if cmd.show_options :
                from   _TFL.formatted_repr import formatted_repr
                print (formatted_repr (options))
            ofn     = options ["output"]
            pdf_doc = PDF_Doc (txt, ** options)
            if cmd.Display :
                subprocess.run ([cmd.display_program, ofn])
            elif cmd.Print :
                subprocess.run ([cmd.print_program,   ofn])
            if cmd.purge_pdf and (cmd.Display or cmd.Print) :
                sos.unlink (ofn)
            elif cmd.verbose :
                print ("Created file", ofn)
    # end def handler

    def _display_filename (self, cmd, arg) :
        result  = Filename (arg).relative_to ("~/")
        if result != arg :
            result = "~/" + result
        return result
    # end def _display_filename

    def _fields__gen \
            ( self, l, m, r, file_name, file_time
            , subject, subtitle, title, extra_info, now
            ) :
        def resolved (x) :
            result = None
            if x == "b" :
                result = Filename (file_name).base
            elif x == "c" :
                result = now
            elif x == "m" :
                result = file_time
            elif x == "n" :
                result = file_name
            elif x == "s" :
                result = subject
            elif x == "t" :
                result = title
            elif x == "u" :
                result = subtitle
            elif x == "x" :
                result = extra_info
            return result
        for x in (l, m, r) :
            r = None
            if x.startswith ("$") and not x.endswith ("#") :
                for y in x [1:] :
                    r = resolved (y)
                    if r :
                        break
            yield r or x
    # end def _fields__gen

    def _footer_fields \
            ( self, footer, file_name, file_time
            , subject, subtitle, title, extra_info, now
            ) :
        l, m, r  = "", "", ""
        if footer.strip () :
            l, _, x = split_hst (footer, "|")
            if _ :
                m, _, r = split_hst (x,  "|")
                if m and not _ :
                    m, r = r, m
            l, m, r = tuple \
                ( self._fields__gen
                    ( l, m, r, file_name, file_time
                    , subject, subtitle, title, extra_info, now
                    )
                )
        return \
            ( l if l != ":" else (Filename (file_name).base if title else "")
            , m if m != ":" else file_time
            , r if r != ":" else now
            )
    # end def _footer_fields

    def _header_fields \
            ( self, header, file_name, file_time
            , subject, subtitle, title, extra_info, now
            ) :
        l, m, r  = "", "", ""
        if header.strip () :
            l, _, x = split_hst (header, "|")
            if _ :
                m, _, r = split_hst (x,  "|")
                if m and not _ :
                    m, r = r, m
            l, m, r = tuple \
                ( self._fields__gen
                    ( l, m, r, file_name, file_time
                    , subject, subtitle, title, extra_info, now
                    )
                )
        return \
            ( l if l != ":" else (title or file_name)
            , m if m != ":" else subject
            , r if r != ":" else "$p#"
            )
    # end def _header_fields

    def _margins (self, margins) :
        if not margins :
            margins = [0] * 4
        else :
            l = len (margins)
            if l == 1 :
                margins = margins * 4
            elif l == 2 :
                margins = margins [:1] * 2 + margins [1:] * 2
            elif l == 3 :
                margins.append (margins [-1])
        return Margins (* margins)
    # end def _margins

    def _pdf_opts (self, cmd, fn, display_fn, ft, output) :
        ff          = cmd.Font_Family
        fs          = cmd.font_size
        hfs         = fs * cmd.Header_size_factor
        ffs         = fs * cmd.Footer_size_factor
        now         = time.strftime (self.time_fmt, time.localtime ())
        subject     = cmd.Subject     or ""
        subtitle    = cmd.Subtitle    or ""
        title       = cmd.Title       or ""
        extra_info  = cmd.Extra_Info  or ""
        result      = dict \
            ( body_color        = getattr (Color, cmd.Body_color, None)
            , columns_per_page  = cmd.columns
            , cutable           = cmd.Cutable
            , font_family       = ff
            , font_size         = fs
            , footer_color      = getattr (Color, cmd.Footer_color, None)
            , footer_fields     = self._footer_fields
                ( cmd.footer, display_fn, ft
                , subject, subtitle, title, extra_info, now
                )
            , footer_font_size  = ffs
            , header_color      = getattr (Color, cmd.Header_color, None)
            , header_fields     = self._header_fields
                ( cmd.header, display_fn, ft
                , subject, subtitle, title, extra_info, now
                )
            , header_font_size  = hfs
            , landscape         = cmd.landscape
            , line_height       = fs + cmd.Baselineskip
            , margins           = self._margins (cmd.margins)
            , output            = output
            , page_size         = cmd.medium
            , rows_per_page     = cmd.rows
            , subject           = subject
            , title             = title
            , vt_limit          = cmd.vt_limit
            )
        return result
    # end def _pdf_opts

Command = TTP_Command # end class

def create_file (contents, filename, * pdf_options) :
    """Create a pdf-file of `contents` with name `filename`."""
    tn  = Filename (".pdf", filename).name
    cmd = [sys.executable, "-m", "_TFL.text_to_pdf", "-Output='%s'" % tn] \
        + list (pdf_options) + ["STDIN"]
    subprocess.run \
        ( cmd
        , encoding = "utf-8"
        , env      = dict (sos.environ)
        , input    = contents
        )
    return tn
# end def create_file

if __name__ != "__main__" :
    TFL._Export_Module ()
if __name__ == "__main__" :
    Command () ()
### __END__ TFL.text_to_pdf
