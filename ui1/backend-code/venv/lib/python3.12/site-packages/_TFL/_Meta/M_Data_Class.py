# -*- coding: utf-8 -*-
# Copyright (C) 2005-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Meta.M_Data_Class
#
# Purpose
#    Meta class supporting definition of classes holding data
#
# Revision Dates
#    25-Jan-2005 (CT) Creation
#    27-Jan-2005 (CT) s/_allowed/_names/g
#    27-Jan-2005 (CT) `_values` added and used
#     4-Feb-2005 (CT) `__call__` added to allow instance derivation from
#                     data-classes
#     4-Feb-2005 (CT) Ancestor of `_names` and `_values` changed from `type`
#                     to `object`
#     4-Feb-2005 (CT) `__module__` set for newly created classes
#     4-Feb-2005 (CT) `_check_dict` factored
#    30-Mar-2005 (CT) `__call__` and `__repr__` added to `_names` to allow
#                     instance derivation from instances, too
#    30-Mar-2005 (CT) Optional argument `name` added to `M_Data_Class.__call__`
#    30-Mar-2005 (CT) `_check_dict` changed to ignore magic names
#    29-Aug-2008 (CT)  s/super(...)/__m_super/
#     2-Feb-2009 (CT) s/_M_Type_/M_Base/
#     4-Feb-2009 (CT) Documentation improved
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

"""
M_Data_Class supports the definition of classes holding primarily or
exclusively data in the form of class attributes with full support for
inheritance.

::

    >>> class M_Record (M_Data_Class) :
    ...     class _names (M_Data_Class._names) :
    ...         foo  = None
    ...         bar  = 42
    ...         baz  = 137
    ...         quux = None
    ...
    >>> R1 = M_Record ("R1", (), dict (foo = 1))
    >>> print (R1, R1.foo, R1.bar, R1.baz)
    <Record R1> 1 42 137
    >>> R2 = M_Record ("R2", (R1, ), dict (bar = 2))
    >>> print (R2, R2.foo, R2.bar, R2.baz)
    <Record R2> 1 2 137
    >>> R3 = M_Record ("R3", (R1, ), dict (baz = 3))
    >>> print (R3, R3.foo, R3.bar, R3.baz)
    <Record R3> 1 42 3
    >>> R4 = M_Record ("R4", (R2, R3), dict ())
    >>> print (R4, R4.foo, R4.bar, R4.baz)
    <Record R4> 1 2 3
    >>> R5 = M_Record ("R5", (R1, ),   dict (bauz = 5))
    Traceback (most recent call last):
      ...
    TypeError: <Record R5> doesn't allow attribute bauz=5
    >>> r1  = R1 (name = "r1",  quux = 1)
    >>> print (r1, r1.foo, r1.bar, r1.baz, r1.quux)
    <Record instance r1> 1 42 137 1
    >>> r11 = r1 (name = "r11", foo  = 2)
    >>> print (r11, r11.foo, r11.bar, r11.baz, r11.quux)
    <Record instance r11> 2 42 137 1
    >>> r12 = r1 (name = "r12", foo  = 3, quux = 13)
    >>> print (r12, r12.foo, r12.bar, r12.baz, r12.quux)
    <Record instance r12> 3 42 137 13
"""

from   _TFL             import TFL
from   _TFL.pyk         import pyk

import _TFL._Meta.M_Class
import _TFL.Caller

class M_Data_Class (TFL.Meta.M_Base) :
    """Meta class supporting definition of classes holding data"""

    class _names (object) :

        def __call__ (self, ** kw) :
            ### Allow creation of instances derived from data-class instances
            ### with new instance attributes specified by `kw`
            return self.__class__ (** dict (self.__dict__, ** kw))
        # end def __call__

        def __repr__ (self) :
            return "<%s instance %s>" % \
                ( self.__class__.__class__.__name__ [2:]
                , getattr (self, "name", self.__class__.__name__)
                )
        # end def __repr__

    # end class _names

    class _values (object) :
        pass
    # end class _values

    def __new__ (meta, name, bases, dict) :
        if not bases :
            bases = (meta._names, )
        if "__module__" not in dict :
            dict ["__module__"] = TFL.Caller.globals () ["__name__"]
        result = meta.__mc_super.__new__ (meta, str (name), bases, dict)
        return result
    # end def __new__

    def __init__ (cls, name, bases, dict) :
        cls._check_dict        (dict)
        cls.__m_super.__init__ (name, bases, dict)
    # end def __init__

    def __call__ (cls, name = None, ** kw) :
        ### Allow creation of instances derived from data-class with instance
        ### attributes specified by `kw`
        cls._check_dict        (kw)
        result = cls.__new__   (cls)
        result.__init__        ()
        result.__dict__.update (kw)
        if name is not None :
            result.name = name
        return result
    # end def __call__

    def __repr__ (cls) :
        return "<%s %s>" % (cls.__class__.__name__ [2:], cls.__name__)
    # end def __repr__

    def _check_dict (cls, dict) :
        _names  = cls._names.__dict__
        _values = cls._values.__dict__
        for k, v in pyk.iteritems (dict) :
            if not k.startswith ("__") :
                if k not in _names :
                    raise TypeError \
                        ("%s doesn't allow attribute %s=%r" % (cls, k, v))
                if k in _values and v not in _values [k] :
                    raise ValueError \
                        ("%s doesn't allow value `%s` for `%s`" % (cls, v, k))
    # end def _check_dict

# end class M_Data_Class

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.M_Data_Class
