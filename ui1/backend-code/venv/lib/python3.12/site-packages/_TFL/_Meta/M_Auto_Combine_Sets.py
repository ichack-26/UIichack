# -*- coding: utf-8 -*-
# Copyright (C) 2010-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Meta.M_Auto_Combine_Sets
#
# Purpose
#    Metaclass autocombining set-valued attributes of a newly defined class
#    with those of its ancestors
#
# Revision Dates
#     5-Jan-2010 (CT) Creation (new implementation)
#    26-Jan-2015 (CT) Add `_sets_to_combine` to `_sets_to_combine`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

"""
Meta class for auto-combining the set-valued attributes mentioned in
`_sets_to_combine` between a class and it's ancestors.

::

    >>> from _TFL.portable_repr import portable_repr
    >>> class A (object, metaclass = M_Auto_Combine_Sets) :
    ...     _sets_to_combine  = ("foo", "bar")
    ...     foo               = set ([1, 2, 3])
    ...
    >>> class B (A) :
    ...     _sets_to_combine  = A._sets_to_combine + ("baz", )
    ...     foo               = set ([5, 4, 3])
    ...     bar               = set ("ab")
    ...
    >>> class C (B) :
    ...     bar               = set ("xyz")
    >>> portable_repr (A.foo), portable_repr (A.bar)
    ('{1, 2, 3}', '{}')
    >>> portable_repr (B.foo), portable_repr (B.bar), portable_repr (B.baz)
    ('{1, 2, 3, 4, 5}', "{'a', 'b'}", '{}')
    >>> portable_repr (C.foo), portable_repr (C.bar), portable_repr(C.baz)
    ('{1, 2, 3, 4, 5}', "{'a', 'b', 'x', 'y', 'z'}", '{}')

"""

from   _TFL                import TFL
import _TFL._Meta.M_Class

import itertools

class M_Auto_Combine_Sets (TFL.Meta.M_Base) :
    """Meta class for auto-combining the set-valued attributes mentioned in
       `_sets_to_combine` between a class and it's ancestors.
    """

    _sets_to_combine = ("_sets_to_combine", )

    def __init__ (cls, name, bases, dict) :
        cls._m_combine_sets    (bases, dict)
        cls.__m_super.__init__ (name, bases, dict)
    # end def __init__

    def _m_combine_sets (cls, bases, dict) :
        for name in cls._sets_to_combine :
            setattr \
                ( cls, name
                , set
                    ( itertools.chain
                        (    getattr (cls, name, set ())
                        , * (getattr (bas, name, set ()) for bas in bases)
                        )
                    )
                )
    # end def _m_combine_sets

# end class M_Auto_Combine_Sets

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.M_Auto_Combine_Sets
