# -*- coding: utf-8 -*-
# Copyright (C) 2006-2010 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.load_config_file
#
# Purpose
#    Load config file
#
# Revision Dates
#     5-Jan-2006 (CT) Creation
#    10-Nov-2009 (CT) s/execfile/exec/ to avoid `-3` warning
#    30-Jul-2010 (CT) Moved from `TGL` to `TFL`
#    ««revision-date»»···
#--

from _TFL import TFL
from _TFL import sos

def load_config_file (file_name, globals, locals = None) :
    if locals is None :
        locals = globals
    fname = sos.expanded_path (file_name)
    try :
        with open (fname) as f :
            config = f.read ()
    except IOError :
        pass
    else :
        exec (config, globals, locals)
    return locals
# end def load_config_file

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.load_config_file
