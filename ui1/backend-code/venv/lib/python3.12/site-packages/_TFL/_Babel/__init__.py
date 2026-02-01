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
#    TFL.Babel.__init__
#
# Purpose
#    Package for inetgration with the Babel i18n framework
#
# Revision Dates
#    21-Jan-2010 (MG) Creation
#    ««revision-date»»···
#--

from   _TFL                   import TFL
from   _TFL.Package_Namespace import Package_Namespace

Babel = Package_Namespace ()
TFL._Export ("Babel")

del Package_Namespace

### __END__ TFL.Babel.__init__
