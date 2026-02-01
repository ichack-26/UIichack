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
#    swap_2strings
#
# Purpose
#    Swap all occurences of two strings in some text
#
# Revision Dates
#    26-Jan-2002 (CT) Creation
#    20-Aug-2003 (CT) s/\n/\\n/ to avoid
#                         `ValueError: inconsistent leading whitespace`
#                     from the $%&@*$ doc-test
#    16-Jun-2013 (CT) Use `TFL.CAO`, not `TFL.Command_Line`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL.Regexp import *

import _TFL.CAO

class String_Swapper :
    """Swaps all occurences of two strings in some text"""

    def __init__ (self, s1, s2) :
        self.s1   = s1
        self.s2   = s2
        self._map = { s1 : s2, s2 : s1 }
        self._pat = Regexp ("(%s|%s)" % (re.escape (s1), re.escape (s2)))
    # end def __init__

    def __call__ (self, text) :
        """Swap all occurences of `self.s1` and `self.s2` in `text`"""
        return self._pat.sub (self._replace, text)
    # end def __call__

    def _replace (self, match) :
        return self._map [match.group (1)]
    # end def _replace

# end class String_Swapper

def swap_2strings (s1, s2, text) :
    """Swap all occurences of `s1` and `s2` in `text`

       >>> print (swap_2strings ("a", "b", "ab" * 5))
       bababababa
       >>> print (swap_2strings ("sda", "sdb", "/dev/sda1 /  \\n/dev/sdb1 /alt  "))
       /dev/sdb1 /
       /dev/sda1 /alt
       >>> print (swap_2strings ("sda", "sdb", "/dev/sda2 /b \\n/dev/sdb2 /alt/b"))
       /dev/sdb2 /b
       /dev/sda2 /alt/b
    """
    return String_Swapper (s1, s2) (text)
# end def swap_2strings

def _main (cmd) :
    import sys
    print (swap_2strings (cmd.s1, cmd.s2, sys.stdin.read ()), end="")
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler       = _main
    , args          =
        ( "s1:S"
        , "s2:S"
        )
    , min_args      = 2
    , max_args      = 2
    )

if __name__ == "__main__" :
    _Command ()
### __END__ swap_2strings
