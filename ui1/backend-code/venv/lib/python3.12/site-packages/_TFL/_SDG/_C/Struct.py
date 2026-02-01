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
#    TFL.SDG.C.Struct
#
# Purpose
#    C structure declaration
#
# Revision Dates
#     9-Aug-2004 (CT) Creation
#    12-Aug-2004 (MG) Formats changed (always use `h_format` for the
#                     `decl_children`)
#    23-Sep-2004 (MG) `vaps_channel_format` added
#    12-Jul-2005 (MG) `description` added to `[ch]_format`
#    30-Aug-2005 (CT)  Use `split_hst` instead of home-grown code
#    20-Nov-2006 (MZO) [21696] `_setup_initializers_for_cdg_array` added
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    18-Oct-2007 (MZO) [25170] line break in description introduced
#    25-Apr-2008 (MG)  `_setup_initializers`: handling for nested structs
#                      extended
#    26-Feb-2012 (MG) `__future__` imports added
#    19-Apr-2020 (CT)  Use "``" for doc strings, not "`'"
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._SDG._C._Decl_
import _TFL._SDG._C.Expression
import _TFL._SDG._C.Type

import weakref

from   _TFL.predicate    import split_hst
from   _TFL.Regexp       import *

class Struct (TFL.SDG.C._Decl_) :
    """C structure declaration"""

    extension              = {}

    front_args             = ("name", )
    init_arg_defaults      = dict \
        ( desc_in_new_line = 0
        , standalone       = ""
        )
    _autoconvert         = dict \
        ( standalone     = lambda s, k, v : v and ";" or ""
        )

    h_format = c_format  = """
        struct _%(name)s
        >{
        >>%(::*decl_children.h_format:)s
        >}%(standalone)s
        >%(::*description:)s
    """

    vaps_channel_format = """
        %(::*decl_children:)s
        """
    field_pat            = Regexp \
        ( r"""(?P<head>\s*)"""
          r"""(?P<const>const \s+ )?"""
          r"""(?P<struct>struct \s+ )?"""
          r"""(?P<volat>volatile \s+ )?"""
          r"""(?P<type> [a-zA-Z_][a-zA-Z0-9_]*"""
          r"""  (?: \s+ [][a-zA-Z0-9_*]*)*"""
          r""")"""
          r"""\s+"""
          r"""(?P<name> [a-zA-Z_][a-zA-Z0-9_:]*)"""
          r"""\s*"""
          r"""(?: (?P<bounds>\[[\w\[\]]+\]))?"""
          r"""(?: = \s* (?P<init> .+))?"""
          r"""\s*"""
          r"""(?: //\s* (?P<desc> .*))?"""
        , re.X
        )

    def __init__ (self, * args, ** kw) :
        self.__super.__init__ (* args, ** kw)
        #if self.name in self.extension :
        #    raise KeyError (self.name, self.extension [self.name])
        self.extension [self.name] = self
    # end def __init__

    def insert (self, child, index = None, delta = 0, cgi = None) :
        """Insert `child` to `self.children` at position `index`
           (`index is None` means append)
           (None means append).
        """
        for c in self._convert_field (child) :
            if cgi is not None :
                c.cgi = cgi
            self.__super.insert (c, index, delta)
    # end def insert

    def _convert_field (self, f) :
        if isinstance (f, TFL.SDG.C.Node) :
            return f
        m = self.field_pat.match (f)
        if not m :
            print (f)
            raise TFL.SDG.Invalid_Node (self, f)
        name   = m.group ("name").strip ()
        type   = m.group ("type").strip ()
        init   = (m.group ("init") or "").strip ()
        desc   = (m.group ("desc") or "").strip ()
        volat  = bool ((m.group ("volat")  or "").strip ())
        const  = bool ((m.group ("const")  or "").strip ())
        struct = bool ((m.group ("struct") or "").strip ())
        if init :
            init, _, desc = [x.strip () for x in split_hst (init, "//")]
        if not init :
            init = None
        if m.group ("bounds") :
            bounds = m.group ("bounds") [1:-1].split ("][")
            return TFL.SDG.C.Array \
                ( type, name, bounds, description = desc
                , new_line_col = self.desc_in_new_line
                , const        = const
                )
        else :
            return TFL.SDG.C.Var \
                ( type, name, description = desc
                , new_line_col = self.desc_in_new_line
                , const        = const
                , volatile     = volat
                , struct       = struct
                )
    # end def _convert_field

    def _setup_initializers (self, init_dict, description = None) :
        result = TFL.SDG.C.Init_Comp (description = description)
        for c in self.decl_children :
            if c.name not in init_dict :
                if c.init :
                    v = c.init.init
                else :
                    msg = ( "No initialization value for `%s.%s`"
                          % (self.name, c.name)
                          )
                    raise ValueError (msg)
            else :
                v = init_dict [c.name]
            if c.type.name in TFL.SDG.C.Struct.extension :
                i = TFL.SDG.C.Struct.extension \
                    [c.type.name]._setup_initializers (v)
            elif isinstance (c, (TFL.SDG.C.Struct, TFL.SDG.C.Array)) :
                i = c._setup_initializers (v)
            else :
                i = TFL.SDG.C.Init_Atom (v, description = c.name)
            result.add (i)
        return result
    # end def _setup_initializers

    def _setup_initializers_for_cdg_array \
        (self, init_dict, description = None) :
        ### speed/ram optimized generation
        result = []
        for c in self.decl_children :
            if c.name not in init_dict :
                if c.init :
                    v = c.init.init
                else :
                    msg = \
                        ( "No initialization value for `%s.%s`"
                        % (self.name, c.name)
                        )
                    raise ValueError (msg)
            else :
                v = init_dict [c.name]
            assert not isinstance (c, (TFL.SDG.C.Struct, TFL.SDG.C.Array)), c
            descr = "/* %s */" % c.name
            result.append ("%s %s" % (v, descr))
        description_with_lf = []
        if description :
            description = description.replace ("\n", " ")
            ## emulate description line break :
            ##     } /* ...*/
            ##     /* ...  */
            indent  = 6
            max_col = 80
            is_first = True
            while description :
                i = (max_col - indent - 6) # 6 comment chars
                if is_first :
                    i -= 6  # consider element maker " [0] "
                    is_first = False
                line = description [: i]
                description_with_lf.append ("/* %s */" % line)
                description = description [i:] # 6 comment chars
        return \
            ("{ %s\n    } %s"
            % ( "\n    , ".join (result)
              , "\n    ".join   (description_with_lf)
              )
            )
    # end def _setup_initializers_for_cdg_array

# end class Struct

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.Struct
