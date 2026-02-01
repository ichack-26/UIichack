# -*- coding: utf-8 -*-
# Copyright (C) 1999-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.NO_List
#
# Purpose
#    List of named objects
#
# Revision Dates
#     5-Oct-1999 (CT)  Creation
#     3-Feb-2000 (MG)  `__getslice__` added
#    28-Mar-2000 (CT)  `__add__` changed to allow addition of normal lists and
#                      tuples to NO_Lists
#    28-Jun-2000 (CT)  `insert` changed to allow `index == None`
#    30-Jun-2000 (CT)  `keys` added
#     8-Aug-2000 (CT)  `get` added
#    16-Mar-2001 (CT)  `Ordered_Set` factored
#    16-Mar-2001 (CT)  `update` added
#    21-Mar-2001 (MG)  Redefine `_check_value` because TTPbuild currently uses
#                      objects with the same name !
#    11-Jun-2003 (CT)  s/== None/is None/
#    11-Jun-2003 (CT)  s/!= None/is not None/
#    20-Nov-2003 (CT)  Calls to `self.__len__` removed
#    28-Sep-2004 (CT)  Use `isinstance` instead of type comparison
#     8-Nov-2006 (PGO) Inheritance changed
#     7-Nov-2007 (CT)  Use `Getter` instead of `Attribute`
#    29-Aug-2008 (CT)  s/super(...)/__m_super/
#    29-May-2009 (MG) `*items`, `*keys`, and `*values` added
#     3-Nov-2009 (CT)  Usage of `has_key` removed
#     9-Sep-2010 (MG) `M_Name_Dict`, `Name_Dict` changed to allow overriding
#                     the `key_attr_name`
#    23-May-2013 (CT) Use `TFL.Meta.BaM` for Python-3 compatibility
#    ««revision-date»»···
#--

from   _TFL                 import TFL
from   _TFL.pyk             import pyk

import _TFL._Meta.M_Class
import _TFL.Accessor
import _TFL.Decorator
import _TFL.Ordered_Set

class M_Name_Dict (TFL.Meta.M_Class) :

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        for method_name in dct.get ("_convert_methods", ()) :
            setattr \
                ( cls, method_name
                , cls.name_of_key (getattr (cls, method_name))
                )
    # end def __init__

    @staticmethod
    @TFL.Decorator
    def name_of_key (method) :
        def _ (self, key, * args, ** kw) :
            if not isinstance (key, pyk.string_types) :
                key = getattr (key, self.key_attr_name)
            return method (self, key, * args, ** kw)
        return _
    # end def name_of_key

# end class M_Name_Dict

class Name_Dict (dict, metaclass = M_Name_Dict) :

    key_attr_name    = "name"
    _convert_methods = \
        ("get", "pop", "__getitem__", "__delitem__", "__setitem__")

# end class Name_Dict

class NO_List (TFL.Ordered_Set):
    """List of named objects. Access to the list elements is provided by
       numerical index and by name.

       Each element of the list must provide an attribute `name` of a
       non-numeric type.
    """

    _reverse_mapping_cls = Name_Dict
    _cannot_hold         = pyk.string_types

    def has_key (self, name) :
        return name in self.index_dict
    # end def has_key

    def iteritems (self) :
        for i in self :
            yield (i.name, i)
    # end def iteritems

    def iterkeys (self) :
        for i in self :
            yield i.name
    # end def iteritems

    def itervalues (self) :
        yield from self 
    # end def iter

    def items  (self) : return list (self.iteritems  ())
    def keys   (self) : return list (self.iterkeys   ())
    def values (self) : return list (self.itervalues ())

    def sort (self, cmp = None, key = None, reverse = False) :
        if key is None :
            key = TFL.Getter.name
        self.__super.sort (cmp = cmp, key = key, reverse = reverse)
    # end def sort

    def __getitem__ (self, name_or_index) :
        if isinstance (name_or_index, int) :
            index = name_or_index
        else :
            index = self.index_dict [name_or_index]
        return self.__super.__getitem__ (index)
    # end def __getitem__

# end class NO_List

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.NO_List
