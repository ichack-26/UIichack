# -*- coding: utf-8 -*-
# Copyright (C) 2005-2014 DI Christian Eder <eder@tttech.com>
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Py_Interpreter
#
# Purpose
#    Provides classes and functions to access the python interpreter
#
# Revision Dates
#     8-Mar-2005 (CED) Creation (moved multiple implemented stuff into here)
#     9-Jun-2005 (CED) `locals` added to `__call__`
#    25-Jul-2005 (CT)  `__call__` fixed (`or {}` considered harmful)
#    25-Jul-2007 (PGO) Reduced not-invented-here-ness
#    ««revision-date»»···
#--

from   _TFL                    import TFL
from   _TFL.predicate          import *

import rlcompleter

class Pycode_Compiler (object) :
    """A class to eval/exec python code lines."""

    def __init__ (self, s) :
        lines = s.split ("\n")
        if len (lines) <= 1 :
            self.src = s
        else :
            self.src  = "\n".join (lines) + "\n"
        try :
            self.code     = compile (self.src, "<stdin>", "eval")
            self.can_eval = True
        except SyntaxError :
            self.code     = compile (self.src, "<stdin>", "exec")
            self.can_eval = False
    # end def __init__

    def __call__ (self, glob_dct, loc_dct = None) :
        if loc_dct is None :
            loc_dct = {}
        if self.can_eval :
            print (eval (self.code, glob_dct, loc_dct))
        else :
            exec (self.code, glob_dct, loc_dct)
    # end def __call__

# end class Pycode_Compiler

def complete_command (line, glob_dct, loc_dct = None) :
    prefix, space, line = line.rpartition       (" ")
    d                   = dict (glob_dct)
    d.update (loc_dct or {})
    c                   = rlcompleter.Completer (d)
    try :
        c.complete (line, 0)
    except Exception :
        return None, None
    match = "".join ((prefix, space, common_head (c.matches)))
    cands = ", ".join (sorted (s.split (".") [-1] for s in set (c.matches)))
    return match, ("%s\n\n" % cands if cands else "")
# end def complete_command

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ Py_Interpreter
