# -*- coding: utf-8 -*-
# Copyright (C) 2004-2013 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.XML.Cdata
#
# Purpose
#    Model a CDATA section of a XML document
#
# Revision Dates
#    26-Aug-2004 (CT) Creation
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL                   import TFL
from   _TFL.pyk               import pyk

import _TFL._SDG._XML.Element

class Cdata (TFL.SDG.XML.Leaf) :
    """Model a CDATA section of a XML document

       >>> c = Cdata ('''<?xml version="1.0"?>
       ... <!DOCTYPE memo SYSTEM "memo.dtd">
       ... <Memo>
       ... </Memo>
       ... ''')
       >>> print (chr (10).join (c.formatted ("xml_format")))
       <![CDATA[
         <?xml version="1.0"?>
         <!DOCTYPE memo SYSTEM "memo.dtd">
         <Memo>
         </Memo>
       ]]>
    """

    front_args           = ("data", )
    init_arg_defaults    = dict \
        ( data           = None
        )

    elem_type            = "CDATA"

    xml_format           = """
        <![CDATA[
        >%(::.data:)s
        ]]>
    """

    _autoconvert         = dict \
        ( data           = lambda s, k, v : s._convert_data (v)
        )

    def _convert_data (self, v) :
        if v and isinstance (v, pyk.string_types) :
            assert "]]>" not in v
            v = v.split ("\n")
        return v
    # end def _convert_data

# end class Cdata

if __name__ != "__main__" :
    TFL.SDG.XML._Export ("*")
### __END__ TFL.SDG.XML.Cdata
