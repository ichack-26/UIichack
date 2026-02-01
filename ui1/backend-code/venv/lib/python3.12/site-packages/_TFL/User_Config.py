# -*- coding: utf-8 -*-
# Copyright (C) 2011-2023 Christian Tanzer All rights reserved
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
#    TFL.User_Config
#
# Purpose
#    Provide thread-local user configuration
#
# Revision Dates
#    19-Jul-2011 (CT) Creation
#    20-Jul-2011 (CT) `get_tz` and `set_defaults` added
#    30-Apr-2012 (CT) Convert `tz` to lazy `Once_Property`, allow
#                     `ImportError` by `dateutil`
#    21-Jun-2012 (CT) Handle `time_zone` properly in `set_default`
#    21-Jun-2012 (CT) Autoconvert `time_zone` values passed as string
#    21-Jun-2012 (CT) Fix typo
#    12-Oct-2014 (CT) Add `sha`
#    10-Oct-2016 (CT) Remove unnecessary import of `MOM`
#    18-Oct-2023 (CT) Change default `time_zone` to `get_tz ()`, if any
#                     * Better than former default of "UTC"
#                     * Set `time_zone` to "UTC", if `None` is passed
#    ««revision-date»»···
#--

from   _TFL                     import TFL

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.pyk                 import pyk

import _TFL._Meta.Property
import _TFL.Context

import locale
import sys
import threading

class User_Config (threading.local) :
    """Provide thread-local user configuration."""

    _initialized         = False

    file_system_encoding = sys.getfilesystemencoding ()
    input_encoding       = locale.getpreferredencoding ()
    language             = "en"
    output_encoding      = input_encoding
    _sha                 = "sha224"
    user                 = None

    _time_zone           = None

    def __init__ (self, ** kw) :
        if self._initialized :
            raise SystemError \
                ( "TFL.User_Config must not be called more than "
                  "once per thread"
                )
        self._initialized = True
        self.__dict__.update (kw)
    # end def __init__

    @property
    def sha (self) :
        import _TFL.Secure_Hash
        result = self._sha
        if result is None :
            result = self._sha = TFL.Secure_Hash.sha224
        elif isinstance (result, str) :
            result = self._sha = getattr (TFL.Secure_Hash, result)
        return result
    # end def sha

    @sha.setter
    def sha (self, value) :
        self._sha = value
    # end def sha

    @property
    def time_zone (self) :
        if self.tz is not None :
            if self._time_zone is None :
                ltz = self.get_tz ()
                self._time_zone = self.tz.tzutc () if ltz is None else ltz
            elif isinstance (self._time_zone, pyk.string_types) :
                self._time_zone = self.get_tz (self._time_zone)
        return self._time_zone
    # end def time_zone

    @time_zone.setter
    def time_zone (self, value) :
        if value is None :
            value = "UTC"
        if isinstance (value, pyk.string_types) :
            value = self.get_tz (value)
        self._time_zone = value
    # end def time_zone

    @Once_Property
    def tz (self) :
        try :
            from dateutil import tz
            return tz
        except ImportError :
            pass
    # end def tz

    def get_tz (self, name = None) :
        """Return tz-info for `name` (default taken from environment).

           For instance::

               tz.gettz ("Europe/Vienna") -->
                   tzfile ('/usr/share/zoneinfo/Europe/Vienna')

        """
        if self.tz is not None :
            return self.tz.gettz (name)
    # end def get_tz

    LET = TFL.Meta.Class_and_Instance_Method (TFL.Context.attr_let)

    def set_default (self, name, value) :
        """Set default of attribute `name` to `value`."""
        if name == "_initialized" :
            raise AttributeError ("Cannot set default for _initialized")
        if name == "time_zone" :
            name = "_time_zone"
            if isinstance (value, pyk.string_types) :
                value = self.get_tz (value)
        setattr (self.__class__, name, value)
        return value
    # end def set_default

    def set_defaults (self, ** kw) :
        for k, v in pyk.iteritems (kw) :
            self.set_default (k, v)
    # end def set_defaults

# end class User_Config

user_config = User_Config ()

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.User_Config
