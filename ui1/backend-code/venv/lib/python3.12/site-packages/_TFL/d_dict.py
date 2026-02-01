# -*- coding: utf-8 -*-
# Copyright (C) 1999-2008 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    d_dict
#
# Purpose
#    Function returning a dictionary allowing
#    - to derive a new dictionary from any number of existing dictionaries
#    - to initialize a new dictionary with keyword syntax (no quotes
#      necessary around keys)
#
# Revision Dates
#    11-Sep-2001 (CT) Creation (factored from `D_Dict`)
#    16-Jan-2003 (CT) Aesthetics
#     6-Jun-2008 (CT) `dict_from_named_objects` added
#    ««revision-date»»···
#--

from _TFL import TFL

def d_dict (* ancestors, ** kw) :
    """Returns a dictionary,

       `d_dict` adds just a bit of syntactic sugar for the initialization of
       dictionary objects:

       - a new dictionary can be initialized with the contents of any number
         of existing dictionaries (the values from the existing dictionaries
         are copied during the construction of the new dictionary)

       - values for the new dictionary can be specified with keyword notation
         -- this saves the quotes for string-valued keys

       For instance, given two dictionaries `d1` and `d2` as

           d1 = {"spam" : 2, "eggs" : 3}
           d2 = d_dict (ham = 1, brunch = "Bacon")

       `d3` can be defined as

           d3 = d_dict (d1, d2, foo = "bar", spam = 0)

       instead of

           d3 = {"foo" : "bar", "spam" : 0}
           d3.update (d2)
           d3.update (d1)

       or even (more verbose, but probably with the intended effect):

           d3 = {}
           d3.update (d2)
           d3.update (d1)
           d3.update ({"foo" : "bar", "spam" : 0})
    """
    result = {}
    if ancestors :
        ancestors = list  (ancestors)
        ancestors.reverse ()
        map               (result.update, ancestors)
    result.update (kw)
    return result
# end def d_dict

def dict_from_named_objects (* args, ** kw) :
    Dict = kw.pop ("dict", dict)
    name = kw.pop ("name", "name")
    assert not kw
    return Dict ((getattr (a, name), a) for a in args)
# end def dict_from_named_objects

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.d_dict
