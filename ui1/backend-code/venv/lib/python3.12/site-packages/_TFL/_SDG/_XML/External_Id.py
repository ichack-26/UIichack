# -*- coding: utf-8 -*-
# Copyright (C) 2005-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.XML.External_Id
#
# Purpose
#    Model an external ID
#
# Revision Dates
#     5-Sep-2005 (CT) Creation
#    23-Jul-2007 (CED) Activated absolute_import
#     6-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL                   import TFL
import _TFL._SDG._XML.Node

class External_Id (TFL.SDG.XML.Node) :
    """Model an external ID"""

    kind                 = "SYSTEM"

    front_args           = ("uri", )
    init_arg_defaults    = dict \
        ( uri            = None
        ,
        )

    public_id            = None

    xml_format           = \
        ( """%(kind)s"""
          """%(:front0= ¡front=%(NL)s    """
            """¡rear0=¡rear=%(NL)s"""
            """¡head="¡tail="¡sep=    """
            """:@_ext_ids:)s"""
        )

    def _ext_ids (self, ** kw) :
        if self.public_id is not None :
            yield self.public_id
        if self.uri is not None :
            yield self.uri
    # end def _ext_ids

# end class External_Id

class External_Id_Public (External_Id) :
    """Model a public external ID"""

    kind                 = "PUBLIC"

    front_args           = ("public_id", "uri")
    init_arg_defaults    = dict \
        ( public_id      = None
        )

# end class External_Id_Public

if __name__ != "__main__" :
    TFL.SDG.XML._Export ("*")
### __END__ TFL.SDG.XML.External_Id
