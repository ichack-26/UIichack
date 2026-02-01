# -*- coding: utf-8 -*-
# Copyright (C) 2008-2014 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Output
#
# Purpose
#    Classes for output redirection and stacking
#
# Revision Dates
#    27-Aug-2008 (CT) Creation
#    28-Aug-2008 (CT) `Tee` added
#    ««revision-date»»···
#--

from   _TFL                     import TFL
from   _TFL.pyk                 import pyk

import _TFL._Meta.Object

import sys

class Redirect_Std (TFL.Meta.Object) :
    """Redirection of sys.stdout and/or sys.stderr"""

    std_streams = set (("stdout", "stderr"))
    target      = None

    def __init__ (self, target, redirects = ("stdout", )) :
        assert all ((r in self.std_streams) for r in redirects), redirects
        self.target    = target
        self.redirects = map = {}
        for r in redirects :
            map [r] = getattr (sys, r)
            setattr (sys, r, self)
    # end def __init__

    def destroy (self) :
        for r, orig in pyk.iteritems (self.redirects) :
            if getattr (sys, r, None) is self :
                setattr (sys, r, orig)
        self.redirects = {}
        try :
            t_destroy = self.target.destroy
        except AttributeError :
            pass
        else :
            t_destroy ()
        self.target = None
    # end def destroy

    def flush (self) :
        try :
            f = self.target.flush
        except AttributeError :
            pass
        else :
            f ()
    # end def flush

    def write (self, text) :
        if self.target is not None :
            self.target.write (text)
    # end def write

# end class Redirect_Std

class Tee (TFL.Meta.Object) :
    """Write output to several streams."""

    def __init__ (self, * streams) :
        self.streams = list (streams)
    # end def __init__

    def add_stream (self, s) :
        streams = self.streams
        if s not in streams :
            streams.append (s)
    # end def add_stream

    def destroy (self) :
        streams = self.streams
        for s in streams :
            try :
                s_destroy = s.destroy
            except AttributeError :
                pass
            else :
                s_destroy ()
        self.streams = []
    # end def destroy

    def flush (self) :
        for s in self.streams :
            try :
                f = s.flush
            except AttributeError :
                pass
            else :
                f ()
    # end def flush

    def remove_stream (self, s) :
        streams = self.streams
        if s in streams :
            streams.remove (s)
    # end def remove_stream

    def write (self, text) :
        for s in self.streams :
            s.write (text)
    # end def write

    def writelines (self, seq) :
        for s in self.streams :
            s.writelines (seq)
    # end def writelines

# end class Tee

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.Output
