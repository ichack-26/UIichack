# -*- coding: utf-8 -*-
# Copyright (C) 2004-2022 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.Node
#
# Purpose
#    Model a node of a structured document
#
# Revision Dates
#    23-Jul-2004 (CT)  Creation
#    26-Jul-2004 (CT)  Creation continued
#    27-Jul-2004 (CT)  Call to `_autoconvert` corrected (`self` passed)
#    28-Jul-2004 (CT)  `front_args` and `rest_args` added to `__init__`
#    30-Jul-2004 (CT)  `base_indent2` added
#     2-Aug-2004 (CT)  `_write_to_stream` added
#     2-Aug-2004 (CT)  Methods put into alphabetical order
#     3-Aug-2004 (CT)  `__repr__` changed to use `as_tree` (to make `as_tree`
#                      work for cases where a node is stored as an attribute
#                      instead of a child)
#     3-Aug-2004 (CT)  `__str__` added (using `as_repr`)
#     3-Aug-2004 (CT)  s/as_repr/as_str/  and s/repr_format/str_format/
#     3-Aug-2004 (CT)  s/as_tree/as_repr/ and s/tree_format/repr_format/
#     3-Aug-2004 (CT)  `base_indent` moved from `init_arg_defaults` to class
#                      variable (save memory for spurious instance attribute)
#    12-Aug-2004 (CT)  s/recurse_args/recurse_kw/g
#    12-Aug-2004 (MG)  `default_cgi` added
#    12-Aug-2004 (MG)  `add`: unnest pass childrens (backward compatibility)
#    12-Aug-2004 (CT)  `indent_anchor` added
#    13-Aug-2004 (MG)  `formatted` Parameter `ht_width` added
#    13-Aug-2004 (CT)  `* args, ** kw` added to `_formatted_attrs`
#    13-Aug-2004 (CT)  Replaced `TFL.Caller.Scope` by
#                      `TFL.Caller.Object_Scope`
#    13-Aug-2004 (CT)  `node_type` removed
#    13-Aug-2004 (CT)  `base_indent2` removed
#    13-Aug-2004 (CT)  Doc-string added
#    23-Aug-2004 (CT)  `repr` and `repr_format` changed to make it
#                      doc-testable
#    23-Aug-2004 (CT)  Doc-string completed
#    24-Aug-2004 (CT)  `_init_kw` changed to protect `%` inside strings
#                      (which can be hidden in lists/tuples, <arrrgh>)
#    25-Aug-2004 (CT)  `_init_kw` changed again to protect `%` inside strings
#                      hidden in `NO_List` <double arrrgh>
#    25-Aug-2004 (MG)  `insert`: guard agains `None` children added
#    26-Aug-2004 (CT)  `_convert` moved in here (from `C.Node`)
#    26-Aug-2004 (CT)  `NL` added
#    17-Sep-2004 (CT)  Argument `indent_anchor` added to `formatted`
#    27-Sep-2004 (CT)  Doc-string improved
#     6-Sep-2005 (CT)  `formatted` changed to include `output_width` in
#                      `recurse_kw`
#    08-Dec-2005 (MG)  Sematic of `has_child` changed: returns now the child
#                      or None instead of True/False
#    12-Dec-2005 (CT)  `return None` removed from `has_child`
#    08-Nov-2006 (PGO) `NO_List` added that doesn't check for dups
#    20-Nov-2007 (MG)  Imports fixed
#     2-Apr-2008 (MG)  `Node` now inherits from `TFL.Meta.Object` instead of
#                      `object`
#    26-Feb-2012 (MG)  `__future__` imports added
#    23-May-2013 (CT)  Use `TFL.Meta.BaM` for Python-3 compatibility
#    10-Oct-2014 (CT)  Use `pyk.encoded` in `_write_to_stream`,
#                      unless `stream is sys.stdout`
#    19-Apr-2020 (CT)  Use "``" for doc strings, not "`'"
#    18-Nov-2022 (CT)  Add support for `children` in `_autoconvert`
#    ««revision-date»»···
#--

"""
A node of a structured document has attributes and children.
Attributes specify information about the node itself, e.g., name,
type, or children group index. Children define lower-level nodes of
the document's tree structure.

Attributes
==========

Normally, attributes must be passed as keyword arguments to
`__init__`.

- `init_arg_defaults` defines which attribute names are allowed for a
  specific node type and specify default values for these attributes.

- `_autoconvert` is a dictionary mapping attribute names to conversion
  functions called automatically during object initialization for all
  attribute values specified by the caller.

- `front_args` defines the names of attributes that must be passed as
  required (positional) arguments at the beginning of the argument list.

- `rest_args` defines the name of a single attribute that takes all
  non-named arguments which aren't `front_args`.

Children
========

For non-leaf nodes, children can be passed to `__init__` behind the
`front_args` and before the keyword arguments if any (if `rest_args`
is defined, children cannot be passed to `__init__`).

Children can be split into different groups.

- Each node type defines a children group index `cgi` to be used as
  default.

  `default_cgi` of the parent will be used to add a node with a `cgi`
  of None.

- `children_group_names` defines the names of the children groups
  supported by a node type.

  For `Node`, only the group `Body` is defined.

- For each children group xxx, a property xxx_children allows access
  to the group's children.

- `children` iterates over all children of all groups in some
  unspecified sequence (i.e., don't use `children` if you care about
  order).

Formats
=======

Formats define how to format a node and its children for a specific
purpose.

- `_list_of_formats` specifies the names of the applicable formats for
  the node-type in question (used by the metaclass; therefore, it must be
  defined by the class body).

- Each format is a string defined as a class variable.

- The meta class `M_Node` transforms the format strings into lists of
  formatter objects.

- Each line of the format string is handled by a separate formatter
  object that controls the indentation and other aspects of the
  formatting process.

- A line of a format string can contain

  * A leading indentation marker comprising zero or more `>`
    characters. Each single `>` corresponds to the number of spaces
    specified by `base_indent`.

    If base_indent is "  " (two spaces), a leading indentation marker
    of `>>>` will result in an leading indentation of six spaces for
    the line in question (relative to the other lines of the format).

  * Plain text.

    This is put into the formatted representation of the node as is.

  * A format string as required by Python's dictionary interpolation.
    This has the form `%(<someexpression>)<format-spec>`.

    `<someexpression>` is evaluated in the context of the node object
    and its `formatted` operation. The result is put in to the
    formatted representation of the node.

    `<format-spec>` is documented in the Python Library Reference
    manual, in the section `String Formatting Operations`.

    A simple example is `%(base_indent * 2)s` which will force a minimum
    width of two times `node.base_indent`.

  * A complex SDG format specification. This has the form
    `%(:<x_forms>:<key-specs>:)<format-spec>` and is described in more
    detail below.

  * A format line containing a complex SDG format specification can
    expand to more than a single line of output in the formatted
    representation of a node.

  * All other lines of a format specification must expand to a single
    line of output (otherwise indentation is messed up).

Complex SDG format specifications
=================================

Complex format specifications support the generation of multiple lines
of formatted output. A complex format specification can refer to
attributes, methods, and children of a node.

A complex format specification has the form::

    %(:<x_forms>:<key-specs>:)<format-spec>

- `x_forms` is optional and can specify additional formats to be used
  for formatting the lines generated by iterating over the values of
  `key-specs`.

  `x_forms` is a (possibly empty) list of assignments separated by `¡`
  characters (which means that `¡` cannot be included in the expansion
  of any of the additional formats). Each assignment has the form
  `key=<value>`. For `value`, white space is significant and appears
  in the output; for `key`, white space isn't allowed.

  The possible keys are:

  * `empty`: format to be used if `key-specs` doesn't expand to
    anything at all.

  * `front`: format to be used once at the front of the expansion of
    `key-specs` (before `head` of the first line).

    . The expansion of `front` can contain a single newline. To avoid
      messing up the indentation of the following lines, such a
      newline must be specified as `%(NL)s`.

  * `front0`: format to be used instead of `front` if `key-specs`
    yields only a single item (i.e., *no* newline).

  * `head`: format to be used at the beginning of every line of the
    expansion of `key-specs` (but after `sep`).

  * `rear`: format to be used once at the back of the expansion of
    `key-specs` (after `tail` of the last line).

    . The expansion of `rear` can contain a single newline. To avoid
      messing up the indentation of the following lines, such a
      newline must be specified as `%(NL)s`.

  * `rear0`: format to be used instead of `rear` if `key-specs`
    yields only a single item (i.e., *no* newline).

  * `sep`: format to be used as separator between the lines of the
    expansion of `key-specs` (it will be inserted between the
    indendation and the expansion of the following line [before
    `head`]).

  * `sep_eol`: format to be used as separator between the lines of the
    expansion of `key-specs` (it will be inserted at the end of the
    preceeding line [after `tail`]).

  * `tail`: format to be used at the end of every line of the
    expansion of `key-specs` (but before `sep_eol`).

- `key-specs` is a list of key specifications to be iterated over,
  separated by commas. Each single key specification has the form::

      <anchor><type><name>

  * `anchor` is either empty or a single `>` character. If `anchor` is
    specified, subsequent lines of the expansion of the key
    specification will be indented to the column where the expansion
    of the first line starts.

  * `type` is one of `.`, `*`, of `@`.

    . `.` specifies that the following name refers to an attribute of
      the node object. The value of that attribute must be None, a
      single string, or a sequence. If the value is None, the
      expansion is empty, if the value is a string, the expansion is a
      single line (with the formatted value of the string), otherwise
      the expansion comprises one line for each element of the
      sequence.

    . `@` specifies that the following name refers to a method of the
      node object. The return value of the function must be None or a
      sequence and is handled like just described above for attribute
      values.

    . `*` specifies that the following name refers to an attribute of
      the node object which contains a (possibly empty) list of
      children nodes. If the name contains a dot, the first part
      specifies the child-bearing attribute and the second part
      specifies the format to be used for recursion over the children
      nodes (by default, the format currently applied to the node
      object is used).

      The expansion comprises all the lines returned by the recursive
      application of the specified format to the children objects
      specified by the first part of `name`.

  If `key-specs` contains more than one key specification, `sep` and
  `sep_eol` are applied to any pair of lines of the expansion of the
  complex format specification. Thus, the result is different from the
  one achieved by using a separate complex format specification for
  each of the key specifications (even if all of those used the same
  `x_forms`).

- `format-spec` specifies how the lines expanded from `key-specs` are
  to be formatted. `format-spec` must be a valid Python format for
  dictionary interpolation. For the precision part of the
  `format-spec`, an extension is allowed to be able to use a computed
  minimum field width/precision -- this must be specified inside
  parenthesis `{}` and is itself evaluated as a format in the context
  of the node object and its `formatted` operation.

  A `{}` expression might want to use values like `indent_anchor`,
  `indent_offset`, `output_width`, and `ht_width` and can be an
  arithmetic expression.

Examples
========

`str_format` is used to convert a node to a string when
`__str__` is called::

    str_format           = '''
        %(__class__.__name__)s %(name)s
        >%(::*children:)s
    '''

The first line of `str_format` contains two simple format
specifications which expand to the class-name and name of a node. The
second line starts with an indentation level marker specifying a
relative indentation of one `base_indent` followed by a complex SDG
format specification. `%(::*children:)s` expands to a formatted
representation of the children of the node using the same format
specification applied to the node itself (in this case, `str_format`).

`repr_format` is used to convert a node to a string when `__repr__` or
`as_repr` is called. Depending on the definition of the node objects,
the result of `repr` might be valid input to `eval`::

    repr_format          = '''
        %(__class__.__name__)s
        >%(:front=( ¡front0=(¡rear=%(NL)s)¡rear0=)¡sep=, :>*children,>@_formatted_attrs:)s
    '''

The second line of `repr_format` contains a complex format
specification with `front`, `rear`, and `sep` values and key
specifications for recursive iteration over `children` followed by a
method call to `_formatted_attrs`.

>>> class T_Node (Node) :
...     init_arg_defaults = dict (hansi = "kieselack")
...
>>> root = T_Node (
...       T_Node ( Leaf ( name = "a.1")
...              , Leaf ( name = "a.2")
...              , name  = "a"
...              , hansi = "A"
...              )
...     , T_Node ( Node ( name = "b.x")
...              , Leaf ( name = "b.z")
...              , name = "b"
...              )
...     , name = "R"
...     )
>>> print (root)
T_Node R
    T_Node a
        Leaf a.1
        Leaf a.2
    T_Node b
        Node b.x
        Leaf b.z
>>> print (chr (10).join (root.as_repr ()))
T_Node
    ( T_Node
        ( Leaf
            (name = 'a.1')
        , Leaf
            (name = 'a.2')
        , hansi = 'A'
        , name = 'a'
        )
    , T_Node
        ( Node
            (name = 'b.x')
        , Leaf
            (name = 'b.z')
        , name = 'b'
        )
    , name = 'R'
    )
"""

from   _TFL              import TFL
from   _TFL.pyk          import pyk

import _TFL.Caller
import _TFL.I18N
import _TFL.NO_List
import _TFL._SDG
import _TFL._SDG.M_Node
import _TFL._Meta.Object

from   _TFL.predicate    import *
from   _TFL.pyk          import pyk

import sys

class Invalid_Node (Exception) :
    pass
# end class Invalid_Node

class _Node_NO_List_ (TFL.NO_List) :

    _real_name = "NO_List"

    def _check_value_duplicate (self, value) :
        """It may me necessary to add the same child multiple times to
           the same node, e.g. ones as a forward typedef, and later to
           actually perform the definition. Therefore, this check is disabled.
        """
        pass
    # end def _check_value

NO_List = _Node_NO_List_ # end def _Node_NO_List_

class Node (TFL.Meta.Object, metaclass = TFL.SDG.M_Node) :
    """Node of a structured document."""

    children             = property (lambda s : s._children_iter ())
    children_group_names = (Body, ) = range (1)
    default_cgi          = Body
    body_children        = property (lambda s : s.children_groups [s.Body])

    base_indent          = "    "
    NL                   = "\n"

    init_arg_defaults    = dict (name = "", cgi = 0)
    _autoconvert         = {}
    front_args           = ()
    rest_args            = None

    _list_of_formats     = ("repr_format", "str_format")
    repr_format          = """
        %(__class__.__name__)s
        >%(:front=( ¡front0=(¡rear=%(NL)s)¡rear0=)¡sep=, :\
           >*children,>@_formatted_attrs:)s
    """
    str_format           = """
        %(__class__.__name__)s %(name)s
        >%(::*children:)s
    """

    def __init__ (self, * children, ** kw) :
        self.parent = None
        n = len (children)
        for a in self.front_args :
            if children :
                if a in kw :
                    raise TypeError \
                        ( "%s() got multiple values for keyword argument %s"
                        % (self.__class__.__name__, a)
                        )
                kw [a]   = children [0]
                children = children [1:]
            elif a not in kw :
                raise TypeError \
                    ( "%s() takes exactly %s arguments (%s given)"
                    % (self.__class__.__name__, len (self.front_args), n)
                    )
        if self.rest_args and children :
            kw [self.rest_args] = children
            children            = ()
        self._init_kw (kw)
        if not self.name :
            self.name = "__%s_%d" % (self.__class__.__name__, self.id)
        self._reset_children ()
        if ac := self._autoconvert.get ("children") :
            children = [ac (self, "children", c) for c in children]
        self.add (* children)
    # end def __init__

    def add (self, * children) :
        """Append all `children` to `self.children`"""
        for c in un_nested (children) :
            self.insert (c)
    # end def add

    def as_repr (self, base_indent = None) :
        return self.formatted ("repr_format", base_indent)
    # end def as_repr

    def as_str (self, base_indent = None) :
        return self.formatted ("str_format", base_indent)
    # end def as_str

    def destroy (self) :
        for c in self.children :
            c.destroy ()
        self._reset_children ()
        self.parent = None
    # end def destroy

    def formatted ( self, format_name
                  , base_indent   = None
                  , output_width  = 79
                  , indent_offset = 0
                  , indent_anchor = None
                  , ht_width      = 0
                  , ** kw
                  ) :
        if base_indent is None :
            base_indent = self.base_indent
        recurser   = "formatted"
        formatters = getattr (self, format_name)
        recurse_kw = dict \
            ( format_name  = format_name
            , base_indent  = base_indent
            , output_width = output_width
            , ** kw
            )
        context = TFL.Caller.Object_Scope (self)
        for f in formatters :
            indent = f.indent_level * base_indent
            io     = indent_offset  + len (indent)
            context.locals ["indent_offset"] = io
            if indent_anchor is None :
                context.locals ["indent_anchor"] = io
            else :
                context.locals ["indent_anchor"] = indent_anchor + len (indent)
            for l in f (self, context) :
                x = indent + l
                yield x
    # end def formatted

    def has_child (self, child_name, transitive = True) :
        """Checks if this node or one of this childs has a node named
           `child_name`.
        """
        child_name = self._child_name (child_name)
        for children in pyk.itervalues (self.children_groups) :
            if child_name in children :
                return children [child_name]
        if transitive :
            for c in self.children :
                child = c.has_child (child_name, transitive = True)
                if child is not None :
                    return child
    # end def has_child

    def insert (self, child, index = None, delta = 0) :
        """Insert `child` to `self.children` at position `index`
           (None means append).
        """
        if child is not None :
            cgi = getattr (child, "cgi", None)
            if cgi is None :
                cgi = self.default_cgi
            else :
                self.default_cgi = min (cgi, self.default_cgi)
            self._insert (child, index, self.children_groups [cgi], delta)
    # end def insert

    def _child_name (self, child_name) :
        if isinstance (child_name, Node) :
            child_name = child_name.name
        return child_name
    # end def _child_name

    def _children_iter (self) :
        for group in pyk.itervalues (self.children_groups) :
            yield from group
    # end def _children_iter

    def _convert (self, value, Class, * args, ** kw) :
        if value and isinstance (value, pyk.string_types) :
            value = Class (value.strip (), * args, ** kw)
        return value
    # end def _convert

    def _formatted_attrs (self, * args, ** kw) :
        for k, v in sorted (pyk.iteritems (self.init_arg_defaults)) :
            a = getattr (self, k)
            if a != v :
                if str != str and isinstance (a, str) :
                    ### Python2: encode unicode to avoid `u`-prefix
                    a = TFL.I18N.encode_o (a)
                yield "%s = %r" % (k, a)
    # end def _formatted_attrs

    def _init_kw (self, kw) :
        kw_err = {}
        for k, v in pyk.iteritems (self.init_arg_defaults) :
            if not hasattr (self, k) :
                setattr (self, k, v)
        for k, v in pyk.iteritems (kw) :
            if k in self.init_arg_defaults :
                ### protect `%` characters hidden inside `v` to avoid
                ### ValueErrors during formatting
                if isinstance (v, pyk.string_types) :
                    v = v.replace ("%", "%%")
                elif isinstance (v, (tuple, list, TFL.NO_List)) :
                    vin = v
                    v   = []
                    for x in vin :
                        if isinstance (x, pyk.string_types) :
                            x = x.replace ("%", "%%")
                        v.append (x)
                if k in self._autoconvert :
                    v = self._autoconvert [k] (self, k, v)
                setattr (self, k, v)
            else :
                kw_err [k] = v
        if kw_err :
            print (self.__class__, self.init_arg_defaults)
            raise TypeError ("unexpected keyword arguments: %s" % kw_err)
    # end def _init_kw

    def _insert (self, child, index, children, delta = 0) :
        if child :
            if index is None :
                index = len (children)
            child.parent = self
            children.insert (index, child, delta)
    # end def _insert

    def _reset_children (self) :
        self.children_groups = dict \
            ((i, NO_List ()) for i in self.children_group_names)
    # end def _reset_children

    def _write_to_stream (self, gen, stream, gauge = None) :
        encoded = pyk.encoded
        if stream is None :
            encoded = lambda x : x
            stream  = sys.stdout
        for x in gen :
            stream.write  (encoded (x))
            stream.write  (encoded ("\n"))
            if gauge is not None :
                gauge.inc ()
    # end def _write_to_stream

    def __iter__ (self) :
        yield self
        for c in self.children :
            yield from iter (c)
    # end def __iter__

    def __repr__ (self) :
        return "(%s)" % ("\n".join (self.as_repr ()), )
    # end def __repr__

    def __str__ (self) :
        return "\n".join (self.as_str ())
    # end def __str__

# end class Node

class Leaf (Node) :
    """Leaf node which doesn't allow children"""

    children_group_names = () ### doesn't allow any children

    def insert (self, child, index = None, delta = 0) :
        raise Invalid_Node (self, child)
    # end def insert

# end class Leaf

### debugging code to be pasted into an interactive interpreter
"""
from _TFL._SDG.Node import *
class T_Node (Node) :
    init_arg_defaults = dict (hansi = "kieselack")

root = T_Node \
    ( T_Node ( Leaf ( name = "a.1")
             , Leaf ( name = "a.2")
             , name  = "a"
             , hansi = "A"
             )
    , T_Node ( Node ( name = "b.x")
             , T_Node ( Node ( name = "b.y.1")
                      , Node ( name = "b.y.2")
                      , name  = "b.y"
                      , hansi = "B.Y"
                      )
             , Leaf ( name = "b.z")
             , name = "b"
             )
    , name = "R"
    )
print (root)
print (repr (root))

from _TFL._SDG.Node import *
class T_Node (Node) :
    init_arg_defaults = dict (hansi = "kieselack")

root = T_Node \
    ( T_Node ( name  = "a"
             , hansi = 42
             )
    , name = "R"
    )
print (chr (10).join (root.as_repr ()))
"""

if __name__ != "__main__" :
    TFL.SDG._Export ("*")
### __END__ TFL.SDG.Node
