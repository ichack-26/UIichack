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
#    TFL.SDG.C.__init__
#
# Purpose
#    Package modelling C code generator
#
# Revision Dates
#    26-Jul-2004 (CT) Creation
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL                   import TFL
from   _TFL.Package_Namespace import Package_Namespace

import _TFL._SDG

C = Package_Namespace ()
TFL.SDG._Export ("C")

del Package_Namespace

### __END__ TFL.SDG.C.__init__
