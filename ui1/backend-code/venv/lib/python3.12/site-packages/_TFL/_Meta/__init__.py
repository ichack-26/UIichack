# -*- coding: utf-8 -*-
# Copyright (C) 2001-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Meta.__init__
#
# Purpose
#    `TFL.Meta` provides meta-classes and property-helpers
#
# Revision Dates
#    13-May-2002 (CT) Creation
#     2-Feb-2009 (CT) Documentation added
#     3-Feb-2009 (CT) Documentation added..
#     4-Feb-2009 (CT) Documentation added...
#    14-Oct-2013 (CT) Add `Single_Dispatch`
#     5-Aug-2015 (CT) Add `M_Auto_Update_Combined`
#    ««revision-date»»···
#--

from   _TFL                   import TFL
from   _TFL.Package_Namespace import Package_Namespace

Meta = Package_Namespace ()
TFL._Export ("Meta")

del Package_Namespace

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

`TFL.Meta` provides a generic base-class and various meta-classes and
property-helpers:

- New-style classes should be derived (directly or indirectly) from
  :class:`Object<_TFL._Meta.Object.Object>` instead of
  Python's builtin `object`.

- Classes derived from other builtin types (like `dict`, `list`,
  `set`, etc.) should declare their metaclass to be
  :class:`M_Class<_TFL._Meta.M_Class.M_Class>`.

- Metaclasses should be derived (directly or indirectly) from
  :class:`M_Base<_TFL._Meta.M_Class.M_Base>`
  (most commonly, from :class:`M_Class<_TFL._Meta.M_Class.M_Class>`).

"""

### __END__ TFL.Meta.__init__
