# -*- coding: utf-8 -*-
# Copyright (C) 2016 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.Meta.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.Meta.Def_Map
#
# Purpose
#    Map where methods/properties are defined in inheritance hierarchy
#
# Revision Dates
#    30-Jul-2016 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL                       import TFL
from   _TFL.pyk                   import pyk
from   _TFL.predicate             import uniq

import _TFL._Meta.Object
import _TFL.defaultdict

from   itertools                  import chain as ichain

class _Def_Map_ (TFL.Meta.Object) :
    """Map where methods/properties are defined in inheritance hierarchy.

    >>> DM = Def_Map
    >>> DM.show_class_map (DM.__class__)
    LET            : _TFL._Meta.Object.Object
    __autowrap     : _TFL._Meta.Object.Object, Def_Map._Def_Map_
    __real_name    : _TFL._Meta.Object.Object, Def_Map._Def_Map_
    _check_MRO     : _TFL._Meta.Object._TFL_Meta_Object_Root_
    _of_bases      : Def_Map._Def_Map_
    _of_class      : Def_Map._Def_Map_
    of_class       : Def_Map._Def_Map_
    of_feature     : Def_Map._Def_Map_
    pop_to_self    : _TFL._Meta.Object.Object
    show_class_map : Def_Map._Def_Map_

    >>> DM.show_class_map (DM.__class__.__class__)
    New                         : _TFL._Meta.M_Class.M_Base
    _M_Automethodwrap__mc_super : _TFL._Meta.M_Class.M_Automethodwrap
    _M_Autorename__mc_super     : _TFL._Meta.M_Class.M_Autorename
    _M_Autosuper__mc_super      : _TFL._Meta.M_Class.M_Autosuper
    _M_Base__mc_super           : _TFL._Meta.M_Class.M_Base
    _M_Class_SW__mc_super       : _TFL._Meta.M_Class.M_Class_SW
    _M_Class__mc_super          : _TFL._Meta.M_Class.M_Class
    _m_autowrap                 : _TFL._Meta.M_Class.M_Automethodwrap
    _m_combine_nested_class     : _TFL._Meta.M_Class.M_Base
    _m_mangled_attr_name        : _TFL._Meta.M_Class.M_Base, _TFL._Meta.M_Class.M_Autorename
    mro                         : type

    """

    def __init__ (self) :
        self._map = {}
    # end def __init__

    def of_class (self, cls) :
        """Return feature map of `cls`.

               name --> [least-specific def, ..., most-specific def]
        """
        map = self._map
        try :
            result = map [cls]
        except KeyError :
            result = map [cls] = self._of_class (cls)
        return result
    # end def of_class

    def of_feature (self, cls, name) :
        """Return list of classes in mro of `cls` defining `name`, ordered from
           least-specific to most-specific.
        """
        try :
            result = self._map [cls] [name]
        except KeyError :
            result = []
            for c in reversed (cls.__mro__) :
                if name in c.__dict__ :
                    result.append (c)
        return result
    # end def of_feature

    def show_class_map (self, cls) :
        """Print feature map of `cls`."""
        map = self.of_class (cls)
        l   = max (len (k) for k in map)
        for k, vs in sorted (pyk.iteritems (map)) :
            print ("%*s : %s" % (-l, k, ", ".join (vs)))
    # end def show_class_map

    def _of_bases (self, cls) :
        result = TFL.defaultdict (list)
        for b in reversed (cls.__bases__) :
            for k, cs in pyk.iteritems (self.of_class (b)) :
                result [k] = list (uniq (ichain (result [k], cs)))
        return result
    # end def _of_bases

    def _of_class (self, cls) :
        name   = repr (cls).split ("'") [1]
        result = self._of_bases (cls)
        for k, v in pyk.iteritems (cls.__dict__) :
            is_thunder = k.startswith ("__") and k.endswith ("__")
            is_super   = k.endswith (("__super", "__c_super", "__m_super"))
            if not (is_thunder or is_super) :
                result [k].append (name)
        return result
    # end def _of_class

    def __getitem__ (self, key) :
        if isinstance (key, type) :
            return self.of_class (key)
        else :
            cls, name = key
            return self.of_feature (cls, name)
    # end def __getitem__

Def_Map = _Def_Map_ () # end class

if __name__ != "__main__" :
    TFL.Meta._Export ("Def_Map")
### __END__ TFL.Meta.Def_Map
