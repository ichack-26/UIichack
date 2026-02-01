#! /usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2001-2017 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL/__init__
#
# Purpose
#    Initialize package `TFL`
#
# Revision Dates
#     3-Jul-2001 (CT) Creation (of comment)
#    22-Feb-2002 (CT) `_Export` for `Package_Namespace` added
#    27-Feb-2002 (CT) `TFL.Package_Namespace` assigned instead of using
#                     `_Export` (which leads to circular import again)
#    24-Jun-2002 (CT) Import `Package_Namespace` absolutely (i.e., from `_TFL`)
#    10-Feb-2010 (MG) `BREAK` added
#     8-Apr-2010 (CT) `BREAK` removed
#    18-Aug-2015 (CT) Remove assignment of `TFL.Package_Namespace`
#    10-Oct-2016 (CT) Add `__version__`
#    22-Feb-2017 (CT) Remove `__version__`
#    ««revision-date»»···
#--

from _TFL.Package_Namespace import Package_Namespace

TFL = Package_Namespace ()

del Package_Namespace

### __END__ TFL/__init__
