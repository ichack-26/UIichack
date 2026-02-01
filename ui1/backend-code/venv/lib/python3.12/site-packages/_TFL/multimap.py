# -*- coding: utf-8 -*-
# Copyright (C) 2006-2013 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.multimap
#
# Purpose
#    Provide multimap (a dictionary of lists or dicts)
#
# Revision Dates
#    13-Mar-2006 (CT) Creation
#    14-Nov-2006 (CT) `mm_set` added
#    20-Mar-2013 (CT) Derive from `TFL.defaultdict_cb`, not `._defaultdict_`
#    16-Apr-2013 (CT) Add `mm_dict_mm_dict`
#    ««revision-date»»···
#--

from   _TFL import      TFL
import _TFL.defaultdict

class mm_dict (TFL.defaultdict_cb) :
    """`defaultdict` with `dict` as `default_factory`.

       >>> mmd = mm_dict (a = {1 : 2, 2 : 4}, b = {42 : 1})
       >>> sorted (mmd.items ())
       [('a', {1: 2, 2: 4}), ('b', {42: 1})]
       >>> "a" in mmd, "d" in mmd
       (True, False)
       >>> sorted (mmd ["a"]), sorted (mmd ["d"])
       ([1, 2], [])
       >>> "a" in mmd, "d" in mmd
       (True, True)
    """

    default_factory = dict

# end class mm_dict

class mm_list (TFL.defaultdict_cb) :
    """`defaultdict` with `list` as `default_factory`.

       >>> mml = mm_list (a = [1], b = [2], c = [42])
       >>> sorted (mml.items ())
       [('a', [1]), ('b', [2]), ('c', [42])]
       >>> "a" in mml, "d" in mml
       (True, False)
       >>> mml ["a"], mml ["d"]
       ([1], [])
       >>> "a" in mml, "d" in mml
       (True, True)
    """

    default_factory = list

# end class mm_list

class mm_set (TFL.defaultdict_cb) :
    """`defaultdict` with `set` as `default_factory`."""

    default_factory = set

# end class mm_set

class mm_dict_mm_dict (TFL.defaultdict_cb) :
    """`defaultdict` with `mm_dict` as `default_factory`."""

    default_factory = mm_dict

# end class mm_dict_mm_dict

class mm_dict_mm_list (TFL.defaultdict_cb) :
    """`defaultdict` with `mm_list` as `default_factory`."""

    default_factory = mm_list

# end class mm_dict_mm_list

multimap = mm_list

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.multimap
