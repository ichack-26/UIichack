# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.r_eval
#
# Purpose
#    Restricted `eval`
#
# Revision Dates
#     7-Jun-2012 (CT) Creation
#     8-Jun-2012 (CT) Add `\s*` to `_eval_restrict_pat`
#     6-Jun-2013 (CT) Change guard to `isinstance (source, pyk.string_types)`
#     4-Dec-2013 (CT) Remove `coding` cookie from unicode values
#     9-May-2017 (CT) Make Python-3 compatible for both `str` and `bytes`
#    ««revision-date»»···
#--

from   _TFL               import TFL
from   _TFL.portable_repr import portable_repr
from   _TFL.pyk           import pyk

import re

_coding_pat        = re.compile \
    ( br"^# *(-\*-)?\s*coding[:=]\s*(?P<enc>[-a-zA-Z0-9]+) *(-\*-)? *" + b"\n"
    , re.MULTILINE
    )

_eval_restrict_pat = re.compile \
    ( pyk.decoded
        (r"(?: (?: ^|\W)(?: lambda)(?: \W|$))|\.\s*__|(?: ^|\W)inspect\.")
    , re.VERBOSE
    )

def r_eval (source, ** kw) :
    """Evaluate `source`, in a scope with values of `kw`, but nothing else.

    >>> r_eval ("2 * 2")
    4
    >>> r_eval (u"2 * 2")
    4
    >>> r_eval (b"2 * 2")
    4
    >>> r_eval ("dir ()")
    Traceback (most recent call last):
    ...
    NameError: name 'dir' is not defined
    >>> r_eval ("dir ()", dir = dir)
    ['__builtins__', 'dir']
    >>> r_eval ("type (())")
    Traceback (most recent call last):
    ...
    NameError: name 'type' is not defined
    >>> r_eval ("lambda : 5")
    Traceback (most recent call last):
    ...
    ValueError: Cannot safely evaluate 'lambda : 5'
    >>> r_eval ("().__class__")
    Traceback (most recent call last):
    ...
    ValueError: Cannot safely evaluate '().__class__'
    >>> r_eval ("((). __class__)")
    Traceback (most recent call last):
    ValueError: Cannot safely evaluate '((). __class__)'
    """
    if isinstance (source, str) :
        src     = source
    else :
        c_match = _coding_pat.search (source)
        enc     = (c_match.group ("enc"), ) if c_match else ()
        src     = _coding_pat.sub ("", source, 1)
        src     = pyk.decoded (src, * enc)
    if _eval_restrict_pat.search (src) :
        raise ValueError ("Cannot safely evaluate %r" % (source [:60], ))
    scope = dict (kw, __builtins__ = {})
    return eval (src, scope)
# end def r_eval

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.r_eval
