# -*- coding: utf-8 -*-
# Copyright (C) 2017-2018 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.Q_Exp_CAO
#
# Purpose
#    CAO argument or option with a query-expression value
#
# Revision Dates
#    17-Aug-2017 (CT) Creation
#     2-Sep-2017 (CT) Move import of `TFL.Q_Exp` into lazy property
#                     * avoid circular imports
#    26-Apr-2018 (CT) Add support for value ranges
#    ««revision-date»»···
#--

from   _TFL                       import TFL
from   _TFL._Meta.Once_Property   import Once_Property

import _TFL.CAO

import itertools

class _Q_Exp_Arg_ (TFL.CAO.Opt.Str) :
    """Argument or option with a query-expression value"""

    _real_name     = "Q_Exp"

    auto_split     = ";"
    description    = "Filter all values that don't satisfy the criteria"
    name           = "qx"

    _fct_set       = set (["CONTAINS", "ENDSWITH", "STARTSWITH"])
    _op_map        = dict \
        ( EQ       = "__eq__"
        , GE       = "__ge__"
        , GT       = "__gt__"
        , LE       = "__le__"
        , LT       = "__lt__"
        , NE       = "__ne__"
        )

    @Once_Property
    def Q (self) :
        from _TFL.Q_Exp import Q as result
        return result
    # end def Q

    def cook (self, value, cao = None) :
        Q = self.Q
        name, op_key, v = tuple (a.strip () for a in value.split (",", 3))
        vs              = tuple (x.strip () for x in v.split ("|"))
        try :
            op_name = self._op_map [op_key]
        except KeyError :
            if op_key in self._fct_set :
                op_name = op_key
            else :
                raise ValueError \
                    ( "Unknown operator %s in query expression %s;"
                      "\n  specify one of: %s"
                    % ( op_key, value
                      , sorted (itertools.chain (self._fct_set, self._op_map))
                      )
                    )
        else :
            def _convert_1 (v) :
                try :
                    return int (v, 0)
                except ValueError :
                    return float (v)
            def _convert (vs) :
                pat = self.range_pat
                for v in vs :
                    if v and pat.match (v) :
                        head  = _convert_1 (pat.head)
                        tail  = _convert_1 (pat.tail) + 1
                        delta = _convert_1 (pat.delta) if pat.delta else 1
                        yield from range (head, tail, delta) 
                    else :
                        yield _convert_1 (v)
            vs = _convert (vs)
        def _gen (name, op_name, vs) :
            for v in vs :
                q      = getattr (Q, name)
                qop    = getattr (q, op_name)
                yield qop (v)
        result = tuple (_gen (name, op_name, vs))
        result = Q.OR  (* result) if len (result) > 1 else result [0]
        return result
    # end def cook

    def cooked (self, value, cao = None) :
        result = self.__super.cooked (value, cao)
        if len (result) > 1 :
           result = [self.Q.AND (* result)]
        return result
    # end def cooked

# end class _Q_Exp_Arg_

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.Q_Exp_CAO
