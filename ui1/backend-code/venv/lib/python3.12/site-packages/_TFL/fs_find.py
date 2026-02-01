# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.fs_find
#
# Purpose
#    Find files and directory names
#
# Revision Dates
#    13-Oct-2016 (CT) Creation
#    23-Feb-2017 (CT) Factor to `TFL_STP`
#    25-Feb-2017 (CT) Fix imports
#    ««revision-date»»···
#--

from   _TFL               import TFL
from   TFL_STP.fs_find    import *

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.fs_find
