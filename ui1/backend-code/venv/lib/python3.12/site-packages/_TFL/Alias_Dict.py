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
#    TFL.Alias_Dict
#
# Purpose
#    Dictionary with support for aliases for the keys
#
# Revision Dates
#    30-Sep-2009 (CT) Creation
#    23-May-2013 (CT) Use `TFL.Meta.BaM` for Python-3 compatibility
#     2-Jun-2013 (CT) Add `copy`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL                  import TFL
from   _TFL.pyk              import pyk
import _TFL._Meta.M_Class

class Alias_Dict (dict, metaclass = TFL.Meta.M_Class) :
    """A dictionary with support for aliases for the keys.

       >>> ad = Alias_Dict (a = 1, b = 42, z = 137)
       >>> sorted (pyk.iteritems (ad))
       [('a', 1), ('b', 42), ('z', 137)]
       >>> 5 in ad
       False
       >>> ad.add_alias (5, "z")
       >>> 5 in ad
       True
       >>> sorted (pyk.iteritems (ad))
       [('a', 1), ('b', 42), ('z', 137)]
    """

    def __init__ (self, * args, ** kw) :
        self.__super.__init__ (* args, ** kw)
        self._alias_names = {}
    # end def __init__

    def add_alias (self, alias_name, real_name) :
        self._alias_names [alias_name] = real_name
    # end def add_alias

    def copy (self, ** kw) :
        result = self.__class__ (self, ** kw)
        result._alias_names = dict (self._alias_names)
        return result
    # end def copy

    def get (self, key, default = None) :
        key = self._alias_names.get (key, key)
        return self.__super.get (key, default)
    # end def get

    def __contains__ (self, key) :
        key = self._alias_names.get (key, key)
        return self.__super.__contains__ (key)
    # end def __contains__

    def __getitem__ (self, key) :
        key = self._alias_names.get (key, key)
        return self.__super.__getitem__ (key)
    # end def __getitem__

# end class Alias_Dict

if __name__ != "__main__" :
    TFL._Export ("Alias_Dict")
### __END__ TFL.Alias_Dict
