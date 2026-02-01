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
#    TFL.run_app_tests
#
# Purpose
#    Run application tests in all modules specified by command line
#
# Revision Dates
#     8-May-2017 (CT) Creation
#     5-Jun-2017 (CT) Fix Py-3 compatibility of `py_version`
#    23-Apr-2020 (CT) Use `importlib.import_module`, not `TFL.import_module`
#    ««revision-date»»···
#--

from   _TFL                       import TFL

from   _TFL                       import sos
from   _TFL.Filename              import Filename
from   _TFL.pyk                   import pyk
from   _TFL.Regexp                import Regexp, re
from   _TFL.subdirs               import subdirs

import _TFL.Caller
import _TFL.CAO
import _TFL.Context
import _TFL.Decorator
import _TFL.Package_Namespace
import _TFL.Record

from   timeit                     import default_timer as _timer
from   fnmatch                    import fnmatch

import doctest
import importlib
import logging
import sys
import subprocess
import fnmatch

TFL.Package_Namespace._check_clashes = False ### avoid spurious ImportErrors

_app_test_pat = Regexp (r"^ *__App_Tests__ *=", re.MULTILINE)

def has_app_test (fn) :
    with open (fn, "rb") as f :
        code = pyk.decoded (f.read ())
    return _app_test_pat.search (code)
# end def has_app_test

def import_module (path) :
    fn = Filename (path)
    mn = fn.base
    md = fn.directory or "./"
    with TFL.Context.list_push (sys.path, md, 0) :
        result = importlib.import_module (mn)
        result.__App_Tests_Dir__ = md
        return result
# end def import_module

def new_summary () :
    return TFL.Record \
        ( cases    = 0
        , excluded = []
        , failed   = 0
        , failures = []
        , modules  = 0
        , total    = 0
        )
# end def new_summary

@TFL.Attributed (map = {})
def py_version (pyx) :
    try :
        result = py_version.map [pyx]
    except KeyError :
        result = py_version.map [pyx] = subprocess.check_output \
            ( [pyx, "--version"], stderr = subprocess.STDOUT
            ).split (b" ") [-1].strip ()
    return pyk.decoded (result)
# end def py_version

def run_app_tests_dir \
        (d, exclude, py_executables, py_options, summary) :
    for f in sorted (sos.listdir_exts (d, ".py")) :
        run_app_tests_mod \
            (f, exclude, py_executables, py_options, summary)
# end def run_app_tests_dir

def run_app_tests_dir_transitive \
        (d, exclude, py_executables, py_options, summary) :
    run_app_tests_dir (d, exclude, py_executables, py_options, summary)
    for s in subdirs (d) :
        run_app_tests_dir_transitive \
            (s, exclude, py_executables, py_options, summary)
# end def run_app_tests_dir_transitive

def run_app_tests_mod \
        (path, exclude, py_executables, py_options, summary) :
    if exclude (path) :
        summary.excluded.append (path)
        print ("%s excluded" % (path, ))
    elif has_app_test (path) :
        try :
            mod = import_module (path)
        except Exception as exc :
            summary.failed += 1
            summary.total  += 1
            summary.failures.append ((path, "Exception %s" % (exc, )))
            print ("Import of %s raises exception `%r`" % (path, exc))
        else :
            app_tests = getattr (mod, "__App_Tests__", None)
            if not app_tests :
                return
            with sos.changed_dir (mod.__App_Tests_Dir__) :
                summary.modules += 1
                summary.cases   += len (app_tests)
                for pyx in py_executables :
                    failures = 0
                    pyv      = py_version (pyx)
                    for app_test in app_tests :
                        summary.total += 1
                        run  = app_test (pyx, py_options)
                        et   = " in %7.5fs" % (run.time)
                        if run :
                            tail            = ""
                            verb            = "passes"
                        else :
                            sep             = "\n  "
                            tps             = [""]
                            if run.error_diff :
                                tps.append ("Error  diff: %s" % run.error_diff)
                            if run.output_diff :
                                tps.append ("Output diff: %s" % run.output_diff)
                            tail            = sep.join (tps)
                            verb            = "fails "
                            summary.failed += 1
                            failures       += 1
                        print \
                            ( "%s [%s] %s application test%s [py %s]%s"
                            % (app_test.name, path, verb, et, pyv, tail)
                            , file = sys.stderr
                            )
                    if failures :
                        summary.failures.append ((path, failures))
# end def run_app_tests_mod

def _main (cao) :
    cao_path       = list (cao.path or [])
    summary        = new_summary ()
    py_executables = [sys.executable] + list (cao.Extra_Interpreters)
    py_options     = sos.python_options ()
    py_vs          = "[Python %s]" % ", ".join \
        (sorted (py_version (pyx) for pyx in py_executables))
    if cao.RExclude :
        x_pat      = Regexp (cao.RExclude)
        exclude    = x_pat.search
    elif cao.exclude :
        exclude    = lambda a : fnmatch (a, cao.exclude)
    else :
        exclude    = lambda a : False
    run_dir = run_app_tests_dir_transitive \
        if cao.transitive else run_app_tests_dir
    start = _timer ()
    for a in cao.argv :
        runner = run_dir if sos.path.isdir (a) else run_app_tests_mod
        runner (a, exclude, py_executables, py_options, summary)
    if cao.summary :
        et = " in %7.5fs" % (_timer () - start, )
        if summary.failed :
            fmt = "%(argv)s fails %(f)s of %(t)s app-tests in %(cases)s test-cases%(et)s %(py_vs)s"
        else :
            fmt = "%(argv)s passes all of %(t)s app-tests in %(cases)s test-cases%(et)s %(py_vs)s"
        print ("=" * 79, file = sys.stderr)
        print \
            ( fmt % TFL.Caller.Scope
                ( argv   = " ".join (cao.argv)
                , cases  = summary.cases
                , et     = et
                , f      = summary.failed
                , t      = summary.total
                )
            , file = sys.stderr
            )
        print \
            ( "    %s"
            % ("\n    ".join ("%-68s : %s" % f for f in summary.failures))
            , file = sys.stderr
            )
        if summary.excluded :
            print \
                ("    %s excluded" % (", ".join (summary.excluded), )
                , file = sys.stderr
                )
# end def _main

Command = TFL.CAO.Cmd \
    ( handler       = _main
    , args          =
        ( "module:P?Module(s) to test", )
    , opts          =
        ( "exclude:S?Glob pattern to exclude certain tests"
        , "Extra_Interpreters:P:?Extra python interpreters to run tests through"
        , "path:P:?Path to add to sys.path"
        , "RExclude:S?Regular expression to exclude certain tests"
        , "summary:B?Summary of failed tests"
        , "transitive:B"
            "?Include all subdirectories of directories specified "
              "as arguments"
        )
    , min_args      = 1
    , put_keywords  = True
    )
if __name__ != "__main__" :
    TFL._Export_Module ()
else :
    Command ()
### __END__ TFL.run_app_tests
