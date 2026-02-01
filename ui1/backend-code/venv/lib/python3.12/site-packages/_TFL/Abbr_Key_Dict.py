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
#    TFL.Abbr_Key_Dict
#
# Purpose
#    Dictionary supporting unique abbreviations of a key to be used as
#    arguments for `__getitem__`
#
# Revision Dates
#    26-Feb-1999 (CT) Creation
#     8-Apr-1999 (CT) `__init__` added
#    15-Dec-1999 (CT) Inherit from `D_Dict` instead of `UserDict`
#    11-Jun-2003 (CT) s/!= None/is not None/
#    19-Apr-2004 (CT) `really_has_key` added
#    28-Sep-2004 (CT) Use `isinstance` instead of type comparison
#    22-Mar-2005 (MG) Remove `D_Dict` dependency
#    24-Mar-2005 (CT) Doctest added
#    24-Mar-2005 (CT) Small changes in MGs changes
#    24-Mar-2005 (CT) Moved into package `TFL`
#    29-Aug-2008 (CT) s/super(...)/__super/
#    23-May-2013 (CT) Use `TFL.Meta.BaM` for Python-3 compatibility
#    ««revision-date»»···
#--

from   _TFL      import TFL
from   _TFL.pyk  import pyk

import _TFL.predicate
import _TFL._Meta.M_Class

class Ambiguous_Key (KeyError) :
    pass
# end class Ambiguous_Key

class Abbr_Key_Dict (dict, metaclass = TFL.Meta.M_Class) :
    """Dictionary supporting unique abbreviations of a key to be used as
       arguments for `__getitem__`.
    """

    def __getitem__ (self, key) :
        matching = self.matching_keys (key)
        if len (matching) == 1 :
            return self.__super.__getitem__ (matching [0])
        elif not matching :
            raise KeyError (key)
        else :
            raise Ambiguous_Key \
                ("%s matches more than 1 key: %s" % (key, matching))
    # end def __getitem__

    def matching_keys (self, abbr) :
        """Returns a list of all keys matching `abbr` if any."""
        if abbr in self :
            return [abbr]
        elif isinstance (abbr, str) :
            return TFL.matches (TFL.sorted (pyk.iterkeys (self)), abbr)
        return []
    # end def matching_keys

    def matching_key (self, abbr) :
        """Returns the key matching `abbr` if any."""
        matching = self.matching_keys (abbr)
        if len (matching) == 1 :
            return matching [0]
    # end def matching_key

    def has_key (self, key) :
        return len (self.matching_keys (key)) == 1
    # end def has_key

    def really_has_key (self, key) :
        return key in self
    # end def really_has_key

# end class Abbr_Key_Dict

__test__ = dict \
    ( test = """
    >>> d = Abbr_Key_Dict (a = 1, ab = 2, abc = 3, bertie = 4, bingo = 5)
    >>> d ["a"], d ["ab"], d ["abc"]
    (1, 2, 3)
    >>> d ["be"], d ["ber"], d ["bertie"]
    (4, 4, 4)
    >>> with expect_except (Ambiguous_Key) :
    ...      d ["b"] # doctest:+ELLIPSIS
    Ambiguous_Key: "b matches more than 1 key: ['bertie', 'bingo']"
    >>> d ["berties"]
    Traceback (most recent call last):
      ...
    KeyError: 'berties'
    >>> d.matching_keys ("a")
    ['a']
    >>> d.matching_keys ("b")
    ['bertie', 'bingo']
    >>> d.matching_keys ("be")
    ['bertie']
    >>> "a" in d, d.has_key ("a")
    (True, True)
    >>> "ab" in d, d.has_key ("ab")
    (True, True)
    >>> "abc" in d, d.has_key ("abc")
    (True, True)
    >>> "b" in d, d.has_key ("b")
    (False, False)
    >>> "be" in d, d.has_key ("be")
    (False, True)
    >>> "bertie" in d, d.has_key ("bertie")
    (True, True)
    """
    )

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Abbr_Key_Dict
