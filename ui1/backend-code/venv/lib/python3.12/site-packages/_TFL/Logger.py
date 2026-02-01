# -*- coding: utf-8 -*-
# Copyright (C) 2007-2010 Martin Glück. All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Logger
#
# Purpose
#    A small helper simplifying logger creation
#
# Revision Dates
#    13-Sep-2009 (MG) Creation
#    11-Jan-2010 (CT) Esthetics
#    ««revision-date»»···
#--

from   _TFL import TFL

import logging

CRITICAL = logging.CRITICAL
FATAL    = logging.FATAL
ERROR    = logging.ERROR
WARNING  = logging.WARNING
WARN     = logging.WARN
INFO     = logging.INFO
DEBUG    = logging.DEBUG
NOTSET   = logging.NOTSET

def Create \
        ( name
        , format   = "%(message)s"
        , date_fmt = None
        , level    = DEBUG
        ) :
    formatter = logging.Formatter     (format, date_fmt)
    handler   = logging.StreamHandler ()
    logger    = logging.getLogger     (name)
    logger.setLevel      (level)
    handler.setLevel     (level)
    handler.setFormatter (formatter)
    logger.addHandler    (handler)
    return logger
# end def Create

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.Logger
