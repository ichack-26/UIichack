# -*- coding: utf-8 -*-
# Copyright (C) 2017-2020 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.App_Test
#
# Purpose
#    Define application tests
#
# Revision Dates
#     8-May-2017 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL                       import TFL

from   _TFL                       import sos
from   _TFL.FCM                   import open_tempfile
from   _TFL.Filename              import Filename
from   _TFL.pyk                   import pyk
from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL._Meta.Property        import Alias_Property

import _TFL.Decorator
import _TFL._Meta.Object

from   timeit                     import default_timer as _timer

import difflib
import itertools
import logging
import sys
import subprocess

class _Result_ (TFL.Meta.Object) :
    """Expected result of application test."""

    def _diffs (self, old_content, new_content, ** kwds) :
        old = old_content.split ("\n")
        new = new_content.split ("\n")
        kwds.setdefault ("lineterm", "")
        return list (difflib.unified_diff (old, new, ** kwds))
    # end def _diffs

    def __bool__ (self) :
        return bool (self.content)
    # end def __bool__

    def __ne__ (self, rhs) :
        return not (self == rhs)
    # end def __ne__

# end class _Result_

class Result_File (_Result_) :
    """Expected result of application test specified as file_name."""

    def __init__ (self, file_name, encodings = ()) :
        self.file_name = sos.expanded_path (file_name)
        self.encodings = encodings
    # end def __init__

    @Once_Property
    def content (self) :
        with open (self.file_name, "rb") as f :
            return f.read ().strip ()
    # end def content

    def diff (self, new_content) :
        if self != new_content :
            old     = str (self)
            new     = pyk.decoded   (new_content, * self.encodings)
            diffs   = self._diffs \
                (old, new, fromfile = self.file_name, tofile = "Result of test")
            diff_no = len (diffs)
            d_name  = Filename (".diff", self.file_name)
            with open (d_name, "wb") as f :
                f.write (pyk.encoded ("\n".join (diffs)))
            return "%d difference%s (see %s)" % \
                (diff_no, "" if diff_no == 1 else "s", d_name)
    # end def diff

    def __eq__ (self, rhs) :
        return self.content == rhs
    # end def __eq__

    def __str__ (self) :
        return pyk.decoded (self.content, * self.encodings)
    # end def __str__

# end class Result_File

class Result_String (_Result_) :
    """Expected result of application test specified as string."""

    def __init__ (self, content = "") :
        self.content = content
    # end def __init__

    def diff (self, new_content) :
        if self != new_content :
            old     = self.content
            new     = pyk.decoded (new_content)
            diffs   = self._diffs \
                ( old, new
                , fromfile = "Expected"
                , tofile   = "Result of test"
                )
            diff_no = sum \
                (1 for d in diffs if d.startswith ("@@") and d.endswith ("@@"))
            sep     = "\n    "
            return "%d difference%s:%s%s" % \
                ( diff_no, "" if diff_no == 1 else "s", sep
                , sep.join (diffs)
                )
    # end def diff

    def __eq__ (self, rhs) :
        return self.content == pyk.decoded (rhs)
    # end def __eq__

    def __str__ (self) :
        return self.content
    # end def __str__

# end class Result_String

class Run (TFL.Meta.Object) :
    """Run one application test and check expected error and output."""

    def __init__ (self, args, expected_error, expected_output) :
        self.args            = args
        self.expected_error  = expected_error
        self.expected_output = expected_output
        r_error, r_output    = self._run (args)
        self.error_diff      = expected_error.diff  (r_error)
        self.output_diff     = expected_output.diff (r_output)
    # end def __init__

    def _read_result (self, file, name) :
        file.flush ()
        file.seek  (0)
        return file.read ().strip ()
    # end def _read_result

    def _run (self, args) :
        with self._std_err_out () as (stderr, stdout) :
            start = _timer ()
            subp  = subprocess.Popen \
                ( args
                , env     = dict (sos.environ)
                , stderr  = stderr
                , stdout  = stdout
                )
            subp.wait ()
            self.time = _timer () - start
        return self.resulting_error, self.resulting_output
    # end def _run

    @TFL.Contextmanager
    def _std_err_out (self) :
        with open_tempfile (mode = "r+b") as (stdout, out_name) :
            with open_tempfile (mode = "r+b") as (stderr, err_name) :
                yield stderr, stdout
                self.resulting_error  = self._read_result (stderr, err_name)
                self.resulting_output = self._read_result (stdout, out_name)
    # end def _std_err_out

    def __bool__ (self) :
        return not (self.error_diff or self.output_diff)
    # end def __bool__

# end class Run

class _Spec_ (TFL.Meta.Object) :
    """Specification of application test."""

    expected_error   = Result_String ()
    expected_output  = Result_String ()
    _name            = None
    kwd_names        = ("expected_error", "expected_output")
    kwd_names_       = ("name", )

    def __init__ (self, * args, ** kwds) :
        self.app_args = args
        self.pop_to_self (kwds, * self.kwd_names)
        self.pop_to_self (kwds, * self.kwd_names_, prefix = "_")
        if kwds :
            raise TypeError \
                ( "Unknown keyword arguments:\n  %s\n  Use any of: %s"
                % (sorted (kwds), sorted (self.kwd_names + self.kwd_names_))
                )
    # end def __init__

    def __call__ (self, py_executable, py_options = ()) :
        args   = self.head_args (py_executable, * py_options) + self.app_args
        return Run (args, self.expected_error, self.expected_output)
    # end def __call__

    @Once_Property
    def name (self) :
        result = self._name
        if result is None :
            result = self.app_name
        return result
    # end def name

# end class _Spec_

class File (_Spec_) :
    """Specification of application test with `file_name` of tested app."""

    app_name          = Alias_Property ("file_name")

    def __init__ (self, file_name, * args, ** kwds) :
        self.file_name = file_name
        self.__super.__init__ (* args, ** kwds)
    # end def __init__

    def head_args (self, * args) :
        return args + (sos.expanded_path (self.file_name), )
    # end def head_args

# end class File

class Module (_Spec_) :
    """Specification of application test with `mod_name` of tested app."""

    app_name          = Alias_Property ("mod_name")

    def __init__ (self, mod_name, * args, ** kwds) :
        self.mod_name = mod_name
        self.__super.__init__ (* args, ** kwds)
    # end def __init__

    def head_args (self, * args) :
        return args + ("-m", self.mod_name)
    # end def head_args

# end class Module

class Non_Python (_Spec_) :
    """Specification of non-python application test."""

    @Once_Property
    def app_name (self) :
        return self.app_args [0]
    # end def app_name

    def head_args (self, * args) :
        return ()
    # end def head_args

# end class Non_Python

__App_Tests__ = \
    [ Non_Python
        ( "echo", "42"
        , expected_output = Result_String ("42")
        , name            = "Correct test with echo"
        )
    , Non_Python
        ( "echo", "42"
        , expected_output = Result_String ("23")
        , name            = "Failing test with echo"
        )
    ]

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.App_Test
