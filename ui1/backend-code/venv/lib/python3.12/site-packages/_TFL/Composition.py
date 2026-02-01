# -*- coding: utf-8 -*-
# Copyright (C) 2000-2009 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Composition
#
# Purpose
#    Function composition
#
# Revision Dates
#    19-Apr-2000 (CT)  Creation
#    25-May-2004 (CED) Doctest added
#    30-Oct-2006 (CED) Moved to TFL
#    ««revision-date»»···
#--

from _TFL        import TFL

class Composition :
    """Functor for composing two functions:

       >>> c = Composition (outer = lambda x : x * 2, inner = lambda x : x + 5)
       >>> c (1)
       12
    """

    def __init__ (self, outer, inner) :
        self.outer = outer
        self.inner = inner
    # end def __init__

    def __call__ (self, * args, ** kw) :
        return self.outer (self.inner (* args, ** kw))
    # end def __call__

# end class Composition

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Composition
