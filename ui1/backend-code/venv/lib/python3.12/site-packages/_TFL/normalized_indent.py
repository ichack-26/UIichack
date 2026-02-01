# -*- coding: utf-8 -*-
# Copyright (C) 2005-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    normalized_indent
#
# Purpose
#    Return string with normalized indentation
#
# Revision Dates
#    14-Mar-2005 (CT) Creation
#     6-Jul-2005 (CT) Doctest moved from function `normalized_indent` to
#                     module (and another case added)
#     6-Jul-2005 (CT) `textwrap.dedent` used if available
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

"""
>>> print (normalized_indent ("Just a single line."))
Just a single line.
>>> print (":", normalized_indent ("  Just a single line inside white space.  "), ":", sep = "")
:Just a single line inside white space.:
>>> print (_normalized_indent ('''First line.
...     Second line.
...     Third line.
...         Fourth line (indented).
...         Fifth line (ditto).
...     Sixth line.
... '''))
First line.
Second line.
Third line.
    Fourth line (indented).
    Fifth line (ditto).
Sixth line.
>>> print ( normalized_indent ('''
...     First line.
...     Second line.
...     Third line.
...         Fourth line (indented).
...         Fifth line (ditto).
...     Sixth line.
... '''))
First line.
Second line.
Third line.
    Fourth line (indented).
    Fifth line (ditto).
Sixth line.
>>> print (normalized_indent ('''
...         First line.
...     Second line.
...     Third line.
...         Fourth line (indented).
...         Fifth line (ditto).
...     Sixth line.
...
... '''))
First line.
Second line.
Third line.
    Fourth line (indented).
    Fifth line (ditto).
Sixth line.
>>> print (normalized_indent ('''
...  First line.
...     Second line.
...     Third line.
...         Fourth line (indented).
...         Fifth line (ditto).
...     Sixth line.
...
... '''))
First line.
Second line.
Third line.
    Fourth line (indented).
    Fifth line (ditto).
Sixth line.
"""

from   _TFL import TFL

def _normalized_indent (text) :
    """Returns `text` with normalized indentation."""
    lines = text.strip ().split ("\n")
    head  = lines [0]
    rest  = lines [1:]
    if rest :
        indent = 0
        for line in rest :
            contents = line.lstrip ()
            if contents :
                indent = len (line) - len (contents)
                break
        if indent :
            lines = [head] + [line [indent:] for line in rest]
    return "\n".join (lines)
# end def _normalized_indent

try :
    from textwrap import dedent as _dedent
except ImportError :
    normalized_indent = _normalized_indent
else :
    def normalized_indent (text) :
        """Returns `text` with normalized indentation."""
        lines  = text.strip ().split ("\n", 1)
        result = lines [0]
        rest   = lines [1:]
        if rest :
            result = "\n".join ((result, _dedent (rest [0])))
        return result
    # end def normalized_indent

if __name__ != "__main__" :
    TFL._Export ("normalized_indent")
### __END__ normalized_indent
