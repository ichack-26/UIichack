# -*- coding: utf-8 -*-
# Copyright (C) 2006-2016 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.DRA.__init__
#
# Purpose
#    Package for data reduction and analysis
#
# Revision Dates
#    15-Nov-2006 (CT) Creation
#     9-Oct-2016 (CT) Move to Package_Namespace `TFL`
#    ««revision-date»»···
#--

from   _TFL                   import TFL
from   _TFL.Package_Namespace import Package_Namespace

DRA = Package_Namespace ()

TFL._Export ("DRA")

del Package_Namespace

### __END__ TFL.DRA.__init__
