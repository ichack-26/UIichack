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
#    TFL.SDG.C.Macro
#
# Purpose
#    C-macro definitions
#
# Revision Dates
#    11-Aug-2004 (MG) Creation
#    12-Aug-2004 (MG) `Macro_Block.children_group_names` added
#    12-Aug-2004 (MG) Convert the `args` paremeter from `None` to `""` and
#                     from `""` to `None` for backward compatibility
#    12-Aug-2004 (MG) `description` added to formats
#    13-Aug-2004 (CT) `Macro.c_format` simplified
#                     (`%(name)s` instead of `%(::.name:)s`)
#    24-Aug-2004 (CT) Spurious space after macro name removed from `h_format`
#                     and `c_format`
#    24-Aug-2004 (MG) `Macro_Block.children_group_names` removed
#     7-Oct-2004 (CED) `Define_Constant` added
#     8-Feb-2005 (CED) `apidoc_tex_format` defined here and necessary changes
#                      made
#     9-Feb-2005 (MBM/CED) formal changes to `apidoc_tex_format`
#    22-Feb-2005 (MBM) Removed <> from index entry
#    24-Feb-2005 (MBM) Changed index entry structure
#     9-Aug-2005 (CT)  Call to `tex_quoted` added
#    30-Oct-2006 (CED) `Preprocessor_Error` added
#     9-Mar-2007 (CED) Accepting integer as value of `Define_Constant`
#    17-Apr-2007 (CED) `Define_Constant` improved to print parantheses around
#                      `value`
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C.Node
import _TFL._SDG._C.Statement
import _TFL.tex_quoted

import textwrap

class _Macro_ (TFL.SDG.C.Node) :
    """Base class of all preprocessor commands (defines, if, ifdef, ...)"""

    cgi       = None

    def _update_scope (self, scope) :
        ### why do we need this ???? MGL, 11-Aug-2004
        self.scope = scope
        for c in self.children :
            c._update_scope (scope)
    # end def _update_scope

# end class _Macro_

class Macro (_Macro_, TFL.SDG.Leaf) :
    """C-macro defintion"""

    init_arg_defaults      = dict \
        ( name_len         = 0
        , scope            = TFL.SDG.C.C
        , args             = None
        , lines            = None
        )
    front_args             = ("name", "args")
    rest_args              = "lines"
    m_head                 = ""

    h_format = c_format    = """
        #%(m_head)s%(name)s%(:head=(¡tail=):.args:)s %(:sep_eol= \\:.lines:)s
        >%(::*description:)s
    """

    def __init__ (self, * args, ** kw) :
        self.__super.__init__ (* args, ** kw)
        if self.args is None :
            self.args = ""
        elif self.args == "" :
            self.args = None
    # end def __init__

# end class Macro

class Define (Macro) :
    """A C-macro #define stament"""

    m_head                 = "define "

    init_arg_defaults      = dict \
        ( def_file         = "unknown"
        , explanation      = ""
        )

    _apidoc_head           = \
        """%(::@_name_comment:)-{output_width - indent_anchor}s
           \\hypertarget{%(name)s}{}
           \\subsubsection{\\texttt{%(name)s}}
           \\index{FT-COM API>\\texttt{%(name)s}}
           \\ttindex{%(name)s}
           \\begin{description}
           >\\item %(::*description:)s \\\\
           >\\item \\textbf{File:} \\\\ \\texttt{%(def_file)s} \\\\
        """

    _apidoc_tail          = \
        """>%(::>@_explanation:)-{output_width - indent_anchor}s
           \\end{description}
           >
        """

    _apidoc_middle       = \
        """>\\item \\textbf{Function declaration:} \\\\
           >>\\texttt{%(name)s (%(args)s)} \\\\
        """

    apidoc_tex_format    = "".join \
        ( [ _apidoc_head
          , _apidoc_middle
          , _apidoc_tail
          ]
        )

    def _name_comment (self, ** kw) :
        format_prec = int (kw ["format_prec"])
        result = \
            ( "%% --- %s %s"
            % ( self.name
              , "-" * ( format_prec - len (self.name) - 7
                      )
              )
            )
        return [result]
    # end def _name_comment

    def _explanation (self, ** kw) :
        if not self.explanation :
            yield ""
            return
        yield "\\item \\textbf{Description:} \\\\"
        format_prec = max (int (kw ["format_prec"]), 4)
        wrapper     = textwrap.TextWrapper (width = format_prec)
        yield from wrapper.wrap (TFL.tex_quoted (self.explanation)) 
    # end def _explanation

# end class Define

class Define_Constant (Define) :
    """A C-macro #define stament, defining a constant value"""

    init_arg_defaults      = dict \
        ( name_len         = 0
        , scope            = TFL.SDG.C.C
        , name             = None
        , value            = None
        )

    front_args           = ("name", "value")

    h_format = c_format  = """
        #%(m_head)s%(name)s %(:head=(¡tail=):.value:)s
        >%(::*description:)s
    """

    _apidoc_middle       = \
       """>\\item \\textbf{Value:} %(value)s
       """

    apidoc_tex_format    = "".join \
        ( [ Define._apidoc_head
          , _apidoc_middle
          , Define._apidoc_tail
          ]
        )

    _autoconvert         = dict \
        ( value          = lambda s, k, v : str (v)
        )
# end class Define_Constant

class Macro_Block (_Macro_, TFL.SDG.C.Stmt_Group) :
    """Block of macro definitions"""

    Ancestor             = TFL.SDG.C.Stmt_Group

# end class Macro_Block

class Preprocessor_Error (_Macro_) :
    """A C preprocessor error statement"""

    m_head                 = "error "

    init_arg_defaults      = dict \
        ( scope            = TFL.SDG.C.HC
        , error_msg        = ""
        )

    front_args             = ("error_msg", )

    h_format = c_format  = """
        #%(m_head) s%(error_msg)s
    """

# end class Preprocessor_Error

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*", "_Macro_")
### __END__ TFL.SDG.C.Macro
