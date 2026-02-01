# -*- coding: utf-8 -*-
# Copyright (C) 2004-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.FMW.Wrapper
#
# Purpose
#    Model wrapper for functions and methods
#
# Revision Dates
#    22-Sep-2004 (CT) Creation
#    23-Sep-2004 (CT) Protect access to `func_code.co_flags` to allow any
#                     callable to be wrapped without AttributeErrors
#    23-Sep-2004 (CT) `_Wrapped_.__getattr__` added to make wrapped
#                     callables more similar to the real thing (e.g., avoid
#                     an AttributeError from `wrapped.func_code`)
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   _TFL                   import TFL
from   _TFL.pyk               import pyk

import _TFL._FMW
import _TFL._Meta.Object

CO_GENERATOR = 0x0020 ### stolen from python/Include/compile.h

class _Wrapped_ (TFL.Meta.Object) :
    """Wrapped function/method/generator."""

    def __init__ (self, __name__, name, fct, * args, ** kw) :
        self.__name__ = __name__
        self.__doc__  = getattr (fct, "__doc__", None)
        self.name     = name
        self.fct      = fct
        self.args     = args
        self.kw       = kw
    # end def __init__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return getattr (self.fct, name)
    # end def __getattr__

    def __repr__ (self) :
        return "<%s for %r>" % (self.__class__.__name__, self.fct)
    # end def __repr__

    def __str__ (self) :
        return self.name
    # end def __str__

# end class _Wrapped_

class Wrapped_FM (_Wrapped_) :
    """Wrapped function/method."""

    def __call__ (self, * args, ** kw) :
        raise NotImplementedError \
            ("%s.__call__ must be redefined" % self.__class__.__name__)
        return self.fct (* args, ** kw)
    # end def __call__

# end class Wrapped_FM

class Wrapped_Gen (_Wrapped_) :
    """Wrapped generator"""

    def __init__ (self, __name__, name, fct, Wrapped_FM, * args, ** kw) :
        self.__super.__init__ (__name__, name, fct, * args, ** kw)
        self.Wrapped_FM = Wrapped_FM
    # end def __init__

    def __call__ (self, * args, ** kw) :
        g = self.fct (* args, ** kw)
        w = self.Wrapped_FM \
            ( self.__name__, self.name + ".next", g.next
            , * (self.args + args), ** dict (self.kw, ** kw)
            )
        w.kw ["run"] = 0
        while True :
            yield w ()
            w.kw ["run"] += 1
    # end def __call__

# end class Wrapped_Gen

class Wrapper (TFL.Meta.Object) :
    """Provide wrappers for functions and methods"""

    Wrapped_Gen = Wrapped_Gen

    def __init__ (self, * wrapped_args, ** wrapped_kw) :
        if wrapped_kw.get ("Wrapped_FM") is not None :
            self.Wrapped_FM = wrapped_kw ["Wrapped_FM"]
            del wrapped_kw ["Wrapped_FM"]
        self.wrapped_args = wrapped_args
        self.wrapped_kw   = wrapped_kw
    # end def __init__

    def add_function (self, module, name) :
        """Wrap function with `name` of module or package-namespace
           `module`.
        """
        setattr (module, name, self._wrapped (module, name))
    # end def add_function

    def add_method (self, cls, name) :
        """Wrap method with `name` of class `cls`"""
        wrapped = self._wrapped (cls, name)
        setattr (cls, name, pyk.new_instancemethod (wrapped, None, cls))
    # end def add_method

    def _wrapped (self, cm, name) :
        qname = "%s.%s" % (cm.__name__, name)
        fct   = getattr (cm, name)
        try :
            co_flags = fct.func_code.co_flags
        except AttributeError :
            co_flags = None
        if co_flags and (co_flags & CO_GENERATOR) :
            return self.Wrapped_Gen \
                ( name, qname, fct, self.Wrapped_FM
                , * self.wrapped_args, ** self.wrapped_kw
                )
        else :
            return self.Wrapped_FM \
                (name, qname, fct, * self.wrapped_args, ** self.wrapped_kw)
    # end def _wrapped

# end class Wrapper

if __name__ != "__main__" :
    TFL.FMW._Export ("*")
### __END__ TFL.FMW.Wrapper
