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
#    TFL.SDG.C._Scope_
#
# Purpose
#    Model scope-like elements in the code in a C file
#
# Revision Dates
#    27-Jul-2004 (CT) Creation
#    12-Aug-2004 (MG) `default_cgi` added
#    26-Feb-2012 (MG) `__future__` imports added
#    19-Apr-2020 (CT)  Use "``" for doc strings, not "`'"
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C.Node

class _Scope_ (TFL.SDG.C.Node) :
    """Root class for all scope-like C document nodes"""

    Ancestor             = TFL.SDG.C.Node
    init_arg_defaults    = dict \
        ( explanation    = ""
        )

    _autoconvert         = dict \
        ( explanation    =
              lambda s, k, v : s._convert_c_comment (k, v, eol = False)
        )

    children_group_names = \
        ( Ancestor.Head, Ancestor.Body, Ancestor.Tail, Ancestor.Decl)
    default_cgi          = Ancestor.Decl
    explanation_level    = Ancestor.description_level + 2

    def insert (self, child, index = None, delta = 0, cgi = None) :
        """Insert `child` to `self.children` at position `index`
           (`index is None` means append)
           (None means append).
        """
        for c in self._convert_c_stmt (child) :
            if cgi is not None :
                c.cgi = cgi
            self.__super.insert (c, index, delta)
    # end def insert

    def insert_head (self, child, index = None, delta = 0) :
        ### just for backward compatibility
        ### don't use for new code
        self.insert (child, index, delta, cgi = self.Head)
    # end def insert_head

    def insert_tail (self, child, index = None, delta = 0) :
        ### just for backward compatibility
        ### don't use for new code
        self.insert (child, index, delta, cgi = self.Tail)
    # end def insert_tail

# end class _Scope_

if __name__ != "__main__" :
    TFL.SDG.C._Export ("_Scope_")
### __END__ TFL.SDG.C._Scope_
