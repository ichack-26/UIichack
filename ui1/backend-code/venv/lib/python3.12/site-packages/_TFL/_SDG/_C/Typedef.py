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
#    TFL.SDG.C.Typedef
#
# Purpose
#    Model C typedef declarations
#
# Revision Dates
#    30-Jul-2004 (CT) Creation
#    12-Aug-2004 (MG) `description` and `eol_desc` added to formats
#    23-Sep-2004 (MG) `vaps_channel_format` added
#    20-Oct-2004 (CT) Import for `_Decl_` added
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C._Decl_
import _TFL._SDG._C.Node

class Typedef (TFL.SDG.C.Maybe_Const, TFL.SDG.Leaf) :
    """Model C typedef declarations"""

    init_arg_defaults    = dict \
        ( type           = ""
        )

    _autoconvert         = dict \
        ( type           = lambda s, k, v : s._convert (v, TFL.SDG.C.Type)
        )

    _name_or_type        = property (lambda s : s.name or s.type.name)

    h_format = c_format  = "".join \
        ( ( """typedef """
          , """%(::.const:)s"""
          , """%(::*type:)s %(::._name_or_type:)s; %(::*eol_desc:)s
               >%(::*description:)s
            """
          )
        )
    vaps_channel_format = """
        SCOPE      SESSION
        TYPE       FAST
        %(::*type:)s
        """

    def __init__ (self, type, name = None, ** kw) :
        if isinstance (type, TFL.SDG.C.Struct) and not name :
            name = type.name
        self.__super.__init__ (name = name, type = type, ** kw)
    # end def __init__

# end class Typedef

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.Typedef
