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
#    TFL.Meta.M_Class
#
# Purpose
#    Provide custom metaclass for new-style Python classes
#
# Revision Dates
#    10-May-2002 (CT)  Creation
#    17-Jan-2003 (CT)  `M_Automethodwrap` added
#    17-Jan-2003 (CT)  `M_` prefixes added
#    20-Jan-2003 (CT)  Docstring of `M_Automethodwrap` improved
#     3-Feb-2003 (CT)  File renamed from `Class.py` to `M_Class.py`
#     1-Apr-2003 (CT)  `M_Class_SW` factored
#     1-Apr-2003 (CT)  `M_Autoproperty` removed from `M_Class`
#                      (optimize, optimize)
#    28-Apr-2003 (CT)  `M_Autorename` changed to not manipulate `caller_globals`
#    23-Jul-2004 (CT)  `_M_Type_` added to `_Export`
#    25-Jan-2005 (CT)  `New` added
#    10-Feb-2005 (MG)  `_M_Type_.New`: `mangled_attributes` added
#    28-Mar-2005 (CT)  `M_Class_SWRP` added
#    23-Mar-2006 (CED) `_fixed_type_` added
#     8-Aug-2006 (PGO) `_super_calling_not_possible` added
#     7-Nov-2007 (CT)  Condition for `_super_calling_not_possible` corrected
#                      (don't complain if one of the bases has used
#                      `_real_name`)
#    29-Aug-2008 (CT)  `_fixed_type_.__init__` added to define `__m_super`
#    29-Aug-2008 (CT)  s/super(...)/__m_super/
#     2-Feb-2009 (CT)  s/_M_Type_/M_Base/
#     2-Feb-2009 (CT)  Documentation improved
#     3-Feb-2009 (CT)  Documentation improved..
#     4-Feb-2009 (CT)  Documentation improved...
#     4-Feb-2009 (CT)  s/_fixed_type_/M_M_Class/ and clarified implementation
#    11-Jun-2009 (CT)  `head_mixins` and `tail_mixins` added to `New`
#    24-Sep-2009 (CT)  Use `_TFL.callable` to avoid `-3` warnings
#    30-Aug-2010 (CT)  `M_Autorename.__name__` changed to pass `name` through
#                      `str` (`unicode` gives `type()` a sissy-fit)
#    10-Feb-2011 (CT)  `_m_combine_nested_class` added to `M_Base`
#    20-Jul-2012 (CT)  Add debug output to `M_Autorename.__new__`
#    28-Sep-2012 (CT)  Improve TypeError message from `_most_specific_meta`
#    20-Mar-2013 (CT)  Add support for `__name__` to `New`
#    23-May-2013 (CT)  Add and use `BaM` for Python-3 compatibility
#    25-Jun-2013 (CT)  Use `__mro__`, not `mro ()`
#    17-Mar-2014 (CT)  Add warning about `with_metaclass` to docstring of `BaM`
#    24-Apr-2014 (CT)  Change `New` to add `_real_name`
#    25-Apr-2014 (CT)  Add `__c_super` for use in `__new__` and classmethods
#    25-Apr-2014 (CT)  Add `__mc_super` for use in metaclass `__new__`
#     5-Jun-2014 (CT)  Remove `M_Autoproperty` and `M_Class_SWRP`
#    16-Jul-2015 (CT)  Use auto-numbered footnotes in docstring
#    10-Dec-2015 (CT) Change `_m_combine_nested_class` to set `__outer__`
#     8-Sep-2016 (CT) Change `M_Autorename.__new__` to fix `__qualname__`
#    19-Aug-2019 (CT) Use `print_prepr`
#     1-Apr-2020 (CT) Remove Py-2 compatibility crutch `BaM`
#     2-Apr-2020 (CT) Remove `pyk.Classic_Class_Type`
#    ««revision-date»»···
#--

from   _TFL             import TFL
from   _TFL.pyk         import pyk

import _TFL._Meta

def _m_mangled_attr_name (name, cls_name) :
    """Returns `name` as mangled by Python for occurences of `__%s` % name
       inside the definition of a class with name `cls_name`.

       >>> print (_m_mangled_attr_name ("foo", "Bar"))
       _Bar__foo
       >>> print (_m_mangled_attr_name ("foo", "_Bar"))
       _Bar__foo
       >>> print (_m_mangled_attr_name ("foo", "_Bar_"))
       _Bar___foo
    """
    if cls_name.startswith ("_") :
        format = "%s__%s"
    else :
        format = "_%s__%s"
    return format % (cls_name, name)
# end def _m_mangled_attr_name

class _class_super_ (object) :
    """Super descriptor usable by classmethods"""

    def __init__ (self, cls) :
        self.cls = cls
    # end def __init__

    def __get__ (self, obj, cls = None) :
        return super (self.cls, cls)
    # end def __get__

# end class _class_super_

class M_M_Class (type) :
    """Metaclass for metaclasses (i.e., a meta-meta-class).
       `M_M_Class` should be used as metaclass for *all* metaclasses.

       It adds private class variables `__m_super` and `__mc_super` containing
       `super (cls)`. This corresponds to `__super` (see
       :class:`~_TFL._Meta.M_Class.M_Autosuper`) but can be used
       inside meta-classes. `__mc_super` can be used in `__new__` methods of
       metaclasses and in classmethods defined in a metaclass.

       This class chooses the most specific metaclass of the `bases`
       (instead of the metaclass of the first element of `bases` as
       standard Python does; for a discussion of this problem, see:
       http://groups.google.com/group/comp.lang.python/tree/browse_frm/thread/2b7a60d08d4a99c4/72346462866e6497).
    """

    def __init__ (cls, name, bases, dict) :
        super (M_M_Class, cls).__init__ (name, bases, dict)
        _c_super_name  = _m_mangled_attr_name ("mc_super", cls.__name__)
        _super_name    = _m_mangled_attr_name ("m_super", cls.__name__)
        _super_value   = super (cls)
        setattr (cls, _super_name,   _super_value)
        setattr (cls, _c_super_name, _class_super_ (cls))
    # end def __init__

    def __call__ (meta, name, bases, dict) :
        meta = meta._most_specific_meta (name, bases, dict)
        cls  = meta.__new__ (meta, name, bases, dict)
        meta.__init__       (cls,  name, bases, dict)
        return cls
    # end def __call__

    def _most_specific_meta (meta, name, bases, dict) :
        result = dict.get ("__metaclass__")
        if result is None :
            result = meta
            if bases is not None :
                for b in bases :
                    b_meta = type (b)
                    if issubclass (result, b_meta) :
                        pass
                    elif issubclass (b_meta, result) :
                        result = b_meta
                    else :
                        raise TypeError \
                            ( "Metatype conflict among bases: %s %s vs. %s %s"
                            % (result, name, b_meta, b)
                            )
        return result
    # end def _most_specific_meta

# end class M_M_Class

class M_Base (type, metaclass = M_M_Class) :
    """Base class of TFL metaclasses.

       It provides a `__m_super` attribute for the meta-classes (for
       cooperative method calls in the meta classes themselves) and
       the class method `New` that creates a descendent class
       augmented by additional attributes and/or methods.
    """

    def _m_mangled_attr_name (cls, name) :
        return _m_mangled_attr_name (name, cls.__name__)
    # end def _m_mangled_attr_name

    def New (cls, name_postfix = None, mangled_attributes = {}, ** kw) :
        """Returns a new class derived from `cls` with `kw` in
           __dict__. If `name_postfix` is given, it is used as postfix
           for the name of the new class.

           For instance::

               Some_Class.New (name_postfix = "X", foo = 42)

           will create a class `Some_Class_X` derived from
           `Some_Class` with a class attribute `foo` with value `42`.
        """
        name = kw.pop ("__name__", cls.__name__)
        new_dict = dict (__module__ = cls.__module__, _real_name = name)
        if name_postfix :
            name = "_".join ((name, name_postfix))
        for attr_name, value in pyk.iteritems (mangled_attributes) :
            new_dict [_m_mangled_attr_name (attr_name, name)] = value
        head_mixins = kw.pop ("head_mixins", ())
        tail_mixins = kw.pop ("tail_mixins", ())
        new_dict.update (kw)
        return type (cls) (name, head_mixins + (cls, ) + tail_mixins, new_dict)
    # end def New

    def _m_combine_nested_class (cls, cn, bases = None, dct = None, ** kw) :
        """Add a class named `cn` derived from all the classes named `cn`
           in `bases` (default `cls.__bases__`) to `cls`.
        """
        if bases is None :
            bases = cls.__bases__
        if dct is None :
            dct   = cls.__dict__
        if cn not in dct :
            c_bases = tuple \
                (  c for c in (getattr (b, cn, None) for b in bases)
                if c is not None
                )
            if c_bases :
                cb0 = c_bases [0]
                d   = dict \
                    ( __module__ = cls.__module__
                    , __outer__  = cls.__name__
                    , ** kw
                    )
                setattr (cls, cn, cb0.__class__ (cn, c_bases, d))
    # end def _m_combine_nested_class

# end class M_Base

class M_Autorename (M_Base) :
    """`TFL.Meta.M_Autorename` renames a class from a unique ugly name, e.g.,
       `_TFL_Meta_Object_` specified in the `class` statement to a possibly
       non-unique but more readable name, e.g., `Object`.

       `M_Autorename` looks for a class attribute `_real_name` that specifies
       the readable name to be used; if `_real_name` exists,
       `M_Autorename` renames the class to `_real_names` value.

       To make the class visible in the defining module under the
       `_real_name` you'll have to add an explicit assignment after
       the class definition.

       Python will use the name following the `class` keyword for
       mangling of private names, i.e., names starting but not ending
       with double underscores, e.g., `__super`. To avoid name clashes
       between private names of classes with the same name (e.g.,
       Package_A.Class and Package_B.Class), define these classes with
       unique names and use `_real_name` to define the name to be used
       by clients of the class.

       If one defines a base class with a generic name, e.g., `Object`,
       `Document`, etc., where the class name is disambiguated by the name of
       the package namespace, one should define `_real_name` for the base
       class.

       The metaclass `M_Autorename` swaps `__name__` and `_real_name`
       before creating the class object. As this occurs after the name
       mangling done by Python (compiler), you can have your cake and
       eat it, too.
    """

    def __new__ (meta, name, bases, dct) :
        real_name = name = str (name)
        if "_real_name" in dct :
            name = str (dct ["_real_name"])
            del dct ["_real_name"]
            if "__qualname__" in dct :
                ### Fix `__qualname__` to refer to `name`
                qn = dct ["__qualname__"]
                dct ["__qualname__"] = ".".join \
                    ((qn.rsplit (".", 1) [0], name)) if "." in qn else name
        dct ["__real_name"] = real_name
        try :
            return meta.__mc_super.__new__ (meta, name, bases, dct)
        except TypeError as exc :
            print ("*" * 3, meta, name)
            for b in bases :
                print (" " * 3, b)
                print \
                    ( " " * 6
                    , "\n       ".join (str (c) for c in b.__mro__ [1:])
                    )
            raise
    # end def __new__

    def __init__ (cls, name, bases, dct) :
        ### Need to pass `cls.__name__` as it might differ from `name`
        cls.__m_super.__init__ (cls.__name__, bases, dct)
    # end def __init__

    def _m_mangled_attr_name (cls, name) :
        return _m_mangled_attr_name (name, cls.__dict__ ["__real_name"])
    # end def _m_mangled_attr_name

# end class M_Autorename

@property
def _super_calling_not_possible (obj) :
    raise NameError \
        ( "Name mangling broken for class `%s` or one of its bases - no super "
          "calling possible. Someone forgot to use `_real_name`!"
        %  obj.__class__.__name__
        )
# end def _super_calling_not_possible

class M_Autosuper (M_Base) :
    """`TFL.Meta.M_Autosuper` adds a class attribute `__super` that can be
       used for cooperative method calls. For use in `__new__` and in
       classmethods, `M_Autosuper` adds a class variable `__c_super`.

       For instance, for a class `Some_Class` derived from `Object`, a
       cooperative method call can be written as::

           self.__super.method (a, b, c)

       instead of::

           super (Some_Class, self).method (a, b, c)

       which avoids the DRY violation of repeating the class name in all
       cooperative method calls.

       A typical usage of cooperative method calls looks like::

           def foo (self, bar, baz) :
               ...
               self.__super.foo (bar, baz)
               ...

           @classmethod
           def bar (cls, baz, qux) :
               ...
               self.__c_super.bar (baz, qux)
               ...

    """

    def __init__ (cls, name, bases, dict) :
        cls.__m_super.__init__ (name, bases, dict)
        _c_super_name  = cls._m_mangled_attr_name ("c_super")
        _super_name    = cls._m_mangled_attr_name ("super")
        _super_value   = super (cls)
        if __debug__ :
            from _TFL.predicate import any_true
            ancestors = cls.__mro__ [1:]
            if (   name == dict.get ("__real_name")
               and any_true
                     ( name == b.__name__ == b.__dict__.get ("__real_name")
                     for b in ancestors
                     )
               ) :
                if 0 :
                    print \
                        ( cls, "has name clash with ancestor"
                        , ", ".join
                            (  str (b) for b in ancestors
                            if name == b.__name__
                                    == b.__dict__.get ("__real_name")
                            )
                        )
                _super_value = _super_calling_not_possible
        setattr (cls, _super_name,   _super_value)
        setattr (cls, _c_super_name, _class_super_ (cls))
    # end def __init__

# end class M_Autosuper

class M_Automethodwrap (M_Base) :
    """Metaclass automatically wrapping the methods specified in the
       dictionary `__autowrap`.

       `__autowrap` must map method names to wrapper function or
       objects (e.g., to staticmethod,
       :class:`~_TFL._Meta.Property.Class_Method` (a TFL replacement
       to classmethod), or
       :class:`~_TFL._Meta.Property.Class_and_Instance_Method`).
    """

    def __init__ (cls, name, bases, dict) :
        cls.__m_super.__init__ (name, bases, dict)
        cls._m_autowrap (bases, dict)
    # end def __init__

    def _m_autowrap (cls, bases, dict) :
        _aw = {}
        bss = list (bases)
        bss.reverse ()
        for b in bss :
            _aw.update (getattr (b, "__autowrap", {}))
        _aw.update (dict.get (cls._m_mangled_attr_name ("autowrap"), {}))
        for name, wrapper in pyk.iteritems (_aw) :
            if TFL.callable (wrapper) :
                method = dict.get (name)
                if method :
                    ### this is tricky: we want to wrap the function found in
                    ### the dictionary, but only if it is an unbound method
                    ###     I didn't find any other way to check for
                    ###     unboundedness than comparing the `im_self` of
                    ###     `getattr (cls, name)` to `None`
                    if getattr (getattr (cls, name), "im_self", 42) is None :
                        try :
                            ### TFL wrappers like to get the class, too
                            setattr (cls, name, wrapper (method, cls))
                        except TypeError :
                            setattr (cls, name, wrapper (method))
        setattr (cls, "__autowrap", _aw)
    # end def _m_autowrap

# end class M_Automethodwrap

class M_Class_SW (M_Autosuper, M_Automethodwrap) :
    """Metaclass combining :class:`~_TFL._Meta.M_Class.M_Autosuper`
       and :class:`~_TFL._Meta.M_Class.M_Automethodwrap`.
    """
# end class M_Class_SW

class M_Class (M_Autorename, M_Class_SW) :
    """`TFL.Meta.M_Class` is the standard metaclass provided by `TFL.Meta`.
       It is used as metaclass by all descendents of `TFL.Meta.Object`. It
       can also be specified as metaclass for classes derived from Python
       builtin types, e.g., `dict`, `list`, or `set`.

       `M_Class` is derived from :class:`~_TFL._Meta.M_Class.M_Autorename`,
       :class:`~_TFL._Meta.M_Class.M_Autosuper`, and
       :class:`~_TFL._Meta.M_Class.M_Automethodwrap` and combines
       the features of these three metaclasses. It thus also serves as an
       example of how cooperative method calls work in practice.
    """
# end class M_Class

import _TFL.predicate

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.M_Class
