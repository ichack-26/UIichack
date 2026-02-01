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
#    TFL.SDG.XML.Comment
#
# Purpose
#    Model a comment of a XML document
#
# Revision Dates
#    26-Aug-2004 (CT) Creation
#    06-Aug-2007 (CED) Future import removed again
#    ««revision-date»»···
#--

from   _TFL                   import TFL
from   _TFL.pyk               import pyk

import _TFL._SDG._XML.Element

class Comment (TFL.SDG.XML.Leaf) :
    """Model a comment of a XML document

       >>> c = Comment ("Just a test of a XML comment -- with illicit token")
       >>> print (chr (10).join (c.formatted ("xml_format")))
       <!-- Just a test of a XML comment ··· with illicit token -->
       >>> c = Comment ('''A two line
       ... comment for a change''')
       >>> print (chr (10).join (c.formatted ("xml_format")))
       <!-- A two line
            comment for a change
       -->
    """

    front_args           = ("text", )
    init_arg_defaults    = dict \
        ( text           = None
        )

    elem_type            = "!--"

    xml_format           = """
        <!-- %(:rear0= ¡rear=%(NL)s:>.text:)s-->
    """

    _autoconvert         = dict \
        ( text           = lambda s, k, v : s._convert_text (v)
        )

    def _convert_text (self, v) :
        if v and isinstance (v, pyk.string_types) :
            v = v.replace ("--", "···").split ("\n")
        return v
    # end def _convert_text

# end class Comment

if __name__ != "__main__" :
    TFL.SDG.XML._Export ("*")
### __END__ TFL.SDG.XML.Comment
