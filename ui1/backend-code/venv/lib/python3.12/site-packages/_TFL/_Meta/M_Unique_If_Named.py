# -*- coding: utf-8 -*-
# Copyright (C) 2009-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Meta.M_Unique_If_Named
#
# Purpose
#    Meta class enforcing unique names for objects
#
# Revision Dates
#    21-Aug-2009 (CT) Creation
#    21-Aug-2009 (CT) Guard `__getattr__` against `name == "_"`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

"""
>>> class A (TFL.Meta.Object) :
...     __metaclass__ = M_Unique_If_Named
...     def __init__ (self, name, ** kw) :
...         self.name = name
...         self.kw   = kw
...
>>> class B (A) :
...     pass
...
>>> class C (A) :
...     _ = TFL.Record ()
...
>>> a = A (name = "foo")
>>> b = B (name = "foo")
Traceback (most recent call last):
  ...
NameError: foo
>>> c = C (name = "foo")
>>> a is A._.foo, a is A ["foo"]
(True, True)
>>> a is B._.foo, a is B.foo
(True, True)
>>> c is C._.foo
True
>>> a is not C._.foo
True
"""

from   _TFL             import TFL
import _TFL._Meta.M_Class

import _TFL.Record

class M_Unique_If_Named (TFL.Meta.M_Class) :
    """Meta class enforcing unique names for objects"""

    def __init__ (cls, name, bases, dict) :
        cls.__m_super.__init__ (name, bases, dict)
        if not hasattr (cls, "_") :
            cls._ = TFL.Record ()
    # end def __init__

    def __call__ (cls, * args, ** kw) :
        name = kw.get ("name")
        if name :
            if name in cls._ :
                raise NameError (name)
        result = cls.__m_super.__call__ (* args, ** kw)
        if name :
            setattr (cls._, name, result)
        return result
    # end def __call__

    def __getattr__ (cls, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (cls.__m_super, name)
        if name == "_" :
            raise AttributeError (name)
        return getattr (cls._, name)
    # end def __getattr__

    def __getitem__ (cls, key) :
        return cls._ [key]
    # end def __getitem__

# end class M_Unique_If_Named

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.M_Unique_If_Named
