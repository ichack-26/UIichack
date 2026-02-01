# -*- coding: utf-8 -*-
# Copyright (C) 2004-2013 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.Formatter
#
# Purpose
#    Formatter objects for SDG
#
# Revision Dates
#    23-Jul-2004 (CT) Creation
#    26-Jul-2004 (CT) Creation continued
#    27-Jul-2004 (CT) Creation continued...
#    28-Jul-2004 (CT) Creation continued....
#    30-Jul-2004 (CT) Use `TFL.Look_Ahead_Gen` instead of home-grown code
#     9-Aug-2004 (CT) `_Recursive_Formatter_Node_.__init__` changed to
#                     discard `None` values
#    11-Aug-2004 (MG) `sep_eol` added
#    12-Aug-2004 (CT) s/recurse_args/recurse_kw/g
#    12-Aug-2004 (CT) `rec_form` added
#    12-Aug-2004 (CT) `indent_anchor` added
#    12-Aug-2004 (CT) `Multi_Line_Formatter.__call__` changed to use
#                     `Look_Ahead_Gen`
#    12-Aug-2004 (MG) Various `__str__` added (to improve debugging
#                     capabilities)
#    12-Aug-2004 (CT) Complex format specification added (`comp_prec` and
#                     `prec`)
#    13-Aug-2004 (CT) `anchor` and `key_pattern` added
#    13-Aug-2004 (CT) `add_indent` added to `Multi_Line_Formatter.__call__`
#                     and used to implement `anchor`ed recursions
#    13-Aug-2004 (CT) Sequence of class declarations changed
#    13-Aug-2004 (MG) `_print` and `PRINT` added for debugging (should be
#                     removed once we have finished the implemetation)
#    13-Aug-2004 (MG) `Multi_Line_Formatter.__call__`: update of the
#                     `indent_anchor` changed and moved to the end of the for
#                     loop
#    13-Aug-2004 (MG) `_Recursive_Formatter_.__class__`: `ht_width` added to
#                     the context
#    13-Aug-2004 (MG) `_Recursive_Formatter_Method_.__iter__`,
#                     `_Recursive_Formatter_Node_.__iter__` pass `ht_width`
#                     to the method/recurse function
#    23-Aug-2004 (CT) Code handling `rec_form` moved from
#                     `_Recursive_Formatter_` to `_Recursive_Formatter_Node_`
#    23-Aug-2004 (CT) `__str__` methods moved behind `__iter__` methods
#    24-Aug-2004 (CT) `Multi_Line_Formatter.__call__` changed to protect `%s`
#                     after interpolation
#    26-Aug-2004 (CT) `front0` and `rear0` added
#    27-Aug-2004 (CT) `Multi_Line_Formatter.__call__` changed to use
#                     `percent_pat.sub` instead of string-replace to protect
#                     `%s` characters after interpolation (otherwise, instead
#                     of a single `%` something like `%%%%%%%%` can show up
#                     in the output <arrrgh>)
#    17-Sep-2004 (CT) `Partial_Line_Formatter` used instead of `lambda`
#    17-Sep-2004 (CT) `percent_pat` moved from `Multi_Line_Formatter` to
#                     module-scope, renamed to `_percent_pat` and used in
#                     `Partial_Line_Formatter` and the recursive formatters
#    17-Sep-2004 (CT) `Multi_Line_Formatter.__call__` changed (back and forth)
#    17-Sep-2004 (CT) Pass both `indent_offset` and `indent_anchor` to
#                     recursive calls
#    21-Sep-2004 (CT) Argument `sep_form` of `_Recursive_Formatter_` changed
#                     to `sep`
#    22-Sep-2004 (CT) `front_before_nl` and `rear_after_nl` added
#    22-Sep-2004 (CT) Define `__repr__` instead of `__str__` for the various
#                     formatter classes
#    22-Sep-2004 (CT) `_Recursive_Formatters_.__iter__` changed to not use
#                     `Look_Ahead_Gen` (unfortunately, looking ahead leads to
#                     premature expansion)
#    23-Sep-2004 (CT) `_Recursive_Formatters_.__iter__` changed to delay
#                     expansion of `front_before_nl` until second iteration
#    23-Sep-2004 (CT) `_Recursive_Formatters_.__iter__` changed to use
#                     `next_sep` and `sep` to keep track of the necessary
#                     separators (this complication is necessary for
#                     supporting multiple `key-specs`)
#    23-Sep-2004 (CT) `Multi_Line_Formatter.__call__` changed to add
#                     indentation for `anchor` only when necessary
#    23-Sep-2004 (CT) `Multi_Line_Formatter.__call__` changed to update
#                     `indent_anchor` (almost?) correctly
#    23-Sep-2004 (CT) Debugging statements removed
#    27-Sep-2004 (CT) Don't set/use `x_forms.front0` and `x_forms.rear0`
#                     unless format specification contains at least one of
#                     them
#    13-Jul-2005 (CT) Style
#    30-Aug-2005 (CT) Use `split_hst` instead of home-grown code
#    20-Nov-2007 (MG)  Imports fixed
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

from   _TFL               import TFL
from   _TFL.pyk           import pyk

import _TFL._Meta.Object
import _TFL._SDG
import _TFL.Generators

from   _TFL.Record        import Record
from   _TFL.predicate     import relax, split_hst
from   _TFL.Regexp        import *

import sys
import pdb

_percent_pat = Regexp ("(?<!%)%(?!%)")

class _Formatter_ (TFL.Meta.Object) :
    """Root class of SDG formatters"""

    def __init__ (self, indent_level, format_line) :
        self.indent_level = indent_level
        self.format_line  = format_line
    # end def __init__

    def __repr__ (self) :
        return "%s %s> '%s'" % \
            (self.kind, self.indent_level, self.format_line)
    # end def __repr__

# end class _Formatter_

class Partial_Line_Formatter (_Formatter_) :
    """Formatter generating part of a single line of output"""

    kind = "PLF"

    def __call__ (self, node, context) :
        return (_percent_pat.sub ("%%", self.format_line % context), )
    # end def __call__

# end class Partial_Line_Formatter

class Single_Line_Formatter (_Formatter_) :
    """Formatter generating a single line of output"""

    kind = "SLF"

    def __call__ (self, node, context) :
        return (self.format_line % context, )
    # end def __call__

# end class Single_Line_Formatter

class _Recursive_Formatter_ (TFL.Meta.Object) :

    def __init__ (self, key, format, head_form, tail_form, anchor) :
        self.key       = key
        self._format   = format
        self.head_form = head_form
        self.tail_form = tail_form
        self.anchor    = anchor
    # end def __init__

    def __call__ (self, node, context, sep) :
        self.node       = node
        self.context    = context
        self.recurse_kw = recurse_kw = context.recurse_kw.copy ()
        self.sep        = sep
        head            = self.head_form % context
        tail            = self.tail_form % context
        _format         = self._format
        if isinstance (_format, Record) :
            prec        = _format.prec % context
            _format     = "%%%s%s%s" % (_format.flags, prec, _format.type)
            recurse_kw  ["format_prec"] = float (prec)
        self.format     = head + _format + tail
        context.locals ["ht_width"] = len (head) + len (tail) + len (self.sep)
        return self
    # end def __call__

# end class _Recursive_Formatter_

class _Recursive_Formatter_Attr_ (_Recursive_Formatter_) :

    def __iter__ (self) :
        attr = getattr (self.node, self.key, None)
        if attr is not None :
            format = self.format
            sep    = ""
            if isinstance (attr, pyk.string_types) :
                attr = (attr, )
            for x in attr :
                yield sep + _percent_pat.sub ("%%", format % x)
                sep = self.sep
    # end def __iter__

    def __repr__ (self) :
        return "RF_Attr %s" % (self.key)
    # end def __repr__

# end class _Recursive_Formatter_Attr_

class _Recursive_Formatter_Method_ (_Recursive_Formatter_) :

    def __iter__ (self) :
        result = getattr (self.node, self.key) \
            ( indent_anchor = self.context.indent_anchor
            , indent_offset = self.context.indent_offset
            , ht_width      = self.context.ht_width
            , ** self.recurse_kw
            )
        if result is not None :
            format = self.format
            sep    = ""
            for x in result :
                yield sep + _percent_pat.sub ("%%", format % x)
                sep = self.sep
    # end def __iter__

    def __repr__ (self) :
        return "RF_Meth %s" % (self.key)
    # end def __repr__

# end class _Recursive_Formatter_Method_

class _Recursive_Formatter_Node_ (_Recursive_Formatter_) :

    def __init__ (self, key, format, head_form, tail_form, anchor) :
        key, _, rec_form = split_hst (key, ".")
        self.rec_form    = rec_form or None
        self.__super.__init__ (key, format, head_form, tail_form, anchor)
    # end def __init__

    def __call__ (self, node, context, sep) :
        result = self.__super.__call__ (node, context, sep)
        if self.rec_form :
            self.recurse_kw ["format_name"] = self.rec_form
        return result
    # end def __call__

    def __iter__ (self) :
        context  = self.context
        format   = self.format
        recurser = context.recurser
        rkw      = self.recurse_kw
        sep      = ""
        nodes    = getattr (self.node, self.key)
        if nodes is not None :
            if isinstance (nodes, TFL.SDG.Node) :
                nodes = (nodes, )
            for x in nodes :
                if x is not None :
                    result = getattr (x, recurser) \
                        ( indent_anchor = self.context.indent_anchor
                        , indent_offset = self.context.indent_offset
                        , ht_width      = context.ht_width
                        , ** rkw
                        )
                    for y in result :
                        yield sep + _percent_pat.sub ("%%", format % y)
                        sep = ""
                    sep = self.sep
    # end def __iter__

    def __repr__(self) :
        return "RF_Node %s" % (self.key)
    # end def __repr__

# end class _Recursive_Formatter_Node_

class _Recursive_Formatters_ (TFL.Meta.Object) :

    def __init__ (self, x_forms, * formatters) :
        self.x_forms    = x_forms
        self.formatters = formatters
    # end def __init__

    def __call__ (self, node, context) :
        self.node    = node
        self.context = context
        x_forms      = self.x_forms
        self.empty   = x_forms.empty   % context
        self.front   = x_forms.front   % context
        self.rear    = x_forms.rear    % context
        self.sep     = x_forms.sep     % context
        self.sep_eol = x_forms.sep_eol % context
        for k in "front0", "front_before_nl", "rear0", "rear_after_nl" :
            v = getattr (x_forms, k)
            if v is not None :
                v = v % context
            setattr (self, k, v)
        return self
    # end def __call__

    def __iter__ (self) :
        node       = self.node
        context    = self.context
        sep        = self.front
        next_sep   = ""
        eol        = self.sep_eol
        i          = 0
        last       = None
        fbnl       = None
        if self.front_before_nl is not None :
            context.locals ["indent_offset"] += len (sep)
            context.locals ["indent_anchor"]  = context.indent_offset
        for f in self.formatters :
            self.anchor = f.anchor
            for line in f (node, context, sep = self.sep) :
                if i == 0 :
                    if self.front_before_nl is not None :
                        fbnl = self.front_before_nl
                else :
                    if fbnl is not None :
                        yield fbnl
                        fbnl = None
                    yield "".join ((sep, last, eol))
                    sep      = next_sep
                    next_sep = ""
                last = line
                i   += 1
            if i :
                next_sep = self.sep
        if last is not None :
            if i == 1 and self.front0 is not None :
                yield "".join ((self.front0, last, self.rear0))
            else :
                if fbnl is not None :
                    yield fbnl
                yield "".join ((sep, last, self.rear))
                if self.rear_after_nl is not None :
                    yield self.rear_after_nl
        elif self.empty :
            yield self.empty
    # end def __iter__

    def __repr__ (self) :
        return "RFS (%s)" % (", ".join ([str (f) for f in self.formatters]), )
    # end def __repr__

# end class _Recursive_Formatters_

class Multi_Line_Formatter (_Formatter_) :
    """Formatter generating a multiple lines of output"""

    kind    = "MLF"

    pattern     = Regexp \
        ( r"""%"""
          r"""\( : (?P<x_forms> [^:]*) : (?P<keys> [^:]+) : \)"""
          r"""(?P<form> """
              r"""(?P<flags>  [-+ #0]*)"""
              r"""(?:"""
                  r"""(?:"""
                      r"""(?P<mfw>    [0-9]*)"""
                      r"""(?P<prec> \.[0-9]+)?"""
                  r""")"""
                  r"""|"""
                  r"""(?:"""
                      r"""\{ (?P<comp_prec> [^\}]+) \}"""
                  r""")"""
              r""")?"""
              r"""(?P<type> [diouxXeEfFgGcrs])"""
          r""")"""
        , re.VERBOSE
        )

    key_pattern = Regexp \
        ( r"""(?P<anchor> >?) (?P<type> [.*@]) (?P<name> .*)"""
        , re.VERBOSE
        )

    Formatters  = \
        { "." : _Recursive_Formatter_Attr_
        , "@" : _Recursive_Formatter_Method_
        , "*" : _Recursive_Formatter_Node_
        }

    def __init__ (self, indent_level, format_line) :
        self.__super.__init__  (indent_level, format_line)
        self._setup_formatters (format_line)
    # end def __init__

    def __call__ (self, node, context) :
        head = ""
        for f in self.formatters :
            lines      = TFL.Look_Ahead_Gen (f (node, context))
            i          = 0
            add_indent = len (head)
            for l in lines :
                lines_not_finished = not lines.is_finished
                if i > 0 and f.anchor and (lines_not_finished or l) :
                    head = (" " * add_indent) + head
                    context.locals ["indent_anchor"] += add_indent
                next  = l % context
                head += next
                context.locals ["indent_anchor"] += len (next)
                if lines_not_finished :
                    context.locals ["indent_anchor"] -= len (head)
                    yield head
                    head = ""
                i += 1
        if head :
            context.locals ["indent_anchor"] -= len (head)
            yield head
    # end def __call__

    def _x_forms (self, x_forms) :
        result = Record \
            ( empty           = ""
            , front           = ""
            , front_before_nl = None
            , front0          = None
            , head            = ""
            , rear            = ""
            , rear_after_nl   = None
            , rear0           = None
            , sep             = ""
            , sep_eol         = ""
            , tail            = ""
            )
        if x_forms :
            for spec in x_forms.split ("¡") :
                key, form = spec.split ("=", 1)
                setattr (result, key, form)
        nl = "%(NL)s"
        if nl in result.front :
            result.front_before_nl, result.front = result.front.split (nl)
        if nl in result.rear :
            result.rear, result.rear_after_nl    = result.rear.split (nl)
        if (result.front0 is not None) or (result.rear0 is not None) :
            if result.front0 is None :
                result.front0 = "".join \
                    ((result.front_before_nl or "", result.front))
            if result.rear0 is None :
                result.rear0  = "".join \
                    ((result.rear, result.rear_after_nl or ""))
        return result
    # end def _x_forms

    def _setup_formatters (self, format_line) :
        self.formatters = formatters = []
        add = formatters.append
        pos = 0
        for match in self.pattern.search_iter (format_line) :
            s = match.start (0)
            if pos < s :
                add (Partial_Line_Formatter (0, format_line [pos:s]))
            add (self._recursive_formatter (match))
            pos = match.end (0)
        if pos < len (format_line) :
            add (Partial_Line_Formatter (0, format_line [pos:]))
    # end def _setup_formatters

    def _recursive_formatter (self, match) :
        x_forms    = self._x_forms (match.group ("x_forms"))
        keys       = match.group ("keys").split (",")
        comp_prec  = match.group ("comp_prec")
        if comp_prec :
            form   = Record \
                ( flags = match.group ("flags")
                , prec  = "%%(%s)s" % (comp_prec, )
                , type  = match.group ("type")
                )
        else :
            form   = "%%%s" % (match.group ("form"), )
        formatters = []
        for key in keys :
            key     = key.strip ()
            k_match = self.key_pattern.match (key)
            if k_match :
                anchor = bool (k_match.group ("anchor"))
                type   = k_match.group ("type")
                name   = k_match.group ("name")
                rf     = self.Formatters [type]
                formatters.append \
                    (rf (name, form, x_forms.head, x_forms.tail, anchor))
            else :
                raise ValueError (key, match.group (0))
        return _Recursive_Formatters_ (x_forms, * formatters)
    # end def _recursive_formatter

# end class Multi_Line_Formatter

def Formatter (level, format_line) :
    if Multi_Line_Formatter.pattern.search (format_line) :
        formatter = Multi_Line_Formatter
    else :
        formatter = Single_Line_Formatter
    return formatter (level, format_line)
# end def Formatter

if __name__ != "__main__" :
    TFL.SDG._Export ("Formatter")
### __END__ TFL.SDG.Formatter
