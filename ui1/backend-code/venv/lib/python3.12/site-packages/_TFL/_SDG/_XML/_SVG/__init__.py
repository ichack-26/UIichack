# -*- coding: utf-8 -*-
# Copyright (C) 2005 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.XML.SVG.__init__
#
# Purpose
#    Package modelling SVG generator
#
# Revision Dates
#     5-Sep-2005 (CT) Creation
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    ««revision-date»»···
#--



from   _TFL                   import TFL
from   _TFL.Package_Namespace import Package_Namespace

import _TFL._SDG._XML

SVG = Package_Namespace ()
TFL.SDG.XML._Export ("SVG")

del Package_Namespace

### __END__ TFL.SDG.XML.SVG.__init__
