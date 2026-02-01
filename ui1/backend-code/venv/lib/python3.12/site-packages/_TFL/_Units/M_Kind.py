# -*- coding: utf-8 -*-
# Copyright (C) 2004-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Units.M_Kind
#
# Purpose
#    Meta class for TFL.Units.Kind
#
# Revision Dates
#     9-Aug-2004 (CT) Creation
#    29-Aug-2008 (CT) s/super(...)/__m_super/
#    17-Feb-2017 (CT) Add `aliases`
#    17-Feb-2017 (CT) Add `_Unit_Descriptor_`
#     5-Jun-2020 (CT) Add guard for `u.abbr` to `M_Kind.__init__`
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.M_Class
import _TFL._Units.Unit

class _Unit_Descriptor_ (object) :
    """Unit descriptor for Unit.Kind classes.

    Accessed through a class, Unit_Descriptor allows creation of instances with
    the corresponding unit as well as operations like::

        Length.kilometer / Time.hour

    Accessed through an instance, Unit_Descriptor converts that instance's
    value to the corresponding unit.
    """

    def __init__ (self, unit) :
        self.unit = unit
    # end def __init__

    def __get__ (self, obj, cls) :
        if obj is None :
            unit = self.unit
            return unit.Bound_Unit (cls, unit)
        return self.unit.from_base (obj.value)
    # end def __get__

# end class _Unit_Descriptor_

class M_Kind (TFL.Meta.M_Class) :
    """Meta class for TFL.Units.Kind"""

    def __init__ (cls, name, bases, dict) :
        cls.__m_super.__init__ (name, bases, dict)
        cls.u_map = u_map = {}
        cls.units = units = {}
        for u in (cls.base_unit, ) + tuple (cls._units) :
            if u :
                units [u.name] = u_map [u.name] = u
                if u.abbr :
                    u_map [u.abbr] = u
                for ali in u.aliases :
                    u_map [ali] = u
                setattr (cls, u.name, _Unit_Descriptor_ (u))
    # end def __init__

# end class M_Kind

if __name__ != "__main__" :
    TFL.Units._Export ("M_Kind")
### __END__ TFL.Units.M_Kind
