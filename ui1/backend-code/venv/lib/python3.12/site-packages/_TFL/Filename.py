# -*- coding: utf-8 -*-
# Copyright (C) 1998-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Filename
#
# Purpose
#    Model filename
#
# Revision Dates
#    16-Apr-1998 (CT) Creation
#    20-Apr-1999 (CT) `__str__` and `__repr__` added
#    16-Jul-1999 (CT) `abs_directory` added
#    16-Jul-1999 (CT) `normpath` applied to `directory`
#    19-Jul-1999 (CT) Use `os.path.abspath` if available
#    17-Sep-1999 (MY) Complete documentation of the module
#    29-Sep-1999 (MY) Spellcheck the comments and put comment-endmarker in
#                     a separate line
#    28-Oct-1999 (CT) `base_ext` added
#     7-Dec-1999 (CT) Hack around bug in os.path.split of Win32 Python 1.5.1
#     7-Dec-1999 (CT) `abs_name` added
#     3-Feb-2000 (CT) `default_dir` added
#     3-May-2000 (CT) `__cmp__` and `__hash__` added
#    31-Jul-2000 (CT) `make_absolute` added
#    18-Dec-2000 (CT) `default_rel` added
#    19-Feb-2001 (CT) Stub for `relative_to` added
#    20-Feb-2001 (CT) `relative_to` added (as implemented by (ARU) and (MFE))
#    20-Feb-2001 (CT) Unit tests for `relative_to` added
#    26-Feb-2001 (ARU) Unit tests for 'Filename' constructor/selector axioms
#                      added
#    26-Feb-2001 (CT) `__init__` changed to apply `path.normpath` only to
#                     non-empty directories
#    26-Feb-2001 (CT) Unit tests corrected
#     3-May-2001 (CT) Doc-test added and style of test formatting changed
#    12-Nov-2001 (CT) `posixified` added
#    21-Feb-2001 (MSF) restored revision 1.21 (unittest is guarded by _debug_)
#     7-Mar-2003 (CT)  `relative_to` changed to include `.` for same
#                      directory
#     7-Mar-2003 (CT) 1.5.2 cruft removed from `relative_to`
#    29-Apr-2004 (MUZ) Corrected unittests
#     6-May-2004 (GWA) 'name_as_dir' added
#    24-May-2004 (CT)  `name_as_dir` removed
#    24-May-2004 (CT)  `Dirname` added
#    25-May-2004 (GWA) `Dirname` Doctests added
#    25-May-2004 (GWA) Bug fix in Dirname - `Dirname` Doctest with existing
#                      file added
#    28-May-2004 (GWA) `Dirname` pickles itself as `Filename`
#     7-Jun-2004 (GWA) `lower_lvl_dir` with Doctest added
#     7-Jun-2004 (GWA) `lower_lvl_dir` removed
#    15-Jul-2004 (CT)  `Function` replaced by staticmethod
#    15-Jul-2004 (CT)  Calls to `string` functions replaced by calls to `str`
#                      methods
#    18-Aug-2004 (CT)  `Filename.__nonzero__` changed to check `base` instead
#                      of `name`
#    30-Aug-2004 (GWA) `relative_to` corrected for win32 environment,
#                      `_cmp_file_str` introduced for posix and win32
#                      environment
#     6-Sep-2004 (GWA) `_cmp_file_str` -> reworked to `_is_file_str_equal`
#     6-Sep-2004 (GWA) `_is_file_str_equal` replaced with `normalized`
#     6-Sep-2004 (GWA) `normalized` changed in non Unix/Windows Environment
#     7-Sep-2004 (CT)  `_as_dir` and `_as_file` added and used
#     7-Sep-2004 (CT)  `as_dir` and `as_file` added
#     7-Sep-2004 (CT)  Methods defined in alphabetical order
#    28-Sep-2004 (CT)  Use `isinstance` instead of type comparison
#    24-Mar-2005 (CT)  Moved into package `TFL`
#    23-Mar-2006 (CED) `real_directory`, `real_name` added
#     7-Nov-2007 (CT)  Doctest fixed (removed `lib/python`)
#    23-Jun-2009 (CT)  `split_ext` added to deal with changed behavior of
#                      `os.path.splitext` in Python 2.6+
#    20-May-2010 (CT) `__main__` added
#    16-May-2012 (CT) Fix `abs_name`, `real_name`, `relative_to` for `Directory`
#                     (result must NOT contain `base_ext`)
#    10-Oct-2016 (CT) Fix doctest of `Dirname (__file__)`
#    19-Aug-2019 (CT) Import `unicode_literals`, fix doctest accordingly
#     6-Apr-2020 (CT) Add `__fspath__`
#     8-Apr-2020 (CT) Change `__str__` to return `.name`
#    25-May-2020 (CT) Improve `relative_to`
#                     + return `self.name`, not empty, if no relation
#                     + don't add leading `./`
#    ««revision-date»»···
#--

"""Provides a class that represents a filename with its parts: path, base
   name, and file extension.
"""

from   _TFL                       import TFL

from   _TFL.portable_repr         import print_prepr
from   _TFL.predicate             import *
from   _TFL.pyk                   import pyk
from   _TFL                       import sos
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL._Meta.Object
import _TFL.Environment

@totally_ordered
class Filename (TFL.Meta.Object) :
    """Represents a filename with its parts: path, base name and file
       extension.

       The parts of the filename are provided by the attributes:

       base        basic file name
       ext         extension of the filename
       directory   path of the filename
       base_ext    `base` + `ext`
       name        complete filename including `directory`, `base`, and `ext`

       For example:

       >>> f=Filename ("/a/b/c/d/e.f")
       >>> print_prepr (f.name)
       '/a/b/c/d/e.f'
       >>> print_prepr (f.base)
       'e'
       >>> print_prepr (f.ext)
       '.f'
       >>> print_prepr (f.directory)
       '/a/b/c/d'
       >>> print_prepr (f.base_ext)
       'e.f'

       >>> f=Filename ("spam.py")
       >>> print_prepr (f.name)
       'spam.py'
       >>> f=Filename ("spam", ".py")
       >>> print_prepr (f.name)
       'spam.py'
       >>> f=Filename ("spam.py", ".pyo")
       >>> print_prepr (f.name)
       'spam.py'
       >>> f=Filename (".pyo", "spam.py")
       >>> print_prepr (f.name)
       'spam.pyo'
       >>> f=Filename ("spam.py", "/usr/local/src")
       >>> print_prepr (f.name)
       '/usr/local/spam.py'
       >>> f=Filename ("spam.py", "/usr/local/src/")
       >>> print_prepr (f.name)
       '/usr/local/src/spam.py'
       >>> f=Filename (".pyo", "spam.py", "/usr/local/src/")
       >>> print_prepr (f.name)
       '/usr/local/src/spam.pyo'
       >>> f=Filename ("../spam.py", "/usr/local/src/")
       >>> print_prepr (f.name)
       '../spam.py'
       >>> f=Filename ("spam.py", default_dir = "/usr/local/src")
       >>> print_prepr (f.name)
       '/usr/local/src/spam.py'
       >>> f=Filename ("spam.py")
       >>> f.directory == sos.getcwd ()
       0
       >>> f=Filename ("spam.py", absolute=1)
       >>> f.directory == sos.getcwd ()
       1
       >>> f=Filename ("../spam.py", "/usr/local/src/", default_rel=1)
       >>> print_prepr (f.name)
       '/usr/local/spam.py'

       >>> fn = Filename ("/tmp/filename_test.test")
       >>> f  = open     (fn, "w").close ()
       >>> sos.remove    (fn)

       >>> print_prepr (fn.name)
       '/tmp/filename_test.test'
       >>> print_prepr (fn + ".1")
       '/tmp/filename_test.test.1'
       >>> print_prepr ("~" + fn)
       '~/tmp/filename_test.test'

    """

    as_dir    = property (lambda s : s._as_dir  (s.name))
    as_file   = property (lambda s : s._as_file (s.name))

    _base_ext = property (lambda s : s.base_ext)

    def __init__ (self, name, * defaults, ** kw) :
        """Constructs the filename from the `name` and the optional `defaults`
           for `name`, `directory`, and `extension`. Default types that are
           already specified are ignored.

           name         name of the file specifying one or more of the
                        components `directory`, `base`, and `ext`

           defaults     arbitrary number of strings (or Filenames) with
                        defaults for `directory`, `base`, and `ext`

                        (if a default should just define a directory, it must
                        end with a directory separator -- otherwise its last
                        part will be interpreted as `base`)

           default_dir  specify a default directory (this string can be
                        specified with or without trailing directory separator)

           absolute     force name to be absolute

           default_rel  Interpret relative name relative to
                        default_dir (instead of to current working directory)

        """
        if isinstance (name, Filename) :
            name = name.name
        path         = sos.path
        default_dir  = kw.get ("default_dir")
        absolute     = kw.get ("absolute")
        default_rel  = kw.get ("default_rel") and not path.isabs (name)
        (self.directory, bname) = path.split (name)
        if name.endswith (sos.sep) :
            ### fix bug in Win32 Python 1.5.1
            ### XXX is this still necessary ???
            self.directory = path.join (self.directory, bname)
            bname          = ""
        (self.base, self.ext) = self.split_ext (bname)
        if default_dir :
            if isinstance (default_dir, pyk.string_types) :
                default_dir = self._as_dir (default_dir)
            defaults = (default_dir, ) + defaults
        for default in defaults :
            if isinstance (default, pyk.string_types) :
                default = Filename (default)
            defd = default.directory
            if defd :
                if not self.directory :
                    self.directory = defd
                elif default_rel :
                    self.directory = path.join (defd, self.directory)
                    default_rel    = 0
            if not self.base :
                self.base = default.base
            if not self.ext :
                self.ext  = default.ext
        self.base_ext  = self.base + self.ext
        self.directory = path.expanduser (self.directory)
        if absolute :
            self.make_absolute ()
        else :
            if self.directory :
                ### in Python 2.0, path.normpath ("") returns "."
                self.directory = path.normpath (self.directory)
            self.name = path.join (self.directory, self.base_ext)
    # end def __init__

    def abs_directory (self) :
        """Return the directory name converted to absolute path string."""
        result = sos.path.abspath (self.directory)
        if (not result) :
            result = sos.getcwd ()
        return result
    # end def abs_directory

    def abs_name (self) :
        """Return the absolute filename corresponding to `self`."""
        return sos.path.join (self.abs_directory (), self._base_ext)
    # end def abs_name

    @classmethod
    def _as_dir (cls, name) :
        path = sos.path
        for sep in (path.sep, path.altsep) :
            if sep and name.endswith (sep) :
                break
        else :
            name = "%s%s" % (name, path.sep)
        return name
    # end def _as_dir

    @classmethod
    def _as_file (cls, name) :
        path = sos.path
        for sep in (path.sep, path.altsep) :
            if sep and name.endswith (sep) :
                name = name [:-len (sep)]
                break
        return name
    # end def _as_file

    def directories (self) :
        return list (d for d in self.directory.split (sos.sep) if d)
    # end def directories

    def make_absolute (self) :
        """Make filename absolute"""
        self.directory = self.abs_directory ()
        self.name      = self.abs_name      ()
    # end def make_absolute

    def real_directory (self) :
        """Return the absolute directory name after resolving all
           symlinks.
        """
        result = self.abs_directory ()
        if hasattr (sos.path, "realpath") :
            result = sos.path.realpath (result)
        return result
    # end def real_directory

    def real_name (self) :
        """Return the absolute filename corresponding to `self`
           after resolving all symlinks.
        """
        return sos.path.join (self.real_directory (), self._base_ext)
    # end def real_name

    def relative_to (self, other) :
        """Returns `self` converted to a path relative to `other`
          (`self.name`, if that's not possible)

           For example:

           >>> f=Filename ("/a/b/c/xxx.x")
           >>> g=Filename ("/a/b/d/yyy.y")
           >>> h=Filename ("/xyz/a/b/d/zzz.z")
           >>> print_prepr (f.relative_to (g))
           '../c/xxx.x'
           >>> print_prepr (g.relative_to (f))
           '../d/yyy.y'
           >>> print_prepr (g.relative_to (h))
           '/a/b/d/yyy.y'
        """
        if not other :
            return ""
        left   = self.__class__ (self,  absolute = 1)
        right  = self.__class__ (other, absolute = 1)
        pairs  = paired (left.directories (), right.directories ())
        i      = 0
        for (l, r) in pairs :
            if (  l is None or r is None
               or self.normalized (l) != self.normalized (r)
               ) :
                break
            i = i + 1
        if not i :
            return self.name
        differences = pairs  [i:]
        up          = [".." for (l, r) in differences if r]
        down        = [l    for (l, r) in differences if l]
        return "/".join (((up + down)) + [self._base_ext])
    # end def relative_to

    @classmethod
    def split_ext (cls, name) :
        ### In Python 2.6, the behavior of `os.path.splitext` changed for
        ### names starting with a leading dot
        if name.startswith (".") :
            base, ext  = sos.path.splitext (name [1:])
            base       = "." + base
            if not ext :
                base, ext = "", base
        else :
            base, ext  = sos.path.splitext (name)
        return base, ext
    # end def split_ext

    def __add__ (self, rhs) :
        return self.name + rhs
    # end def __add__

    def __bool__ (self) :
        return bool (self.base)
    # end def __bool__

    def __eq__ (self, other) :
        if isinstance (other, Filename) :
            return self.name == other.name
        else :
            return self.name == other
    # end def __eq__

    def __fspath__ (self) :
        return self.name
    # end def __fspath__

    def __hash__ (self) :
        return hash (self.name)
    # end def __hash__

    def __lt__ (self, other) :
        if isinstance (other, Filename) :
            return self.name < other.name
        else :
            return self.name < other
    # end def __lt__

    def __radd__ (self, lhs) :
        return lhs + self.name
    # end def __radd__

    def __repr__ (self) :
        """Returns a string representation of the Filename object"""
        return "%s (%s)" % (self.__class__.__name__, self.name)
    # end def __repr__

    def __str__ (self) :
        """Returns the string representation of the filename"""
        return self.name
    # end def __str__

    normalized = staticmethod (identity)

    if TFL.Environment.system == "posix" :
        posixified = staticmethod (identity)
    elif TFL.Environment.system == "win32" :
        normalized = staticmethod (str.lower)

        def posixified (filename) :
            """Return `filename` in posix syntax"""
            return filename.replace ("\\", "/")
        posixified = staticmethod (posixified)
    else :
        def posixified (filename) :
            raise NotImplementedError \
                ( "Function Filename.posixified for system %s"
                % TFL.Environment.system
                )
        posixified = staticmethod (posixified)
    # end if TFL.Environment.system

# end class Filename

class Dirname (Filename) :
    """Represents a directory name.

       Examples :

        >>> g=Dirname ('p/xyz.ddb/')
        >>> g
        Dirname (p/xyz.ddb/)
        >>> g=Dirname ('p/xyz.ddb')
        >>> g
        Dirname (p/xyz.ddb/)
        >>> print_prepr (g.base_ext)
        'xyz.ddb'
        >>> print_prepr (g.base)
        'xyz.ddb'
        >>> print_prepr (g.ext)
        ''
        >>> g = Dirname (__file__)
        >>> g.name.endswith ('/_TFL/') or g.name == "./"
        True
    """

    _base_ext = ""

    def __init__ (self, name, ** kw) :
        if isinstance (name, Filename) :
            name = name.name
        path = sos.path
        if path.isfile (name) and not path.isdir (name) :
            name, _ = path.split (name)
        self.__super.__init__ (self._as_dir (name), ** kw)
        if self.name :
            dirs = self.directories ()
            if dirs :
                self.base_ext = self.base = dirs [-1]
    # end def __init__

# end class Dirname

if __name__ != "__main__" :
    TFL._Export ("*")
else :
    import _TFL.CAO

    def _main (cmd) :
        result = Filename \
            ( * cmd.argv
            , absolute    = cmd.absolute
            , default_dir = cmd.default_dir
            , default_rel = cmd.rel_to_default_dir
            )
        if cmd.Directory :
            result = Dirname (result.name)
        print (result.name)
    # end def _main

    _Command = TFL.CAO.Cmd \
        ( handler     = _main
        , args        = ("name:P?Name fragment(s) to assemble", )
        , opts        =
            ( "-absolute:B?Convert to an absolute filename"
            , "-default_dir:P?Default directory"
            , "-Directory:B?Result is directory name"
            , "-rel_to_default_dir:B"
                "?Interpret relative name relative to default_dir"
            )
        , min_args    = 1
        )

    _Command ()
### __END__ TFL.Filename
