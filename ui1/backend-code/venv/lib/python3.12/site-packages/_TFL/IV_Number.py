# -*- coding: utf-8 -*-
# Copyright (C) 1999-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.IV_Number
#
# Purpose
#    Model Interface-Version Number
#
# Revision Dates
#    25-Oct-1999 (CT) Creation
#     2-Nov-1999 (CT) Comment added
#    15-Nov-1999 (CT) `db_extension` added
#    18-Nov-1999 (CT) `producer` added
#    19-Nov-1999 (CT) `producer` convert to list
#    19-Nov-1999 (CT) `consumer` added
#     8-Aug-2000 (MG) Format of `__repr__` changed
#     9-Aug-2000 (CT) `clone` added
#     9-Aug-2000 (MG) `_unnested` added and used in `__repr__`
#    28-Sep-2000 (CT) s/database/data base/g
#    13-Dec-2000 (CT) s/data base/database/g
#    12-Apr-2002 (CT) Use `StandardError` instead of `Exception`
#    15-Apr-2002 (CT) Raise `TypeError` instead of string exception
#                     (__setattr__)
#    24-Oct-2002 (CT) Esthetics
#    28-Sep-2004 (CT) Use `isinstance` instead of type comparison
#    14-Feb-2006 (CT) Moved into package `TFL`
#     9-Aug-2006 (CT) `__hash__` changed to return `hash (id (self))`
#                     instead of `id (self)`
#    ««revision-date»»···
#--

from   _TFL                  import TFL
from   _TFL.pyk              import pyk

class Interface_Mismatch (Exception) :
    pass

class IV_Number :
    """Model Interface-Version Number.

       An `IV_Number` describes the version of a specific interface of a
       software product (e.g., a database read or written).

       `external_version` is set to the version of the interface when the
       program reads information from that interface. The value of
       `external_version` can be used to convert from an old to a new format.

           `external_version` applies only to two-way interfaces which are
           read and written by the same program.

       `external_version` must lie in the interval (`comp_min`, `comp_max`).
       If it is set to a value not in that interval, an exception is raised.
       The function `compatible` can be used to check the `external_version`
       before setting it.
    """

    def __init__ \
        ( self, name, producer, consumer, program_version
        , comp_min     = None
        , comp_max     = None
        , db_extension = None
        ) :
        if isinstance (producer, pyk.string_types) :
            producer = (producer, )
        if isinstance (consumer, pyk.string_types) :
            consumer = (consumer, )
        self.name              = name
        self.producer          = producer
        self.consumer          = consumer
        self.program_version   = program_version
        self.comp_min          = (comp_min, program_version) [comp_min is None]
        self.comp_max          = (comp_max, program_version) [comp_max is None]
        self.db_extension      = db_extension
        self.reset_external_version ()
    # end def __init__

    def clone (self, comp_min) :
        """Returns a clone of `self` with changed `comp_min`."""
        return self.__class__   \
            ( self.name
            , self.producer
            , self.consumer
            , self.program_version
            , comp_min
            , self.comp_max
            , self.db_extension
            )
    # end def clone

    def compatible (self, external_version) :
        return self.comp_min <= external_version <= self.comp_max
    # end def compatible

    def restrict (self, comp_min, comp_max) :
        """Restrict compatibility interval to `comp_min` and `comp_max`."""
        self.__dict__ ["comp_min"] = max (self.comp_min, comp_min)
        self.__dict__ ["comp_max"] = min (self.comp_max, comp_max)
    # end def restrict

    def reset_external_version (self) :
        """Reset `self.external_version`."""
        self.__dict__ ["external_version"] = -1
    # end def reset_external_version

    def __setattr__ (self, name, value) :
        """Prevent the changing of attributes other than `external_version`.

           `external_version` is checked for compatibility with `comp_min`
           and `comp_max`.

           Once an attribute is set, it cannot be changed to another value.
        """
        if hasattr (self, name) and name != "external_version" :
            raise TypeError \
                ( "Attribute %s is readonly. Cannot change value from %s to %s"
                % (name, getattr (self, name), value)
                )
        self.__dict__ [name] = value
        if name == "external_version" :
            if not self.compatible (value) :
                raise Interface_Mismatch (self)
    # end def __setattr__

    def __str__ (self) :
        return "%s = %s" % (self.name, self.program_version)
    # end def __str__

    def _unnested (self, l) :
        if len (l) == 1 :
            return l [0]
        else :
            return l
    # end def _unnested

    def __repr__ (self) :
        return "%s ('%s', %s, %s, %s, %s, %s, '%s')" % \
            ( self.__class__.__name__, self.name
            , repr (self._unnested (self.producer))
            , repr (self._unnested (self.consumer))
            , self.program_version, self.comp_min, self.comp_max
            , self.db_extension or ""
            )
    # end def __repr__

# end class IV_Number

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.IV_Number
