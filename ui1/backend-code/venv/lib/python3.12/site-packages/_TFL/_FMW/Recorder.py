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
#    TFL.FMW.Recorder
#
# Purpose
#    Model wrapper for functions and methods
#
# Revision Dates
#    22-Sep-2004 (CT) Creation
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    ««revision-date»»···
#--



from   _TFL                   import TFL
import _TFL._FMW.Wrapper
import _TFL._Meta.Object

import sys

class File_Recorder (TFL.Meta.Object) :
    """Record wrapper calls into a file"""

    def __init__ (self, file = None, format = None) :
        self.file   = file
        if format is not None :
            self.format = format
    # end def __init__

    def record (self, ** kw) :
        file = self.file or sys.stdout
        file.write (self.format % kw)
    # end def record

# end class File_Recorder

class Dict_Recorder (TFL.Meta.Object) :
    """Record wrapper calls into a dictionary"""

    def __init__ (self) :
        self.dict = {}
    # end def __init__

    def record (self, ** kw) :
        self.dict.setdefault (kw ["wrapper"].name, []).append (kw)
    # end def record

# end class Dict_Recorder

class Wrapped_Recorder (TFL.FMW.Wrapped_FM) :
    """Wrapper recording execution of a single function or method"""

    def __init__ (self, * args, ** kw) :
        try :
            self.recorder = kw ["recorder"]
        except KeyError :
            self.recorder = self.Default_Recorder ()
        else :
            del kw ["recorder"]
        self.__super.__init__ (* args, ** kw)
    # end def __init__

# end class Wrapped_Recorder

if __name__ != "__main__" :
    TFL.FMW._Export ("*")
### __END__ TFL.FMW.Recorder
