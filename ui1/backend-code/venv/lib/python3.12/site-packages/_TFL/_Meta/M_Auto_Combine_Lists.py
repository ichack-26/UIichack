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
#    TFL.Meta.M_Auto_Combine_Lists
#
# Purpose
#    Meta class for auto-combining the list-valued attributes mentioned in
#    `_lists_to_combine` between a class and it's ancestors.
#
# Revision Dates
#    23-Jul-2004 (CT) Creation (factored from TOM.Meta.M_Auto_Combine)
#     2-Jul-2006 (MG) Unnecessary imports removed
#    14-Dec-2007 (MG) Import changed
#    29-Aug-2008 (CT) s/super(...)/__m_super/
#     2-Feb-2009 (CT) s/_M_Type_/M_Base/
#     3-Feb-2009 (CT) Documentation improved
#     5-Jan-2010 (CT) Use `uniq` instead of `set` and `sorted`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

"""
Meta class for auto-combining the list-valued attributes mentioned in
`_lists_to_combine` between a class and it's ancestors.

::

    >>> class A (object, metaclass = M_Auto_Combine_Lists) :
    ...     _lists_to_combine = ("foo", "bar", "qux")
    ...     bar               = [1, 3]
    ...     qux               = [(0, ), (1, )]
    ...
    >>> class B (A) :
    ...     _lists_to_combine = A._lists_to_combine + ("baz", )
    ...     foo               = [0]
    ...     bar               = [-1, 1, 2, 42]
    ...     qux               = [(2, ), (0, )]
    ...
    >>> A.foo, A.bar, A.qux
    ([], [1, 3], [(0,), (1,)])
    >>> B.foo, B.bar, B.qux, B.baz
    ([0], [1, 3, -1, 2, 42], [(0,), (1,), (2,)], [])
    >>> id (B.qux [0]) == id (A.qux [0])
    True
"""

from   _TFL                import TFL
import _TFL._Meta.M_Class
from   _TFL.predicate      import uniq

import itertools

class M_Auto_Combine_Lists (TFL.Meta.M_Base) :
    """Meta class for auto-combining the list-valued attributes mentioned in
       `_lists_to_combine` between a class and it's ancestors.

       Beware:
       - The elements of the `_lists_to_combine` must be hashable.
    """

    _lists_to_combine = ()

    def __init__ (cls, name, bases, dict) :
        cls._m_combine_lists   (bases, dict)
        cls.__m_super.__init__ (name, bases, dict)
    # end def __init__

    def _m_combine_lists (cls, bases, dict) :
        for name in cls._lists_to_combine :
            setattr \
                ( cls, name
                , list
                    ( uniq
                        ( itertools.chain
                            ( * (   getattr (c, name, [])
                                for c in reversed ((cls, ) + bases)
                                )
                            )
                        )
                    )
                )
    # end def _m_combine_lists

# end class M_Auto_Combine_Lists

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.M_Auto_Combine_Lists
