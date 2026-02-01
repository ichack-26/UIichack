# -*- coding: utf-8 -*-
# Copyright (C) 2004-2014 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.tex_quoted
#
# Purpose
#    Quote TeX-critical characters
#
# Revision Dates
#    29-Jan-2004 (CT)  Creation
#    11-May-2004 (RMA) Added tex_quoted_no_underscore and
#                      tex_quoted_underscore_word_with_path
#    01-Jun-2004 (RMA) Added {} to word boundaries to fix
#                      tex_quoted_underscore_word_with_path
#    ««revision-date»»
#--

from   _TFL                     import TFL
from   _TFL.pyk                 import pyk
from   _TFL.Regexp              import Regexp, re

_tex_pi_symbols = Regexp (r"[«»]", re.X)
_tex_to_quote   = Regexp (r"([\\#~%&${}^])", re.X)
_tex_underscore = Regexp (r"([_])", re.X)
_tex_tt_symbols = Regexp (r"[<>+*|]", re.X)
_tex_diacritics = Regexp (r"[äöüÄÖÜß«»]")

_word_boundaries= "[^ ()}{,\t\n\r\f\v]"

_tex_path_text  = Regexp \
    (r"(%s*?[_]%s*)"  % (_word_boundaries, _word_boundaries), re.X)

def _tex_subs_pi_symbols (match) :
    m = match.group (0)
    i = {"«" : 225, "»" : 241} [m]
    return r"\Pisymbol{psy}{%d}" % (i, )
# end def _tex_subs_pi_symbols

def _tex_subs_to_quote (match) :
    return r"\texttt{\%s}" % (match.group (0), )
# end def _tex_subs_to_quote

def _tex_subs_tt_symbols (match) :
    return r"\texttt{%s}" % (match.group (0), )
# end def _tex_subs_tt_symbols

def _tex_subs_diacritics (match) :
    m = match.group (0)
    return { "ä" : r"""\"a""", "Ä" : r"""\"A"""
           , "ö" : r"""\"o""", "Ö" : r"""\"O"""
           , "ü" : r"""\"u""", "Ü" : r"""\"U"""
           , "ß" : r"""\"s"""
           }.get (m, m)
# end def _tex_subs_diacritics

def _tex_subs_to_path (match) :
    return r"{\small\path|%s|}" % (match.group (0), )
# end def _tex_subs_to_path

def tex_quoted (s) :
    """Return `s` with all TeX-critical characters quoted in some adequate,
       if ugly, way.
    """
    s = tex_quoted_no_underscore (s)
    if isinstance (s, pyk.string_types) :
        s = _tex_underscore.sub   (_tex_subs_to_quote,   s)
    return s
# end def tex_quoted

def tex_quoted_no_underscore (s) :
    """Same as tex_quoted but does NOT quote underscores.
    """
    if isinstance (s, pyk.string_types) :
        s = _tex_pi_symbols.sub (_tex_subs_pi_symbols, s)
        s = _tex_to_quote.sub   (_tex_subs_to_quote,   s)
        s = _tex_tt_symbols.sub (_tex_subs_tt_symbols, s)
        s = _tex_diacritics.sub (_tex_subs_diacritics, s)
    return s
# end def tex_quoted_no_underscore

def tex_quoted_underscore_word_with_path (s) :
    if isinstance (s, pyk.string_types) :
        s = _tex_path_text.sub (_tex_subs_to_path, s)
    return s
# end def tex_quoted_underscore_word_with_path

if __name__ != "__main__" :
    TFL._Export ("tex_quoted")
### __END__ TFL.tex_quoted
