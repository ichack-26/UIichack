# -*- coding: utf-8 -*-
# Copyright (C) 2004 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.FMW.Tracer
#
# Purpose
#    Provide tracing wrapper for methods and functions without changing the
#    source code of the traced components
#
# Revision Dates
#    22-Sep-2004 (CT) Creation
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    ««revision-date»»···
#--



from   _TFL                   import TFL
import _TFL._FMW.Recorder
import _TFL._FMW.Wrapper

class Trace_Recorder_F (TFL.FMW.File_Recorder) :
    """Record trace information into a file"""

    format = \
        ( "%(indent)s%(wrapper)s"
          "\n%(indent)s    %(args)s, %(kw)s\n"
        )

# end class Trace_Recorder_F

class Traced (TFL.FMW.Wrapped_Recorder) :
    """Tracer of execution of a single function or method without changing the
       source code of the measured component.
    """

    Default_Recorder = Trace_Recorder_F
    level            = 0

    def __call__ (self, * args, ** kw) :
        indent = ". " * self.level
        self.recorder.record \
            ( wrapper   = self
            , args      = args + self.args
            , kw        = dict (kw, ** self.kw)
            , indent    = indent
            )
        self.__class__.level += 1
        try :
            result = self.fct (* args, ** kw)
        finally :
            self.__class__.level -= 1
        return result
    # end def __call__

# end class Traced

class Tracer (TFL.FMW.Wrapper) :
    """Trace execution of functions and methods without changing the
       source code of the measured components."""

    Wrapped_FM = Traced

# end class Tracer

if __name__ != "__main__" :
    TFL.FMW._Export ("*")
### __END__ TFL.FMW.Tracer
