# -*- coding: utf-8 -*-
# Copyright (C) 2000-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Black_Hole
#
# Purpose
#    Provides class taking all function calls and attribute accesses thrown at
#    it and ignores them
#
# Revision Dates
#    16-Aug-2000 (CT) Creation
#    11-Feb-2006 (CT) Moved into package `TFL`
#    19-Apr-2020 (CT)  Use "``" for doc strings, not "`'"
#    ««revision-date»»···
#--

from   _TFL                import TFL
from   _TFL.pyk            import pyk

class _Black_Hole_ :
    """Takes all function calls and attribute accesses thrown at it and
       ignores them.

       Don't try too apply `dir` to `black_hole` -- it will die slowly.

       `__coerce__` is needed to allow comparisons and the use of
       `black_hole` with unary and binary operators.

    """

    def __init__    (s, * args, ** kw) : pass
    def __call__    (s, * args, ** kw) : return s
    def __bool__    (s)                : return False
    def __coerce__  (s, o)             : return s, s
    def __eq__      (s, o)             : return False
    def __getattr__ (s, n)             : return s
    def __ge__      (s, o)             : return False
    def __gt__      (s, o)             : return False
    def __hash__    (s)                : return 0
    def __len__     (s)                : return 0
    def __le__      (s, o)             : return False
    def __lt__      (s, o)             : return False
    def __ne__      (s, o)             : return False
    def __repr__    (s)                : return "<_Black_Hole_ at %s>" % id (s)
    def __str__     (s)                : return ""

# end class _Black_Hole_

black_hole = _Black_Hole_ ()

if __name__ != "__main__" :
    TFL._Export ("black_hole", "_Black_Hole_")
### __END__ TFL.Black_Hole
