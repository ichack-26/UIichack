# -*- coding: utf-8 -*-
# Copyright (C) 2002-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Meta.Object
#
# Purpose
#    Base class using TFL.Meta.Class as metaclass
#
# Revision Dates
#    13-May-2002 (CT) Creation
#    17-Jan-2003 (CT) `M_` prefixes added
#    24-Mar-2003 (CT) Delegation for `__init__` added
#     5-Mar-2008 (CT) `_TFL_Meta_Object_Root_` added to accomodate Python 2.6
#                     (http://bugs.python.org/issue1683368)
#     2-Feb-2009 (CT) Documentation improved
#    17-Jul-2009 (CT) `_check_MRO` and doctest added to `_TFL_Meta_Object_Root_`
#     9-Dec-2009 (CT) Context manager `LET` added
#    10-Dec-2009 (CT) `LET` defined as alias for `TFL.Context.attr_let`
#    16-Feb-2011 (CT) `pop_to_self` added
#     8-Jun-2012 (CT) Add `opts.get ("prefix")` to `pop_to_self`
#    23-May-2013 (CT) Use `TFL.Meta.BaM` for Python-3 compatibility
#     5-Jun-2014 (CT) Remove `__properties`
#    16-Oct-2015 (CT) Add `__future__` imports
#    17-Apr-2018 (CT) Change doctest to work with and without `-O`
#    ««revision-date»»···
#--

from   _TFL       import TFL
from   _TFL._Meta import Meta

import _TFL._Meta.M_Class
import _TFL._Meta.Property

import _TFL.Context
import _TFL.Decorator

class _TFL_Meta_Object_Root_ (object) :
    """Root class to fix `__init__` and `__new__`, check the `mro`.

       As of Python 2.6, `object.__init__` doesn't accept parameters
       (http://bugs.python.org/issue1683368).

       Don't inherit from _TFL_Meta_Object_Root_ directly (unless you really
       know what you're doing).

    """

    def __new__ (cls, * args, ** kw) :
        if __debug__ :
            cls._check_MRO (args, kw)
        return object.__new__ (cls)
    # end def __new__

    def __init__ (self, * args, ** kw) :
        object.__init__ (self)
    # end def __init__

    @classmethod
    def _check_MRO (cls, args, kw) :
        if (args or kw) :
            ### Make sure that there is no class intervening between
            ### `_TFL_Meta_Object_Root_` and `object` in `cls.__mro__`
            ###
            ### due to http://bugs.python.org/issue1683368, cooperative
            ### calls to `__new__` and `__init__` can't work **unless**
            ### all cooperating classes derive from the same root (that
            ### is not `object`)
            sup = super (_TFL_Meta_Object_Root_, cls)
            msg       = \
                ( "MRO conflict for %s.%%s: super != object,\n    %s"
                % (cls.__name__, tuple (c.__name__ for c in cls.__mro__))
                )
            assert sup.__new__  is object.__new__,  (msg % ("__new__", ))
            assert sup.__init__ is object.__init__, (msg % ("__init__", ))
    # end def _check_MRO

# end class _TFL_Meta_Object_Root_

_Object_Root_ = _TFL_Meta_Object_Root_

class _TFL_Meta_Object_ (_Object_Root_, metaclass = Meta.M_Class) :
    """Instead of `object`, `TFL.Meta.Object` should be used as baseclass to
       define top-level classes. Classes derived (directly or indirectly)
       from `Object` gain the benefits:

       - :class:`~_TFL._Meta.M_Class.M_Class` is used as metaclass unless an
         explicit metaclass is defined for the derived class. `M_Class`
         provides the benefits:

         * `__super` for cooperative method calls
           (see :class:`~_TFL._Meta.M_Class.M_Autosuper`).

         * Renaming to `_real_name` to avoid name clashes between classes in
           a class hierarchy (see :class:`~_TFL._Meta.M_Class.M_Autorename`).

         Even if an explicit metaclass is defined for a class, it should
         still derive from `Object` to gain protection for cooperative
         `__init__` and `__new__` calls.

       - Cooperative super-calls to `__init__` (and `__new__`) are protected
         against `object.__init__` not accepting parameters in Python 2.6 and
         later.

         * More general, some, if not all, future incompatibility problems
           are easy to solve if `Object` is the single ancestor in
           need of fixing.
    """

    _real_name    = "Object"
    """This class will be known and used as `Object` although the class
       statement contains a different (mangled) name. This allows the use of
       the generic class name `Object` in different packages without messing
       up Python's name mangling. The renaming is done by `TFL.Meta.M_Class`
       (more specifically, by `TFL.Meta.M_Autorename` which is one of the
       bases of `M_Class`).
       """

    def __init__ (self, * args, ** kw) :
        ### delegate to `__super` to accomodate multiple inheritance
        self.__super.__init__ (* args, ** kw)
    # end def __init__

    LET = TFL.Meta.Class_and_Instance_Method (TFL.Context.attr_let)

    def pop_to_self (self, kw, * names, ** opts) :
        """Pop each name in `names` from `kw` and store its value in `self`."""
        prefix = opts.get ("prefix", "")
        for name in names :
            if name in kw :
                setattr (self, prefix + name, kw.pop (name))
    # end def pop_to_self

Object = _TFL_Meta_Object_ # end class

_test_MRO = """
In __debug__ mode, :class:`_Object_Root_` checks the MRO to ensure
that there is no class intervening between
`_TFL_Meta_Object_Root_` and `object` in `cls.__mro__`.

Due to http://bugs.python.org/issue1683368, cooperative
calls to `__new__` and `__init__` can't work **unless**
all cooperating classes derive from the same root (that
is not `object`)::

    >>> class A (object) :
    ...     def __init__ (self, x = 2) :
    ...         print ("A.__init__:", x)
    ...         self.x = x
    ...         super (A, self).__init__ ()
    ...
    >>> class B (TFL.Meta.Object, A) :
    ...     def __init__ (self, y) :
    ...         print ("B.__init__:", y)
    ...         self.y = y
    ...         self.__super.__init__ ()
    ...
    >>> b = B (1) ### Test fails if run with `-O` !!!
    Traceback (most recent call last):
        ...
    AssertionError: MRO conflict for B.__init__: super != object,
        ('B', 'Object', '_TFL_Meta_Object_Root_', 'A', 'object')

    >>> class C (object) :
    ...     def __init__ (self, x = 2) :
    ...         print ("C.__init__:", x)
    ...         self.x = x
    ...         super (C, self).__init__ ()
    ...
    >>> class D (TFL.Meta.Object, C) :
    ...     def __init__ (self, y, x = 3) :
    ...         print ("D.__init__:", y)
    ...         self.y = y
    ...         self.__super.__init__ (y = y, x = x)
    ...         C.__init__ (self, x)
    ...     @classmethod
    ...     def _check_MRO (cls, args, kw) :
    ...         '''We know what we're doing and explicitly call `C__init__`.'''
    ...
    >>> d = D (42)
    D.__init__: 42
    C.__init__: 3
    >>> print (d.x, d.y)
    3 42
"""

if __debug__ :
    __test__ = dict (test_MRO = _test_MRO)

if __name__ != "__main__" :
    TFL.Meta._Export ("Object")
### __END__ TFL.Meta.Object
