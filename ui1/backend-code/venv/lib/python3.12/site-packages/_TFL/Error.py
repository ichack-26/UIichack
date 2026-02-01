# -*- coding: utf-8 -*-
# Copyright (C) 2008-2013 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Error
#
# Purpose
#    Provide exception classes for TFL package namespace
#
# Revision Dates
#     3-Apr-2008 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL                import TFL

class Not_A_File              (Exception) : pass
class Not_A_Dir               (Exception) : pass
class Sync_Conflict           (Exception) : pass
class Already_Open            (Exception) : pass
class Not_Open                (Exception) : pass
class Could_Not_Delete_Old_DB (Exception) : pass

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Error
