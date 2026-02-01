# -*- coding: utf-8 -*-
# Copyright (C) 2010 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.relative_to_search_path
#
# Purpose
#    Convert an absolute path to a path relative to one of the elements of a
#    search path, if possible
#
# Revision Dates
#    25-Jan-2010 (CT) Creation
#    16-Jun-2010 (CT) s/print/pyk.fprint/
#    ««revision-date»»···
#--

from   _TFL import TFL
from   _TFL.pyk import pyk
from   _TFL import sos

import _TFL._Meta.Object
import _TFL.CAO

import sys

class Relative_To_Search_Path (TFL.Meta.Object) :
    """Return `abs_path` as path relative to one of the elements in
       `search_path`, if possible.
    """

    if sos.path.altsep :
        seps = (sos.path.sep, sos.path.altsep)
    else :
        seps = (sos.path.sep, )

    def __init__ (self, search_path) :
        self.search_path = list \
            (p for p in (self._normalized (p) for p in search_path) if p)
    # end def __init__

    def __call__ (self, abs_path) :
        p = self._normalized (abs_path)
        if sos.path.isabs (abs_path) :
            for sp in self.search_path :
                if p.startswith (sp) :
                    result = p [len (sp):]
                    for s in self.seps :
                        result = result.lstrip (s)
                    return result
        return abs_path
    # end def __call__

    def _normalized (self, p) :
        path = sos.path
        return path.realpath (path.normpath (path.normcase (p)))
    # end def _normalized

# end class Relative_To_Search_Path

def relative_to_search_path (search_path, abs_path) :
    """Return `abs_path` as path relative to one of the elements in
       `search_path`, if possible.
    """
    return Relative_To_Search_Path (search_path) (abs_path)
# end def relative_to_search_path

relative_to_python_path = Relative_To_Search_Path \
    (sos.environ.get ("PYTHONPATH").split (sos.path.pathsep) or sys.path)

def _main (cmd) :
    rtsp = Relative_To_Search_Path (cmd.search_path)
    print (* (rtsp (p) for p in cmd.argv), sep = cmd.Sep)
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler     = _main
    , args        =
        ( "path:P?Path(es) to convert to relative to `search_path`"
        ,
        )
    , opts        =
        ( "-search_path:P:?Search path"
        , "-Sep:S=\n?Separator between pathes printed to stdout"
        )
    , description =
        "Convert absolute pathes to pathes relative to one of the "
        "elements of a search path, if possible"
    )

if __name__ != "__main__" :
    TFL._Export ("*")
else :
    _Command ()
### __END__ TFL.relative_to_search_path
