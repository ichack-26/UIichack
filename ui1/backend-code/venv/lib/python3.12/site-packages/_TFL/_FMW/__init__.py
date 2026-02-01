# -*- coding: utf-8 -*-
# Copyright (C) 2004-2010 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.FMW.__init__
#
# Purpose
#    Function/Method Wrapper package
#
# Revision Dates
#    22-Sep-2004 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL                   import TFL
from   _TFL.Package_Namespace import Package_Namespace

FMW = Package_Namespace ()
TFL._Export ("FMW")

del Package_Namespace

### __END__ TFL.FMW.__init__
