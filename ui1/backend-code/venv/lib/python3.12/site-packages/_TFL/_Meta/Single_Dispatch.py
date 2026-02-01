# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.Meta.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.Meta.Single_Dispatch
#
# Purpose
#    Implement dispatch based on the type of a single argument
#
# Revision Dates
#    25-Jun-2013 (CT) Creation
#    27-Jun-2013 (CT) Add `Single_Dispatch_Method.__new__` to allow arguments
#                     when used as decorator
#    27-Jun-2013 (CT) Add `Single_Dispatch_Method.__call__` to allow calls of
#                     un-bound method
#    12-Sep-2013 (CT) Return `func`, not `self`, from
#                     `Single_Dispatch_Method.add_type` (decorator chaining)
#    12-Sep-2013 (CT) Allow more than one type arg for `add_type`
#    16-Jan-2014 (CT) Add `Single_Dispatch.__new__` to allow arguments
#                     when used as decorator
#     2-Jul-2014 (CT) Add `__debug__` clause to `Single_Dispatch.add_type`
#    13-Apr-2015 (CT) Add `derived` and `override_type`
#                     + factor `_add_types`; add `_derived`
#                     + DRY `Single_Dispatch_Method.add_type`
#     7-Aug-2015 (CT) Change `Single_Dispatch.__init__` to save `__doc__`
#    ««revision-date»»···
#--

from   _TFL              import TFL
from   _TFL.pyk          import pyk


import _TFL._Meta.Object
import _TFL._Meta.Property

from   weakref           import WeakKeyDictionary

import functools

class Single_Dispatch (TFL.Meta.Object) :
    """Dispatch based on the type of a single argument."""

    dispatch_on = 0

    def __new__ (sd_cls, func = None, T = object, dispatch_on = None) :
        if func is None :
            return \
                ( lambda func, T = T, dispatch_on = dispatch_on
                    : sd_cls (func, T = T, dispatch_on = dispatch_on)
                )
        return sd_cls.__c_super.__new__ (sd_cls)
    # end def __new__

    def __init__ (self, func, T = object, dispatch_on = None) :
        self.top_func = func
        self.top_type = T
        self.registry = { T : func }
        self.cache    = WeakKeyDictionary ()
        self._derived = set ()
        if dispatch_on is not None :
            self.dispatch_on = dispatch_on
        functools.wraps (func) (self)
        ### `functools.wraps` fails to transfer `__doc__`
        self.__doc__  = getattr (func, "__doc__", None)
    # end def __init__

    def __call__ (self, * args, ** kw) :
        try :
            da = args [self.dispatch_on]
        except IndexError as exc :
            raise TypeError \
                ( "Function %r needs at least %s positional arguments; "
                  "got %s: %s, %s"
                % ( self.top_func.__name__
                  , self.dispatch_on + 1
                  , len (args), args, kw
                  )
                )
        func = self.dispatch (da.__class__)
        return func (* args, ** kw)
    # end def __call__

    def add_type (self, * Types, ** kw) :
        """Add implementations for `Types`"""
        func = kw.pop ("func", None)
        if func is None :
            return lambda func : self.add_type (* Types, func = func)
        else :
            registry = self.registry
            _derived = self._derived
            for T in Types :
                if T in registry and not T in _derived :
                    raise TypeError \
                        ( "Duplicate implementation for function %r for type %r"
                        % (self.top_func.__name__, T.__name__)
                        )
            return self._add_types (func, Types)
    # end def add_type

    def derived (self) :
        """Return a derived generic function with a copy of the dispatch table"""
        result          = self.__class__ \
            (self.top_func, self.top_type, self.dispatch_on)
        result.registry = dict (self.registry)
        result._derived = set  (self.registry)
        return result
    # end def derived

    def dispatch (self, T) :
        """Return the function implementation matching type `T`."""
        try :
            result = self.cache [T]
        except KeyError :
            try :
                result = self.registry [T]
            except KeyError :
                result = self.registry [self._best_match (T)]
            self.cache [T] = result
        return result
    # end def dispatch

    def override_type (self, * Types, ** kw) :
        """Add implementations for `Types`,
           overriding existing implementations, if any.
        """
        func = kw.pop ("func", None)
        if func is None :
            return lambda func : self.override_type (* Types, func = func)
        else :
            return self._add_types (func, Types)
    # end def override_type

    def _add_types (self, func, Types) :
        if __debug__ :
            try :
                top_name = getattr (self.top_func, "__name__")
                add_name = getattr (func, "__name__")
            except AttributeError :
                pass
            else :
                if top_name == add_name :
                    raise TypeError \
                        ( "Name clash; specify a different name for %s "
                          "to avoid shadowing of generic function %s"
                        % (func, self.top_func)
                        )
        registry = self.registry
        _derived = self._derived
        for T in Types :
            registry [T] = func
            _derived.discard (T)
        self.cache.clear ()
        ### needs to return `func` to allow decorator chaining
        return func
    # end def _add_types

    def _best_match (self, T) :
        registry = self.registry
        matches  = tuple (b for b in T.__mro__ [1:] if b in registry)
        if not matches :
            raise TypeError ("No match for argument type %s" % (T, ))
        return matches [0]
    # end def _best_match

# end class Single_Dispatch

class Single_Dispatch_2nd (Single_Dispatch) :
    """Dispatch based on the type of the second argument."""

    dispatch_on = 1

# end class Single_Dispatch_2nd

class Single_Dispatch_Method (TFL.Meta.Method_Descriptor) :
    """Dispatch a method based on the type of the second, i.e., first
       non-self, argument.
    """

    def __new__ \
            ( sdm_cls
            , method = None, cls = None, T = object, dispatch_on = None
            ) :
        if method is None :
            return \
                ( lambda method, cls = cls, T = T, dispatch_on = dispatch_on
                    : sdm_cls
                          (method, cls = cls, T = T, dispatch_on = dispatch_on)
                )
        return sdm_cls.__c_super.__new__ (sdm_cls)
    # end def __new__

    def __init__ (self, method, cls = None, T = object, dispatch_on = None) :
        func = method
        if isinstance (func, TFL.Meta.Method_Descriptor) :
            func = func.method
        self.__super.__init__ \
            ( Single_Dispatch_2nd (func, T = T, dispatch_on = dispatch_on)
            , cls = cls
            )
    # end def __init__

    def __call__ (self, * args, ** kw) :
        return self.method (* args, ** kw)
    # end def __call__

    def add_type (self, * Types, ** kw) :
        return self.method.add_type (* Types, ** kw)
    # end def add_type

    def dispatch (self, T) :
        return self.method.dispatch (T)
    # end def dispatch

    def override_type (self, * Types, ** kw) :
        return self.method.override_type (* Types, ** kw)
    # end def override_type

# end class Single_Dispatch_Method

__doc__ = """
:class:`Single_Dispatch` implements dispatch based on the type of a single
argument::

    >>> @Single_Dispatch
    ... def foo (x) :
    ...     print ("foo got generic argument", x)

    >>> foo.__name__, foo.__class__
    ('foo', <class 'Single_Dispatch.Single_Dispatch'>)

    >>> sorted ((k.__name__, v.__name__) for k, v in foo.registry.items ())
    [('object', 'foo')]

    >>> foo (23)
    foo got generic argument 23
    >>> foo ("42")
    foo got generic argument 42

    >>> @foo.add_type (int)
    ... def foo_int (x) :
    ...     print ("foo_int got integer argument", x)

    >>> sorted ((k.__name__, v.__name__) for k, v in foo.registry.items ())
    [('int', 'foo_int'), ('object', 'foo')]

    >>> foo (23)
    foo_int got integer argument 23

    >>> foo ("42")
    foo got generic argument 42

    >>> @foo.add_type (str)
    ... def foo_str (x) :
    ...     print ("foo_str got string argument '%s'" % (x, ))

    >>> foo (23)
    foo_int got integer argument 23

    >>> foo ("42")
    foo_str got string argument '42'

    >>> @foo.add_type (int)
    ... def foo_int2 (x) :
    ...     print ("foo_int2 got integer argument", x)
    Traceback (most recent call last):
    ...
    TypeError: Duplicate implementation for function 'foo' for type 'int'

    >>> @foo.override_type (int)
    ... def foo_int2 (x) :
    ...     print ("foo_int2 got integer argument", x)

    >>> foo (37)
    foo_int2 got integer argument 37

    >>> foobar = foo.derived ()
    >>> @foobar.add_type (int)
    ... def foobar_int (x) :
    ...     print ("foobar_int got integer argument", x)

    >>> foobar (23)
    foobar_int got integer argument 23

    >>> foobar ("42")
    foo_str got string argument '42'

    >>> @Single_Dispatch_2nd
    ... def bar (* args) :
    ...     print ("bar got generic argument", args)

    >>> bar (1)
    Traceback (most recent call last):
    ...
    TypeError: Function 'bar' needs at least 2 positional arguments; got 1: (1,), {}
    >>> bar (1, 2)
    bar got generic argument (1, 2)
    >>> bar (1, 2, 3)
    bar got generic argument (1, 2, 3)

    >>> @bar.add_type (int)
    ... def bar_int (* args) :
    ...     print ("bar_int got integer argument", args)

    >>> bar (1, 2)
    bar_int got integer argument (1, 2)

    >>> bar (1, 2.0)
    bar got generic argument (1, 2.0)

    >>> @bar.add_type (float)
    ... def bar_float (* args) :
    ...     print ("bar_float got float argument", args)

    >>> bar (1, 2)
    bar_int got integer argument (1, 2)
    >>> bar (1, 2.0)
    bar_float got float argument (1, 2.0)
    >>> bar (1, True)
    bar_int got integer argument (1, True)

    >>> barfoo = bar.derived ()

    >>> @barfoo.add_type (bool)
    ... def barfoo_bool (* args) :
    ...     print ("barfoo_bool got boolean argument", args)

    >>> barfoo (1, 2)
    bar_int got integer argument (1, 2)
    >>> barfoo (1, 2.0)
    bar_float got float argument (1, 2.0)
    >>> barfoo (1, True)
    barfoo_bool got boolean argument (1, True)


:class:`Single_Dispatch_Method` implements dispatch based on the type of a
single, normally the second, argument of an instance method::

    >>> class Qux (object) :
    ...
    ...     @Single_Dispatch_Method
    ...     def qux (self, x, y) :
    ...         print ("qux got generic argument", x, y)
    ...
    ...     @qux.add_type (int)
    ...     def qux_int (self, x, y) :
    ...         print ("qux_int got integer argument", x, y)

    >>> baz = Qux ()
    >>> baz.qux (1, 2)
    qux_int got integer argument 1 2

    >>> baz.qux ('1', 2)
    qux got generic argument 1 2

    >>> @Qux.qux.add_type (str)
    ... def qux_str (self, x, y) :
    ...     print ("qux_str got string argument", x, y)

    >>> baz.qux (1, 2)
    qux_int got integer argument 1 2

    >>> baz.qux ('1', 2)
    qux_str got string argument 1 2

    >>> baz.qux (1.0, 2)
    qux got generic argument 1.0 2

    >>> @Qux.qux.add_type (int)
    ... def qux_int2 (self, x, y) :
    ...     print ("qux_int2 got integer argument", x, y)
    Traceback (most recent call last):
    ...
    TypeError: Duplicate implementation for function 'qux' for type 'int'

    >>> @Qux.qux.override_type (int)
    ... def qux_int2 (self, x, y) :
    ...     print ("qux_int2 got integer argument", y, x)

    >>> baz.qux (1, 2)
    qux_int2 got integer argument 2 1

"""

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.Single_Dispatch
