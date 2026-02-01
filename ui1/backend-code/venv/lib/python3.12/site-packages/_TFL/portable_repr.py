# -*- coding: utf-8 -*-
# Copyright (C) 2014-2019 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.portable_repr
#
# Purpose
#    Portable replacement for `repr` giving identical results in Python 2 & 3
#
# Revision Dates
#     9-Oct-2014 (CT) Creation
#     9-Oct-2014 (CT) Fix `dict` items, empty `tuple`, `unicode`; add `set`
#    10-Oct-2014 (CT) Add `function`
#    15-Oct-2014 (CT) Protect against recursion
#    16-Oct-2014 (CT) Wrap generic functions in dict created from
#                     `_portable_repr_properties` by `dict_from_class`
#    22-Oct-2015 (CT) Add `logging.exception` to `generic_portable_repr`
#    13-Feb-2017 (CT) Add `_float_epsilon`
#    19-Aug-2019 (CT) Add and use `print_prepr`
#    ««revision-date»»···
#--

from   _TFL                       import TFL

from   _TFL._Meta.Single_Dispatch import Single_Dispatch
from   _TFL.Decorator             import Attributed, Decorator, dict_from_class
from   _TFL.pyk                   import pyk

import collections
import sys

__doc__ = r"""
``portable_repr`` returns a portable canonical string
representation of `obj`.

For most object types, ``eval (portable_repr (object)) == object``.

Examples::

    >>> print_prepr ([1,2,3, "a", u"b", "c", b"bytes"])
    [1, 2, 3, 'a', 'b', 'c', 'bytes']

    >>> print_prepr ({ 1: u"a", 2: "b", "c" : 23, u"d" : 42 })
    {'c' : 23, 'd' : 42, 1 : 'a', 2 : 'b'}

    >>> print_prepr (set ([1, "a", "2", 3]))
    {'2', 'a', 1, 3}

    >>> print_prepr (1 << 65)
    36893488147419103232

    >>> import math
    >>> print_prepr (math.pi)
    3.14159265359

    >>> class C (object) :
    ...     class D (object) :
    ...         pass

    >>> print_prepr (C)
    <class 'portable_repr.C'>

    >>> print_prepr (C.D)
    <class 'portable_repr.D'>

    >>> print_prepr (dict)
    <class 'builtins.dict'>

    >>> print_prepr (type (u""))
    <class 'builtins.text-string'>

    >>> print_prepr (type (b""))
    <class 'builtins.byte-string'>

    >>> print_prepr (type (1 << 65))
    <class 'builtins.int'>

    >>> dd = TFL.defaultdict(int,{1: 2, "a": 42})
    >>> portable_repr (dd)
    "defaultdict(<class 'builtins.int'>, {'a' : 42, 1 : 2})"

    >>> portable_repr(portable_repr.top_func)
    '<function generic_portable_repr>'

    >>> l = [1,2,3]
    >>> t = ("a", l)
    >>> l.append (t)

    >>> print_prepr (l)
    [1, 2, 3, ('a', [...])]

    >>> print_prepr (t)
    ('a', [1, 2, 3, (...)])

"""

@dict_from_class
class _portable_repr_properties (object) :
    """Dictionary of properties for `portable_repr`"""

    if sys.version_info < (3,) :
        Type_Name_Map  = dict \
            ( bytes    = "byte-string"
            , long     = "int"
            , str      = "byte-string"
            , unicode  = "text-string"
            )
    else : ### Python version >= 3
        Type_Name_Map  = dict \
            ( bytes    = "byte-string"
            , str      = "text-string"
            )

    @Single_Dispatch
    def generic_portable_repr (obj, seen) :
        """Return a portable canonical string representation of `obj`.

           For many object types, eval (portable_repr (object)) == object.
        """
        try :
            return repr (obj)
        except Exception as exc :
            import logging
            logging.exception \
                ( "***** Exception '%s' for object of type %s"
                , exc.__class__.__name__, type (obj)
                )
            raise
    call = generic_portable_repr # end def

    @Decorator
    def recurses (f) :
        def _ (obj, seen) :
            oid = id (obj)
            if oid in seen :
                return portable_repr.recursion_repr (obj)
            else :
                seen = set (seen)
                seen.add   (oid)
                return f   (obj, seen)
        return _
    # end def recurses

    @Single_Dispatch
    def recursion_repr (obj) :
        return "<Recursion on %s...>" % (obj.__class__.__name__)
    # end def recursion_repr

    @recursion_repr.add_type (dict)
    def recursion_repr_dict (obj) :
        return "{...}"
    # end def recursion_repr_dict

    @recursion_repr.add_type (list)
    def recursion_repr_list (obj) :
        return "[...]"
    # end def recursion_repr_list

    @recursion_repr.add_type (tuple)
    def recursion_repr_tuple (obj) :
        return "(...)"
    # end def recursion_repr_tuple

    @generic_portable_repr.add_type (collections.defaultdict)
    def default_dict (obj, seen) :
        return "%s(%s, %s)" % \
            ( obj.__class__.__name__
            , portable_repr.call (obj.default_factory, seen)
            , portable_repr.dict (obj,                 seen)
            )
    # end def default_dict

    @generic_portable_repr.add_type (dict)
    @recurses
    def dict (obj, seen) :
        return "".join \
            ( ( "{"
              , ( ", ".join
                    ( sorted
                        ( " : ".join
                            ( ( portable_repr.call (k, seen)
                              , portable_repr.call (v, seen)
                              )
                            )
                        for k, v in pyk.iteritems (obj)
                        )
                    )
                )
              , "}"
              )
            )
    # end def dict

    @generic_portable_repr.add_type (float)
    def float (obj, seen) :
        return "%.12g" % obj if abs (obj) >= portable_repr._float_epsilon \
            else "0"
    # end def float

    @generic_portable_repr.add_type (type (call.top_func))
    def function (obj, seen) :
        return "<function %s>" % obj.__name__
    # end def function

    @generic_portable_repr.add_type (list)
    @recurses
    def list (obj, seen) :
        return "".join \
            ( ( "["
              , (", ".join (portable_repr.call (x, seen) for x in obj))
              , "]"
              )
            )
    # end def list

    @generic_portable_repr.add_type (set)
    def set (obj, seen) :
        return "".join \
            ( ( "{"
              , (", ".join (sorted (portable_repr.call (x, seen) for x in obj)))
              , "}"
              )
            )
    # end def set

    @generic_portable_repr.add_type (tuple)
    @recurses
    def tuple (obj, seen) :
        return "".join \
            ( ( "("
              , (", ".join (portable_repr.call (x, seen) for x in obj))
              , "," if len (obj) == 1 else ""
              , ")"
              )
            )
    # end def tuple

    @generic_portable_repr.add_type (type)
    def type (obj, seen) :
        m_name = obj.__module__
        if m_name == "__builtin__" :
            m_name = "builtins"
        t_name = portable_repr.Type_Name_Map.get (obj.__name__, obj.__name__)
        return "<class %s>" % \
            portable_repr.call (".".join ((m_name, t_name)), seen)
    # end def type

    if sys.version_info < (3,) :
        @generic_portable_repr.add_type (long)
        def long (obj, seen) :
            return repr (obj).rstrip ("L")
        # end def long

        @generic_portable_repr.add_type (unicode)
        def unicode (obj, seen) :
            return repr (obj).lstrip ("u")
        # end def unicode
    else : ### Python version >= 3
        @generic_portable_repr.add_type (bytes)
        def bytes (obj, seen) :
            return repr (obj).lstrip ("b")
        # end def bytes

# end class _portable_repr_properties

_portable_repr_properties.update \
    (  (k, getattr (_portable_repr_properties ["call"], k))
    for k in ("add_type", "dispatch", "top_func")
    )

@Attributed (_float_epsilon = 1e-16, ** _portable_repr_properties)
def portable_repr (obj) :
    """Return a portable canonical string representation of `obj`.

       For many object types, eval (portable_repr (object)) == object.
    """
    return portable_repr.call (obj, seen = set ())
# end def portable_repr

def print_prepr (* args) :
    """Print `portable_repr` of all `args`"""
    print (* (portable_repr (a) for a in args))
# end def print_prepr

__all__ = ("portable_repr", "print_prepr")

if __name__ != "__main__" :
    TFL._Export (* __all__)
### __END__ TFL.portable_repr
