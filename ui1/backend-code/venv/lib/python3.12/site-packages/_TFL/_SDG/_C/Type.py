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
#    TFL.SDG.C.Type
#
# Purpose
#    Model C types
#
# Revision Dates
#    27-Jul-2004 (CT) Creation
#    23-Sep-2004 (MG) `vaps_channel_format` and friends added
#    24-Sep-2004 (MG) `vaps_channel_format` simplified
#    23-Feb-2005 (CED) `apidoc_tex_format` defined
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C.Node

class Type (TFL.SDG.C.Node) :
    """Model C types"""

    type_dict           = { "sbyte2" : "S"
                          , "sbyte4" : "L"
                          , "float"  : "F"
                          }

    front_args          = ("name", )

    h_format = c_format = apidoc_tex_format = "%(name)s"

    vaps_channel_format = """%(name)s"""


# end class Type

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.Type
