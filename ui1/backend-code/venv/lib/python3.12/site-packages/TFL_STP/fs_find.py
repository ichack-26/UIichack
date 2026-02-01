# -*- coding: utf-8 -*-
# Copyright (C) 2016-2020 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL_STP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL_STP.fs_find
#
# Purpose
#    Find files and directory names
#
# Revision Dates
#    13-Oct-2016 (CT) Creation
#    23-Feb-2017 (CT) Move to package `TFL_STP` (from `_TFL`)
#    12-May-2017 (CT) Add `Filter.startswith`
#    ««revision-date»»···
#--

import os
import re

_cwd        = os.curdir
_cwd_prefix = os.curdir + os.sep
_undef      = object ()

class Filter (object) :
    """Filter to include or exclude file- and directory names.

    >>> def show (ds) :
    ...     print (", ".join ("%s" % d for d in ds))

    >>> contains_slash = Filter.contains ("/")
    >>> contains_SVG   = Filter.contains ("SVG")
    >>> dirs = ['_Meta', '_SDG', '_SDG/_C', '_SDG/_XML', '_SDG/_XML/_SVG']

    >>> xs = Filter (dir_exclude = contains_slash)
    >>> ds = dirs [:]
    >>> xs.prune_dirs (ds)
    >>> show (ds)
    _Meta, _SDG

    >>> iv_xs = Filter (dir_include = contains_SVG, dir_exclude = contains_slash)
    >>> ds = dirs [:]
    >>> iv_xs.prune_dirs (ds)
    >>> show (ds)
    _Meta, _SDG, _SDG/_XML/_SVG

    >>> iv_xa = Filter (dir_include = contains_SVG)
    >>> ds = dirs [:]
    >>> iv_xa.prune_dirs (ds)
    >>> show (ds)
    _SDG/_XML/_SVG

    >>> contains_e_or_V = Filter.combine (any, Filter.contains ("e"), Filter.contains ("V"))
    >>> ie_xa = Filter (dir_include = contains_e_or_V)
    >>> ds = dirs [:]
    >>> ie_xa.prune_dirs (ds)
    >>> show (ds)
    _Meta, _SDG/_XML/_SVG

    """

    all = staticmethod (lambda d : True)

    @staticmethod
    def combine (combiner, * predicates) :
        """Predicate that combines `predicates` with `combiner`."""
        return lambda x : combiner (tuple (p (x) for p in predicates))
    # end def combine

    @staticmethod
    def contains (substr) :
        """Predicate for directories/files that name containing `substr`."""
        return lambda x : substr in x
    # end def contains

    @staticmethod
    def equal (name) :
        """Predicate for directories/files with name equal to `name`."""
        return lambda x : x == name
    # end def equal

    @staticmethod
    def IN (* names) :
        """Predicate for directories/files with a name in `names`."""
        return lambda x : x in names
    # end def IN

    @staticmethod
    def has_extension (* extensions) :
        """Predicate for directories/files with any of the `extensions`."""
        pat = "|".join (r"\." + x.lstrip (".") for x in extensions)
        rx  = pat if len (extensions) == 1 else "(" + pat + ")"
        return re.compile (rx + "$").search
    # end def has_extension

    @staticmethod
    def startswith (* prefixes) :
        """Predicate for directories/files with a name starting with any of `prefixes`."""
        return lambda x : x.startswith (prefixes)
    # end def startswith

    def __init__ \
            ( self
            , include     = None
            , exclude     = _undef
            , dir_include = None
            , dir_exclude = _undef
            ) :
        self.include      = include
        self.exclude      = exclude if exclude is not _undef \
            else (None if include is None else self.all)
        self.dir_include  = dir_include
        self.dir_exclude  = dir_exclude if dir_exclude is not _undef \
            else (None if dir_include is None else self.all)
    # end def __init__

    def __call__ (self, name) :
        """Return True if `name` is included or not excluded."""
        return self.allow (name)
    # end def __call__

    def allow (self, name) :
        """Return True if `name` is included or not excluded."""
        include = self.include
        exclude = self.exclude
        result  = any \
            ( ( include is not None and    include (name)
              , exclude is     None or not exclude (name)
              )
            )
        return result
    # end def allow

    def allow_dir (self, dir_name) :
        """Return True if `dir_name` is included or not excluded."""
        include = self.dir_include
        exclude = self.dir_exclude
        result  = any \
            ( ( include is not None and    include (dir_name)
              , exclude is     None or not exclude (dir_name)
              )
            )
        return result
    # end def allow_dir

    def prune_dirs (self, dirs) :
        """Remove all entries from `dirs` that are not included or excluded."""
        include = self.dir_include
        exclude = self.dir_exclude
        if include is not None or exclude is not None :
            allow_dir = self.allow_dir
            dirs [:] = [d for d in dirs if allow_dir (d)]
    # end def prune_dirs

# end class Filter

def dir_as_prefix (dir) :
    """Normalized prefix for `dir`: remove "." and "./"."""
    if dir == _cwd :
        return ""
    elif dir.startswith (_cwd_prefix) :
        return dir [len (_cwd_prefix):]
    else :
        return dir
# end def dir_as_prefix

def _walk (* paths, ** kw) :
    """Generate all directories in `paths` allowed by `filter`, if any."""
    filter = kw.pop ("filter", None)
    if kw :
        raise TypeError \
            ("Unkown arguments keyword passed to dir_iter: %s" % sorted (kw))
    prune_dirs = getattr (filter, "prune_dirs", None)
    for path in paths :
        if os.path.isdir (path) :
            for root, dirs, files in os.walk (path, topdown = True) :
                if prune_dirs is not None :
                    prune_dirs (dirs)
                if root == path or filter is None or filter.allow_dir (root) :
                    base = dir_as_prefix (root)
                    yield base, dirs, files, filter
# end def _walk

def dir_iter (* paths, ** kw) :
    """Generate all directories in `paths` allowed by `filter`, if any."""
    for base, dirs, files, filter in _walk (* paths, ** kw) :
        for d in dirs :
            if filter is None or filter (d) :
                yield os.path.join (base, d) if base else d
# end def dir_iter

def directories (* paths, ** kw) :
    """List of all directories in `paths` allowed by `filter`, if any."""
    return list (dir_iter (* paths, ** kw))
# end def directories

def file_iter (* paths, ** kw) :
    """Generate all files in `paths` allowed by `filter`, if any."""
    for base, dirs, files, filter in _walk (* paths, ** kw) :
        for f in files :
            if filter is None or filter (f) :
                yield os.path.join (base, f) if base else f
# end def file_iter

def files (* paths, ** kw) :
    """List of all files in `paths` allowed by `filter`, if any."""
    return list (file_iter (* paths, ** kw))
# end def files

### __END__ TFL_STP.fs_find
