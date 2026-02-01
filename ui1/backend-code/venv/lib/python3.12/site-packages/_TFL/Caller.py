# -*- coding: utf-8 -*-
# Copyright (C) 2001-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Caller
#
# Purpose
#    Return information about the context of the caller's caller (e.g.,
#    globals, locals, ...)
#
#    Started with a posting by Fredrik Lundh <effbot@telia.com> to
#    comp.lang.python (see http://www.deja.com/=dnc/getdoc.xp?AN=586687655)
#
#    For a description of frame objects, see the Python Reference Manual,
#    section `The standard type hierarchy', entry `Frame objects' (for 1.5.2,
#    on page 16)
#
# Revision Dates
#     6-Mar-2000 (CT) Creation
#     5-Apr-2000 (CT) `caller_code' added
#    10-Aug-2000 (CT) `caller_info' added
#     2-Sep-2000 (CT) Simplified `caller_info' (try/except isn't necessary)
#    18-May-2001 (CT) Renamed from caller_globals to TFL/Caller.py
#    18-May-2001 (CT) `depth' added
#    18-Sep-2001 (CT) `globs` and `locls` arguments added to `Scope.__init__`
#     3-Nov-2001 (MG) import `TFL.Caller` instead of `Caller`
#    25-Feb-2002 (CT) `Caller.__getitem__` changed to allow nested format
#                     expressions (stolen from Skip Montanaro <skip@pobox.com>)
#    12-Mar-2002 (CT) `_Export_Module` added
#     1-Jun-2002 (CT) Try `sys._getframe` in `frame` instead of raising
#                     `AssertionError`
#    13-Aug-2004 (CT) `Scope` derived from `TFL.Meta.Object`
#    13-Aug-2004 (CT) `Object_Scope` derived from `Scope`
#    17-Sep-2004 (CT) Optional argument `locls` added to `Object_Scope`
#    17-Sep-2004 (CT) `Object_Scope.derived` added
#    24-Mar-2005 (CT) `U_Test` scaffolding removed (use `run_doctest` instead)
#    25-Mar-2005 (MG) Import of `Filename` changed
#    14-Sep-2005 (CT) `kw` added to `Scope.__init__`
#    28-Dec-2005 (CT) `Scope.eval` added
#    28-Dec-2005 (CT) `Scope.__getitem__` changed to raise `KeyError` instead
#                     of `NameError`
#    29-Dec-2005 (CT) `Object_Scope.__getitem__` changed to catch `KeyError`
#                     instead of `NameError`
#    24-Jan-2008 (CT) More doctests added
#    11-Sep-2009 (CT) `Object_Scope_Mutable` added
#    31-Jan-2012 (CT) Change `Object_Scope.__init__` to pass
#                     `object.__dict__` through `dict` (to allow classes, too)
#    16-Jul-2015 (CT) Use `expect_except` in doc-tests
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.Object

import sys
import traceback

def frame (depth = 0) :
    """Return the execution frame of the caller's caller (for depth == 1, the
       frame of the caller's caller's caller is returned, and so on).
    """
    try:
        result = sys._getframe (2 + depth)
    except AttributeError :
        result = sys.exc_traceback.tb_frame.f_back.f_back
        try :
            for i in range (depth) :
                result = result.f_back
        except AttributeError :
            raise ValueError ("call stack is not deep enough: %d" % (depth, ))
    return result
# end def frame

def globals (depth = 0) :
    """Return the `globals ()` of the caller's caller (larger values of
       `depth` return caller's farther up the call stack).

       This is useful for evaluating an expression in the context of a
       function's caller or for changing the context of a functions caller
       (e.g., for implementing a Common Lisp like `trace` function)
    """
    return frame (depth).f_back.f_globals
# end def globals

def locals (depth = 0) :
    """Return the `locals ()` of the caller's caller (larger values of
       `depth` return caller's farther up the call stack).

       This is useful for evaluating an expression in the context of a
       function's caller.
    """
    return frame (depth).f_back.f_locals
# end def locals

def code (depth = 0) :
    """Returns the code object of the caller's caller (larger values of
       `depth` return caller's farther up the call stack).
    """
    return frame (depth).f_back.f_code
# end def code

def info (level = -3) :
    """Returns `file-name`, `line-number`, and `function-name` of caller at
       position `level` in the call stack (-3 being the caller of
       `infos` caller).
    """
    return traceback.extract_stack () [level] [:3]
# end def info

class Scope (TFL.Meta.Object) :
    """Global and local variables visible in caller's scope.

       The variables are available as attributes and via the index operator.
       The index operator also supports expressions as indices and will
       return the result of such expressions as evaluated in the caller's
       scope.

       The supplied index operator allows Scope objects to be used as mapping
       arguments for the string formatting operator "%"::

           >>> print ("42*3 == %(42*3)s" % Scope ())
           42*3 == 126

           >>> a,b,c = 2,3,4
           >>> print ("a = %(a)s, b = %(b)d, c = %(c)f, d = %(b*c)s" % Scope ())
           a = 2, b = 3, c = 4.000000, d = 12

           >>> list = [x*x for x in range (10)]
           >>> print ("%(list)s, %(list [2:4])s, %(list [-1])s" % Scope ())
           [0, 1, 4, 9, 16, 25, 36, 49, 64, 81], [4, 9], 81

           >>> square = lambda n : n * n
           >>> print ("%(square (%(3*4)s))s" % Scope ())
           144

    """

    def __init__ (self, depth = 0, globs = None, locls = None, ** kw) :
        if globs is None :
            globs = globals (depth)
        if locls is None :
            locls = locals  (depth)
        if kw :
            locls = dict (locls, ** kw)
        self.globals = globs
        self.locals  = locls
    # end def __init__

    def eval (self, expression, globs = {}) :
        return eval (expression, globs, self)
    # end def eval

    def __getitem__ (self, index) :
        ### following Skip Montanaro, we interpolate `self` first to allow
        ### nested `%(expression)s`, ### e.g., "%(2*(%(3*4)s))s" % Scope ()
        index = index % self
        try :
            return eval (index, self.globals, self.locals)
        except NameError :
            raise KeyError (index)
    # end def __getitem__

    def __getattr__ (self, name) :
        try :
            return self.locals [name]
        except KeyError :
            try :
                return self.globals [name]
            except KeyError :
                raise AttributeError (name)
    # end def __getattr__

# end class Scope

class Object_Scope (Scope) :
    """Provide access to the caller's locals and to the
       attributes of the object passed in.

       >>> from _TFL.Filename import *
       >>> f = Filename ("/foo/bar/baz.dat")
       >>> c = Object_Scope  (f)
       >>> c.f
       Filename (/foo/bar/baz.dat)
       >>> c.name
       '/foo/bar/baz.dat'
       >>> c.base
       'baz'
       >>> c.ext
       '.dat'
       >>> c.base_ext
       'baz.dat'
       >>> c.directory
       '/foo/bar'
       >>> c.directories
       <bound method Filename.directories of Filename (/foo/bar/baz.dat)>
       >>> list (c.directories ())
       ['foo', 'bar']
       >>> from _TFL.Record import Record
       >>> c = Record (x = 1)
       >>> o = Record (a = 42, b = Record (a = 137, b = "foo", c = c))
       >>> s = Object_Scope (o)
       >>> s.a
       42
       >>> print (s.b)
       (a = 137, b = 'foo', c = Record (x = 1))
       >>> print (s.b.c)
       (x = 1)
       >>> "s.a = %(a)s, s.b.a = %(b.a)s, s.b.c.x = %(b.c.x)s" % s
       's.a = 42, s.b.a = 137, s.b.c.x = 1'
    """

    def __init__ (self, object, locls = None) :
        self.__super.__init__ \
            (depth = 1, globs = dict (object.__dict__), locls = locls)
        self.object = object
    # end def __init__

    def derived (self, ** kw) :
        return self.__class__ (self.object, locls = dict (self.locals, ** kw))
    # end def derived

    def __getitem__ (self, index) :
        try :
            return self.__super.__getitem__ (index)
        except KeyError :
            o = self.object
            for k in index.split (".") :
                o = getattr (o, k)
            return o
    # end def __getitem__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        try :
            return self.__super.__getattr__ (name)
        except AttributeError :
            return getattr (self.object, name)
    # end def __getattr__

# end class Object_Scope

class Object_Scope_Mutable (Object_Scope) :
    """Add mutability to `Object_Scope`.

       >>> from _TFL.Record import Record
       >>> o = Record (a = 42, b = Record (a = 137, b = "foo"))
       >>> s = Object_Scope_Mutable (o, {})
       >>> s.a
       42
       >>> s.locals
       {}
       >>> s ["a"] = 137
       >>> s.a
       137
       >>> s.locals
       {'a': 137}
       >>> t = Object_Scope (o, {})
       >>> t.a
       42
       >>> with expect_except (TypeError) :
       ...     t ["a"] = 666
       TypeError: 'Object_Scope' object does not support item assignment
    """

    def __setitem__ (self, key, value) :
        self.locals [key] = value
    # end def __setitem__

# end class Object_Scope_Mutable

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

"""

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ Caller
