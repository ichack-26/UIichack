# -*- coding: utf-8 -*-
# Copyright (C) 2010-2020 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.pyk
#
# Purpose
#    Hide incompatibilities between Python versions
#
# Revision Dates
#    16-Jun-2010 (CT) Creation
#     2-Apr-2020 (CT) Remove Python-2 compatibility
#    ««revision-date»»···
#--

"""
This module hides incompatibilities between different Python versions.

Originally, differences between Python-2 and Python-3 were covered.

After removing Python-2, the module doesn't much except allow keeping uses of
`pyk` in place.

Should a future Python version introduce gratuitous incompatibilities again,
`pyk` is here to cover that.
"""

import sys

if sys.version_info < (3,) :
    raise NotImplementedError \
        ("Python 2 is no longer supported; use branch `Python_2` if you must")
else :
    from _TFL._pyk3 import pyk
### __END__ TFL.pyk
