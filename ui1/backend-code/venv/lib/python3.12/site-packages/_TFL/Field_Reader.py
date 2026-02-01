# -*- coding: utf-8 -*-
# Copyright (C) 2002-2004 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Field_Reader
#
# Purpose
#    Read and convert fields from the next line of a file
#
# Revision Dates
#    25-May-2002 (CT) Creation
#    28-Sep-2004 (CT) Use `isinstance` instead of type comparison
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    ««revision-date»»···
#--



import sys

class Field_Reader :
    """Read and convert fields from the next line of a file"""

    def __init__ (self, * field_types, ** kw) :
        self.field_types = field_types
        self._file       = kw.get ("file",      sys.stdin)
        splitargs        = kw.get ("splitargs", ())
        if isinstance (splitargs, str) :
            splitargs    = (splitargs, )
        self.splitargs   = splitargs
    # end def __init__

    def __call__ (self) :
        fields = self._file.readline ().split (* self.splitargs)
        return [c (f) for (c,f) in zip (self.field_types, fields)]
    # end def __call__
# end class Field_Reader

from _TFL import TFL
TFL._Export ("Field_Reader")

### __END__ Field_Reader
