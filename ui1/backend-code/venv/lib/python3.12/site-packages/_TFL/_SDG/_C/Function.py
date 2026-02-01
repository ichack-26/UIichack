# -*- coding: utf-8 -*-
# Copyright (C) 2004-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.C.Function
#
# Purpose
#    Model C functions
#
# Revision Dates
#    28-Jul-2004 (CT) Creation
#    13-Aug-2004 (CT) `base_indent2` replaced by `base_indent * 2`
#    25-Aug-2004 (MG) `*_common` formats added to allow reused in decentants
#    26-Aug-2004 (CT) Use `NL` instead of `'''\\n'''`
#    26-Aug-2004 (CT) `front0` and `rear0` used
#     1-Sep-2004 (MG) `Function.tail_char` added and used in format
#    23-Feb-2005 (CED) `apidoc_tex_format` and friends defined
#     8-Sep-2005 (PGO) import of textwrap removed (not used)
#    08-Dec-2005 (MG)  `_convert_args` use `_force` instead of `_convert`
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C._Decl_
import _TFL._SDG._C.Type
import _TFL._SDG._C.Arg_List

class _Function_ (TFL.SDG.C.Maybe_Extern, TFL.SDG.C.Maybe_Static) :
    """Root class for C function declarations and function definitions"""

    init_arg_defaults    = dict \
        ( arg_list       = ""
        , return_type    = ""
        )
    _autoconvert         = dict \
        ( arg_list       =
            lambda s, k, v : s._convert_args (v)
        , return_type    =
            lambda s, k, v : s._convert (v, TFL.SDG.C.Type)
        )
    front_args           = ("return_type", "name", "arg_list")
    star_level           = 3

    _h_format = _c_format  = \
        ( """%(::*return_type:)s %(name)s"""
              """%(:front=%(NL)s%(base_indent * 2)s( """
                """¡rear=%(NL)s%(base_indent * 2)s)"""
                """¡front0= ("""
                """¡rear0=)"""
                """¡empty= (void)"""
                """:*arg_list"""
                """:)s"""
        )

    def _convert_args (self, v) :
        if v is None or v == "void" :
            return ""
        else :
            return self._force (v, TFL.SDG.C.Arg_List)
    # end def _convert_args

# end class _Function_

class Fct_Decl (_Function_) :
    """C function declaration"""

    h_format_common      = _Function_._h_format + ";"
    c_format_common      = _Function_._c_format + ";"

    h_format             = h_format_common
    c_format             = c_format_common

# end class Fct_Decl

class Function (_Function_, TFL.SDG.C._Scope_) :
    """C function definition"""

    init_arg_defaults      = dict \
        ( def_file         = "unknown"
        )
    cgi                  = TFL.SDG.C.Node.Body
    tail_char            = ";"

    apidoc_tex_format    = \
        """%(::@_name_comment:)-{output_width - indent_anchor}s
           \\hypertarget{%(name)s}{}
           \\subsubsection{\\texttt{%(name)s}}
           \\index{FT-COM API\\texttt{%(name)s}}
           \\ttindex{%(name)s}
           \\begin{description}
           >\\item %(::*description:)s \\\\
           >\\item \\textbf{File:} \\\\ \\texttt{%(def_file)s} \\\\
           >\\item \\textbf{Function declaration:} \\\\
           >>\\texttt{""" + _Function_._h_format + """} \\\\
           >%(::*explanation:)s
           \\end{description}
           >
        """

    _mod_format          = """%(::.static:)s%(::.extern:)s"""
    h_format_common      = "".join \
        ( ( _mod_format
          , _Function_._h_format
          , """%(:empty=;"""
              """¡front=;%(NL)s%(base_indent * 2)s"""
              """¡sep=%(base_indent * 2)s"""
              """:*description:)s
               >
          """
          )
        )
    body_format          = """
                >>%(::*description:)s
                {
                >>%(::*explanation:)s
                >>%(::*decl_children:)s
                >>%(::*head_children:)s
                >>%(::*body_children:)s
                >>%(::*tail_children:)s
                }%(tail_char)s
                >
            """
    c_format_common      = "".join \
        ( ( _mod_format
          , _Function_._c_format
          , body_format
          )
        )

    h_format             = h_format_common
    c_format             = c_format_common

    def _update_scope_child (self, child, scope) :
        child._update_scope (TFL.SDG.C.C)
    # end def _update_scope_child

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

# end class Function

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*", "_Function_")
### __END__ TFL.SDG.C.Function
