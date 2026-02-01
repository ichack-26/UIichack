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
#    TFL.Meta.M_Auto_Combine_Dicts
#
# Purpose
#    Metaclass autocombining dictionaries of newly defined class with those
#    of its ancestors
#
# Revision Dates
#    23-Jul-2004 (CT) Creation (factored from TOM.Meta.M_Auto_Combine)
#    29-Aug-2008 (CT)  s/super(...)/__m_super/
#     2-Feb-2009 (CT) s/_M_Type_/M_Base/
#     3-Feb-2009 (CT) Documentation improved
#     5-Jan-2010 (CT) Use `itertools.chain` instead of `TFL.d_dict`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

"""
Meta class for auto-combining the dict-valued attributes mentioned in
`_dicts_to_combine` between a class and it's ancestors.

::

    >>> from _TFL.portable_repr import portable_repr
    >>> class A (object, metaclass = M_Auto_Combine_Dicts) :
    ...     _dicts_to_combine = ("foo", "bar")
    ...     bar               = dict (x = 1, y = 2)
    ...
    >>> class B (object) :
    ...     foo               = dict (u = 1, v = "a")
    ...     bar               = dict (y = 3, z = 42)
    ...
    >>> class BA (B, A) :
    ...     _dicts_to_combine = A._dicts_to_combine + ("baz", )
    ...
    >>> class AB (A, B) :
    ...     foo               = dict (v = "b", w = "a")
    ...     bar               = dict (x = "z", z = -42)
    >>> portable_repr (A.foo), portable_repr (A.bar)
    ('{}', "{'x' : 1, 'y' : 2}")
    >>> portable_repr (B.foo), portable_repr (B.bar)
    ("{'u' : 1, 'v' : 'a'}", "{'y' : 3, 'z' : 42}")
    >>> portable_repr (BA.foo), portable_repr (BA.bar), portable_repr (BA.baz)
    ("{'u' : 1, 'v' : 'a'}", "{'x' : 1, 'y' : 3, 'z' : 42}", '{}')
    >>> portable_repr (AB.foo), portable_repr (AB.bar)
    ("{'u' : 1, 'v' : 'b', 'w' : 'a'}", "{'x' : 'z', 'y' : 2, 'z' : -42}")

"""

from   _TFL                import TFL
from   _TFL.pyk            import pyk

import _TFL._Meta.M_Class

import itertools

class M_Auto_Combine_Dicts (TFL.Meta.M_Base) :
    """Meta class for auto-combining the dict-valued attributes mentioned in
       `_dicts_to_combine` between a class and it's ancestors.
    """

    _dicts_to_combine = ()

    def __init__ (cls, name, bases, dct) :
        cls._m_combine_dicts   (bases, dct)
        cls.__m_super.__init__ (name, bases, dct)
    # end def __init__

    def _m_combine_dicts (cls, bases, dct) :
        for name in cls._dicts_to_combine :
            setattr \
                ( cls, name
                , dict
                    ( itertools.chain
                        ( * (   pyk.iteritems (getattr (c, name, {}))
                            for c in reversed ((cls, ) + bases)
                            )
                        )
                    )
                )
    # end def _m_combine_dicts

# end class M_Auto_Combine_Dicts

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.M_Auto_Combine_Dicts
