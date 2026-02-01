# -*- coding: utf-8 -*-
# Copyright (C) 2008-2019 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Re_Filter
#
# Purpose
#    Provide classes for filtering with regexes
#
# Revision Dates
#     6-May-2008 (CT) Creation
#    29-Aug-2008 (CT) s/super(...)/__super/
#    15-Mar-2009 (CT) `Re_Filter_OA_Opt` changed to accept `attr` spec in
#                     `__init__`
#     4-Jan-2010 (CT) Option classes based on TFL.CAO instead of
#                     TFL.Command_Line
#    16-Oct-2015 (CT) Add `__future__` imports
#    19-Aug-2019 (CT) Use `print_prepr`
#    ««revision-date»»···
#--

from    _TFL.Regexp import *
import  _TFL.CAO
import  _TFL.Filter

class Re_Filter (TFL.Filter) :
    """Return all items of an iterable of strings that match a Regexp.

       >>> f = Re_Filter ("(foo|bar)")
       >>> g = ~ f
       >>> l = ["fool", "abc", "barroom", "fubar", "zoppl", "sucks"]
       >>> _show (f.filter (l))
       ['fool', 'barroom', 'fubar']
       >>> _show (g.filter (l))
       ['abc', 'zoppl', 'sucks']
    """

    def __new__ (cls, * args, ** kw) :
        return cls.__c_super.__new__ (cls, None)
    # end def __new__

    def __init__ (self, pattern, flags = 0, quote = 0) :
        if isinstance (pattern, Regexp) :
            regexp = pattern
        else :
            regexp = Regexp (pattern, flags, quote)
        self._regexp = regexp
        self.__super.__init__ (self.match)
    # end def __init__

    def match (self, item) :
        return self._regexp.search (item)
    # end def match

# end class Re_Filter

class Re_Filter_OA (Re_Filter) :
    """Return all objects with a specific attributes matching a Regexp."""

    def __init__ (self, attr, pattern, flags = 0, quote = 0) :
        self._attr = attr
        self.__super.__init__ (pattern, flags = 0, quote = 0)
    # end def __init__

    def match (self, obj) :
        return self.__super.match (getattr (obj, self._attr))
    # end def match

# end class Re_Filter_OA

class _Re_Filter_Arg_ (TFL.CAO.Str_AS) :
    """Argument or option defining a filter using a Re_Filter"""

    _real_name = "Re_Filter"

    def __init__ (self, ** kw) :
        kw.setdefault         ("auto_split", """\n""")
        self.__super.__init__ (** kw)
    # end def __init__

    def combine (self, values) :
        if len (values) > 1 :
            return TFL.Filter_And (* values)
        elif values :
            return values [0]
    # end def combine

    def cook (self, value, cao = None) :
        if value :
            return Re_Filter (value)
    # end def cook

# end class _Re_Filter_Arg_

class _Re_Filter_Arg_OA_ (_Re_Filter_Arg_) :
    """Argument or option defining a filter using Re_Filter_OA"""

    _real_name = "Re_Filter_OA"

    def __init__ (self, ** kw) :
        self.attr_to_match = kw.pop ("attr", None)
        self.__super.__init__ (** kw)
    # end def __init__

    def cook (self, value, cao = None) :
        if value :
            if ":" in value :
                attr, pattern = value.split (":", 1)
            elif self.attr_to_match :
                attr    = self.attr_to_match
                pattern = value
            else :
                raise TFL.CAO.Err \
                    ( "Specify object attribute to which filter "
                      "`%s` should apply"
                    % value
                    )
            return Re_Filter_OA (attr, pattern)
    # end def cook

# end class _Re_Filter_Arg_OA_

def _show (it) :
    from _TFL.portable_repr import print_prepr
    print_prepr (list (it))
# end def _show

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Re_Filter
