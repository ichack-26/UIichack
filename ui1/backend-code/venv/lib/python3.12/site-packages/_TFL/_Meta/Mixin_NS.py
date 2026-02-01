# -*- coding: utf-8 -*-
# Copyright (C) 2009-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Meta.Mixin_NS
#
# Purpose
#    Provide mixin namespaces
#
# Revision Dates
#    17-Apr-2009 (CT) Creation
#    23-May-2013 (CT) Use `TFL.Meta.BaM` for Python-3 compatibility
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL             import TFL
import _TFL._Meta.M_Class

import _TFL.Caller

class M_Mixin_NS (TFL.Meta.M_Class) :
    """Meta class for Mixin_NS"""

    Copy  = TFL.Meta.M_Class.New
    Table = {}

    def New (cls, * mixins) :
        """Create a new Mixin_NS for `mixins` class(es)"""
        assert mixins
        result = cls.Table.get (mixins)
        if result is None :
            mixin  = mixins [0]
            name   = "MNS_%s" % (mixin.__name__, )
            result = cls.Table [mixins] = type \
                ( str (name)
                , (Mixin_NS, ) + mixins
                , dict
                    ( __module__ = TFL.Caller.globals () ["__name__"]
                    , __doc__    = getattr (mixin, "__doc__", None)
                    )
                )
        return result ()
    # end def New

# end class M_Mixin_NS

class Mixin_NS (object, metaclass = M_Mixin_NS) :
    """Mixin namespace: provides access to mixin functionality via a single
       object.

       Inspired by Michele Simionato's essay `Mixins considered harmful/4`
       (http://www.artima.com/weblogs/viewpost.jsp?thread=254507).

       >>> class M1 (object) :
       ...     def foo (self) :
       ...         ### Use `self._obj` to show class of bound object
       ...         print (self._obj.__class__.__name__, "foo", self.a, self.b)
       ...
       >>> class M2 (object) :
       ...     def foo (self) :
       ...         print (self._obj.__class__.__name__, "foo", self.b, self.c)
       ...     def bar (self) :
       ...         print (self._obj.__class__.__name__, "bar", self.c)
       ...
       >>> class C (object) :
       ...     m1 = Mixin_NS.New (M1)
       ...     m2 = Mixin_NS.New (M2)
       ...     a  = 1
       ...     b  = 2
       ...     c  = 3
       ...
       >>> c = C ()
       >>> c.m1.foo ()
       C foo 1 2
       >>> c.m2.foo ()
       C foo 2 3
       >>> c.m2.bar ()
       C bar 3
       >>>
       >>> c.m1 = 42
       Traceback (most recent call last):
       ...
       AttributeError: Cannot assign value 42 to mixin namespace attribute
       >>> C.m1.a
       Traceback (most recent call last):
         ...
       TypeError: Cannot access attributes of unbound instance of <MNS_M1 unbound>
    """

    def __init__ (self, obj = None) :
        self._obj = obj
    # end def __init__

    def __get__ (self, obj, cls = None):
        if obj is None:
            return self
        return self.__class__ (obj)
    # end def __get__

    def __getattr__ (self, name):
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        obj = self._obj
        if obj is None :
            raise TypeError \
                ("Cannot access attributes of unbound instance of %r" % (self))
        return getattr (obj, name)
    # end def __getattr__

    def __repr__ (self):
        obj = self._obj
        if obj is None :
            msg = "unbound"
        else :
            msg = "bound to %r" % obj
        return "<%s %s>" % (self.__class__.__name__, msg)
    # end def __repr__

    def __set__ (self, obj, value) :
        raise AttributeError \
            ("Cannot assign value %r to mixin namespace attribute" % (value, ))
    # end def __set__

# end class Mixin_NS

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ Mixin_NS
