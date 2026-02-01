# -*- coding: utf-8 -*-
# Copyright (C) 2002 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    __init__
#
# Purpose
#    Package for 2D geometry
#
# Revision Dates
#    24-Jun-2002 (CT) Creation
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    ««revision-date»»···
#--



from   _TFL                   import TFL
from   _TFL.Package_Namespace import Package_Namespace

D2 = Package_Namespace ()
TFL._Export ("D2")

del Package_Namespace

### __END__ __init__
