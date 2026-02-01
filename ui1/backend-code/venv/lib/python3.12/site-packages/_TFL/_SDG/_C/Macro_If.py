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
#    TFL.SDG.C.Macro_If
#
# Purpose
#    Defines preprocessor if/else/elseif
#
# Revision Dates
#    11-Aug-2004 (MG) Creation
#    13-Aug-2004 (CT) `Macro_If.c_format` simplified
#                     (`%(if_tag)s` instead of `%(::.if_tag:)s`)
#    20-Oct-2004 (CT) Imports for `Conditional` and `If_Stmt` added
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL                import TFL
import _TFL._SDG._C.Conditional
import _TFL._SDG._C.If_Stmt
import _TFL._SDG._C.Macro

class Macro_Else (TFL.SDG.C.Macro_Block) :
    """C macro else"""

    cgi                  = TFL.SDG.C.Node.Else
    h_format = c_format  = """
        #else
        >%(::*children:)s
    """

# end class Macro_Else

class Macro_Elseif (TFL.SDG.C.Conditional, TFL.SDG.C.Macro_Block) :
    """A Macro elseif statement"""

    cgi                  = TFL.SDG.C.Node.Elseif
    h_format = c_format  = """
        #elif %(::*condition:)s
        >%(::*children:)s
    """
# end class Macro_Elseif

class Macro_If (TFL.SDG.C._Macro_, TFL.SDG.C.If) :
    """If preprocessor statement (#IF)"""

    then_class          = TFL.SDG.C.Macro_Block
    else_class          = Macro_Else
    elif_class          = Macro_Elseif
    if_tag              = "if"

    h_format = c_format = "\n".join \
        ( ( """#%(if_tag)s %(::*condition:)s"""
          , """>%(::*then_children:)s"""
          , """%(::*elseif_children:)s"""
          , """%(::*else_children:)s"""
          , """#endif /* %(if_tag)s %(::*condition:)s */"""
          )
        )

# end class Macro_If

class Macro_Ifndef (Macro_If) :
    """Ifndef preprocessor statement (#ifndef)"""

    if_tag = "ifndef"

# end class Macro_Ifndef

class Macro_Ifdef (Macro_If) :
    """Ifdef preprocessor statement (#ifdef)"""

    if_tag = "ifdef"

# end class Macro_Ifdef

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.Macro_If
