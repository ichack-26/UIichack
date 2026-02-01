# -*- coding: utf-8 -*-
# Copyright (C) 2000-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Function
#
# Purpose
#    Encapsulate function into callable object
#
# Revision Dates
#    16-May-2000 (CT) Creation
#    22-Sep-2000 (CT) Set `__name__'
#    19-Jun-2001 (CT) Assign to `self.__call__' in `__init__' instead of
#                     defining `__call__' as method
#     3-Oct-2001 (CT) `__deepcopy__` added
#     3-Oct-2001 (CT) `_Function_` factored
#    23-Sep-2004 (CT) `_Function_.__getattr__` added to make wrapped
#                     callables more similar to the real thing (e.g., avoid
#                     an AttributeError from `wrapped.func_code`)
#    14-Feb-2006 (CT) Moved into package `TFL`
#    14-Feb-2006 (CT) `_Function_` unfactored (`Function` was empty)
#    21-Feb-2008 (MG) `__init__`: use getattr chain to handle all sorts of
#                     callables as `function`
#    15-Apr-2008 (MG) `function` class attribute added (needed for unpickling)
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL             import TFL

class Function :

    function = None ### needed to be able to unpickle a Function instance

    def __init__ (self, function, _doc = None) :
        self.function = function
        self.__name__ = getattr \
            (function, "__name__", getattr (function, "name", repr (function)))
        self.__doc__  = _doc or function.__doc__
    # end def __init__

    def __deepcopy__ (self, memo_dict) :
        return self.__class__ (self.function, self.__doc__)
    # end def __getstate__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return getattr (self.function, name)
    # end def __getattr__

    def __repr__ (self) :
        return "<%s %s at %x>" % \
            (self.__class__.__name__, self.__name__, id (self.function))
    # end def __repr__

    def __str__ (self) :
        return self.__name__
    # end def __str__

# end class Function

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Function
