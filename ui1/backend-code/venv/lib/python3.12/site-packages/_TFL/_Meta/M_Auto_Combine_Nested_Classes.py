# -*- coding: utf-8 -*-
# Copyright (C) 2011-2015 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.Meta.M_Auto_Combine_Nested_Classes
#
# Purpose
#    Meta class for auto-combining the class-valued attributes mentioned in
#    `_nested_classes_to_combine` between a class and it's ancestors.
#
# Revision Dates
#    10-Feb-2011 (CT) Creation
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL                import TFL
import _TFL._Meta.M_Class

class M_Auto_Combine_Nested_Classes (TFL.Meta.M_Base) :
    """Meta class for auto-combining the class-valued attributes mentioned in
       `_nested_classes_to_combine` between a class and it's ancestors.
    """

    _nested_classes_to_combine = ()

    def __init__ (cls, name, bases, dct) :
        for cn in cls._nested_classes_to_combine :
            cls._m_combine_nested_class (cn, bases, dct)
        cls.__m_super.__init__ (name, bases, dct)
    # end def __init__

# end class M_Auto_Combine_Nested_Classes

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.M_Auto_Combine_Nested_Classes
