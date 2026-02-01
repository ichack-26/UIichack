# -*- coding: utf-8 -*-
# Copyright (C) 2004-2020 TTTech Computertechnik AG. All rights reserved
# Schönbrunnerstraße 7, A--1040 Wien, Austria. office@tttech.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.C.import_C
#
# Purpose
#    Provide all imports needed to create a C-document.
#
#    Usage:
#        from _TFL._SDG._C.import_C import C
#
#        module = C.Module (...)
#        module.add (C.If (...))
#        [...]
#
# Revision Dates
#    10-Aug-2004 (MG)  Creation
#    11-Aug-2004 (MG)  Creation continued
#    12-Aug-2004 (MG)  Backward compatibility added
#    24-May-2005 (CED) Import of `Enum` added
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL._SDG._C                     import C
import _TFL._SDG._C.Array
import _TFL._SDG._C.Block
import _TFL._SDG._C.Comment
import _TFL._SDG._C.Enum
import _TFL._SDG._C.For_Stmt
import _TFL._SDG._C.Function
import _TFL._SDG._C.If_Stmt
import _TFL._SDG._C.Include
import _TFL._SDG._C.Macro
import _TFL._SDG._C.Macro_If
import _TFL._SDG._C.Module
import _TFL._SDG._C.New_Line
import _TFL._SDG._C.Statement
import _TFL._SDG._C.Struct
import _TFL._SDG._C.Switch
import _TFL._SDG._C.Typedef
import _TFL._SDG._C.Var
import _TFL._SDG._C.While

### __END__ TFL.SDG.C.import_C
