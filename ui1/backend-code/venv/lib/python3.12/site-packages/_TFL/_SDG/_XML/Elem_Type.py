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
#    TFL.SDG.XML.Elem_Type
#
# Purpose
#    Provide a function for creating new element types dynamically
#
# Revision Dates
#    27-Aug-2004 (CT) Creation
#    20-Sep-2004 (CT) Test for `x_attrs` added
#    21-Oct-2004 (CT) Use `"` instead of `'` in output
#     5-Sep-2005 (CT) Doctest fixed (`x_attrs` sorted alphabetically)
#     6-Sep-2005 (CT) Doctest adapted to change of `_attr_values`
#    20-Nov-2007 (MG) Imports fixed
#    26-Feb-2012 (MG) `__future__` imports added
#    27-Aug-2012 (CT) Add `init_arg_defaults` as argument
#    29-Aug-2012 (CT) Add `_autoconvert` as argument
#    ««revision-date»»···
#--

"""Usage example:

   >>> from _TFL._SDG._XML.Document import *
   >>> d = Document ("Test", "Test for TFL.SDG.XML.Elem_Type creation and use")
   >>> X = Elem_Type ( "X", foo = None, bar = 42, baz = "quuux")
   >>> Y = Elem_Type ( "Y", bases = (TFL.SDG.XML.Empty, )
   ...               , foo = None, bar = 42, baz = "quuux"
   ...               )
   >>> d.add (X ("A foo-carrying X", foo = "wibble"))
   >>> d.add (Y (bar = "wobble"))
   >>> d.add (X ("A bar-less X", bar = None))
   >>> d.add (Y (baz = None, x_attrs = dict (qux = 84, quy = 85)))
   >>> d.write_to_xml_stream ()
   <?xml version="1.0" encoding="utf-8" standalone="yes"?>
   <Test>
     Test for TFL.SDG.XML.Elem_Type creation and use
     <X bar="42" baz="quuux" foo="wibble">
       A foo-carrying X
     </X>
     <Y bar="wobble" baz="quuux"/>
     <X baz="quuux">
       A bar-less X
     </X>
     <Y bar="42" qux="84" quy="85"/>
   </Test>

"""

from   _TFL                   import TFL
from   _TFL.pyk               import pyk

import _TFL._SDG._XML.Element
import _TFL.Caller

from   _TFL.predicate         import *

def Elem_Type \
        ( elem_type
        , bases             = None
        , front_args        = ()
        , rest_args         = None
        , init_arg_defaults = {}
        , _autoconvert      = {}
        , ** attributes
        ) :
    """Return a new subclass of XML.Element"""
    if bases is None :
        bases         = (TFL.SDG.XML.Element, )
    attr_names        = []
    front_dict        = dict_from_list (front_args)
    init_arg_defaults = dict (init_arg_defaults)
    for k, v in pyk.iteritems (attributes) :
        init_arg_defaults [k] = v
        if not (k in front_dict or k == rest_args) :
            attr_names.append (k)
    return TFL.SDG.XML.Element.__class__ \
        ( elem_type, bases
        , dict
            ( attr_names        = tuple (sorted (attr_names))
            , _autoconvert      = _autoconvert
            , elem_type         = elem_type
            , front_args        = front_args
            , init_arg_defaults = init_arg_defaults
            , rest_args         = rest_args
            , __module__        = TFL.Caller.globals () ["__name__"]
            )
        )
# end def Elem_Type

if __name__ != "__main__" :
    TFL.SDG.XML._Export ("*")
### __END__ TFL.SDG.XML.Elem_Type
