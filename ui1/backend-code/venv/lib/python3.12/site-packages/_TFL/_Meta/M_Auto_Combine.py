# -*- coding: utf-8 -*-
# Copyright (C) 2003-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Meta.M_Auto_Combine
#
# Purpose
#    Metaclass for autocombining lists, dictionaries and sets between a class
#    and its ancestors
#
# Revision Dates
#    13-Jan-2003 (CT)  Creation (factored from TOM.Meta.ATS_Type.py)
#     4-Feb-2003 (CT)  `_lists_to_combine` moved to `ATS_Type`
#    20-Feb-2003 (CT)  `_dicts_to_combine` added
#    20-Feb-2003 (CT)  Empty defaults for `_lists_to_combine` and
#                      `_dicts_to_combine` added
#     1-Apr-2003 (CT)  s/M_Class/M_Class_SW/ (optimize, optimize)
#     7-Jul-2003 (CED) `_m_combine_lists` fixed
#    23-Jul-2004 (CT)  `TFL.Meta.M_Auto_Combine_Dicts` and
#                      `TFL.Meta.M_Auto_Combine_Lists` factored
#    18-Feb-2005 (CT)  Moved to `TFL.Meta`
#    13-Jul-2005 (CED) `M_Auto_Combine_Sets` added to bases
#     3-Feb-2009 (CT)  Documentation added
#    28-Sep-2012 (CT)  Add `M_Auto_Combine_Nested_Classes`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL                import TFL

import _TFL._Meta.M_Auto_Combine_Dicts
import _TFL._Meta.M_Auto_Combine_Lists
import _TFL._Meta.M_Auto_Combine_Nested_Classes
import _TFL._Meta.M_Auto_Combine_Sets
import _TFL._Meta.M_Class

class M_Auto_Combine ( TFL.Meta.M_Auto_Combine_Dicts
                     , TFL.Meta.M_Auto_Combine_Lists
                     , TFL.Meta.M_Auto_Combine_Nested_Classes
                     , TFL.Meta.M_Auto_Combine_Sets
                     , TFL.Meta.M_Class
                     ) :
    pass
# end class M_Auto_Combine

__doc__ = """
Meta class for auto-combining

* the list-attributes mentioned in `_lists_to_combine`
  (see :class:`~_TFL._Meta.M_Auto_Combine_Lists.M_Auto_Combine_Lists`)

* the dict-attributes mentioned in `_dicts_to_combine`
  (see :class:`~_TFL._Meta.M_Auto_Combine_Dicts.M_Auto_Combine_Dicts`)

* the class-valued--attributes mentioned in `_nested_classes_to_combine`
  (see :class:`~_TFL._Meta.M_Auto_Combine_Nested_Classes.M_Auto_Combine_Nested_Classes`)

* the set-attributes  mentioned in `_sets_to_combine`
  (see :class:`~_TFL._Meta.M_Auto_Combine_Sets.M_Auto_Combine_Sets`)

between a class and its ancestors.
"""

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.M_Auto_Combine
