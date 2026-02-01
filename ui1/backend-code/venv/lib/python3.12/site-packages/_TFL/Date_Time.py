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
#    TFL.Date_Time
#
# Purpose
#    Provide classes and functions for handling dates and times
#
#    This is just a quick hack around time.py which grew out of frustration
#    that Python 1.5.* doesn't support `time.strptime` under Win32
#
#    To be really useful it would not lots of work...
#
# Revision Dates
#     5-Oct-1999 (CT) Creation
#     6-Oct-1999 (CT) Allow dates without year-field in `day_to_time_tuple`
#     6-Oct-1999 (CT) Conversion of alphabetic months moved into `Time_Tuple`
#                     (from `day_to_time_tuple`)
#    18-Nov-1999 (CT) Main-script added
#    03-Jan-2000 (CT) `day_per_month` added
#    03-Jan-2000 (CT) `_dd_month_pat` changed (last `.` optional)
#    11-Jan-2000 (CT) Optional `.` moved from `_dd_month_pat` to
#                     `_day_patterns`
#    16-Jan-2000 (CT) Class `Date` added
#    16-Jan-2000 (CT) `Time_Tuple.rindex` added
#    16-Jan-2000 (CT) `Time_Tuple.__init__` and `Time_Tuple._sanitized_month`
#                     corrected
#    14-Jan-2001 (CT) `__getattr__` added to `Date`
#    29-Jul-2001 (CT) Reverse mapping added to `months`
#    17-Sep-2001 (CT) `_time_pat` added
#    27-Dec-2001 (CT) `Time_Tuple.__init__` changed to ignore `None` values
#                     in `kw`
#    12-Feb-2002 (CT) `_sanitized_year` added
#    12-Feb-2002 (CT) Changed `Time_Tuple.__init__` to use `_sanitized`
#                     instead of  `_sanitized_field` for positional arguments
#     1-Jan-2003 (CT) `week` added to `Time_Tuple` and removed from `Date`
#     5-Apr-2003 (CT) Pattern for `yyyy/mm/dd` added to `_day_patterns`
#     5-Apr-2003 (CT) `Date.__init__` changed to allow `Date` instances as
#                     argument, too
#    13-Apr-2003 (CT) `_week` corrected for years starting on mondays
#    11-Jun-2003 (CT) s/!= None/is not None/
#     6-Feb-2004 (CT) `tuple` computed by `__getattr__`
#    13-Apr-2004 (CT) `YYYYMMDD_pat` added to `_day_patterns`
#    28-Sep-2004 (CT) Use `isinstance` instead of type comparison
#     7-Apr-2005 (CT) Use `isinstance` instead of type comparison (last
#                     instance)
#    18-Oct-2005 (CT) `YYYY_MM_DD_pat` changed to allow `-` as separator
#    18-Oct-2005 (CT) `_time_pat` changed to support `dst`
#    11-Feb-2006 (CT) Moved into package `TFL`
#     9-Aug-2006 (CT) `__hash__` changed to return `hash (self.value)` instead
#                     of `id (self)`
#     4-Jan-2008 (CT) `_sanitized_year` changed to add `2000` for `values < 40`
#    24-Sep-2009 (CT) Use `in` operator instead of `has_key` method
#     6-Dec-2009 (CT) 3-compatibility
#     7-Jun-2012 (CT) Use `TFL.r_eval`
#    16-Jun-2013 (CT) Use `TFL.CAO`, not `TFL.Command_Line`
#    16-Jun-2013 (CT) Improve 3-compatibility
#     3-Jan-2014 (CT) Check `pyk.string_types`, not `str`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

### Note: this module is obsolete and shouldn't be used for new code

from   _TFL                       import TFL
from   _TFL.pyk                   import pyk
from   _TFL.Regexp                import *
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL.CAO
import _TFL.r_eval

from   time                       import *

class Time_Tuple :
    """Encapsulate a time tuple as used by time.gmtime, time.mktime, and
       other functions provided by time.

       You can access the values of the time tuple by index or by name.
    """

    index  = { "year"            : 0
             , "month"           : 1
             , "day"             : 2
             , "hour"            : 3
             , "minute"          : 4
             , "second"          : 5
             , "weekday"         : 6
             , "jd"              : 7
             , "julian_day"      : 7
             , "dst"             : 8
             , "daylight_saving" : 8
             }
    rindex = { 0                 : "year"
             , 1                 : "month"
             , 2                 : "day"
             , 3                 : "hour"
             , 4                 : "minute"
             , 5                 : "second"
             , 6                 : "weekday"
             , 7                 : "julian_day"
             , 8                 : "daylight_saving"
             }

    months = { 'jan' :  1, 'january'   :   1,  1 : "jan"
             , 'feb' :  2, 'february'  :   2,  2 : "feb"
             , 'mar' :  3, 'march'     :   3,  3 : "mar"
             , 'apr' :  4, 'april'     :   4,  4 : "apr"
             , 'may' :  5, 'may'       :   5,  5 : "may"
             , 'jun' :  6, 'june'      :   6,  6 : "jun"
             , 'jul' :  7, 'july'      :   7,  7 : "jul"
             , 'aug' :  8, 'august'    :   8,  8 : "aug"
             , 'sep' :  9, 'september' :   9,  9 : "sep"
             , 'oct' : 10, 'october'   :  10, 10 : "oct"
             , 'nov' : 11, 'november'  :  11, 11 : "nov"
             , 'dec' : 12, 'december'  :  12, 12 : "dec"
             }

    day_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    def __init__ (self, * args, ** kw) :
        """Create a time tuple from `args` and `kw`.

           If used, `args` must contain time some or all tuple elements in
           the canonical sequence

               (year, month, day, hour, minute, second, weekday, jd, dst)

           If used, `kw` can provide any of these elements by name.

           Any elements specified neither by `args` nor `kw` are taken from

               `localtime (time())`

           The arguments can be strings or integers. String arguments must
           evaluate to integers or be a valid month name (see the
           Time_Tuple.months dictionary).
        """
        body = list (localtime (time ()))
        for i in range (len (args)) :
            body [i] = self._sanitized (self.rindex [i], args [i])
        for k in kw.keys () :
            if kw [k] is not None :
                if k not in self.index :
                    raise NameError (k)
                body [self.index [k]] = self._sanitized (k, kw [k])
        self.body = tuple (body)
    # end def __init__

    def _sanitized (self, field, value) :
        sanitizer = self._sanitizers.get (field, Time_Tuple._sanitized_field)
        return sanitizer (self, value)
    # end def _sanitized

    def _sanitized_field (self, value) :
        if isinstance (value, str) :
            if value [0] == "0" :
                value = value [1:]
            value = TFL.r_eval (value)
        return int (value)
    # end def _sanitized_field

    def _sanitized_month (self, value) :
        if isinstance (value, str) :
            v = value.lower ()
            if v in self.months :
                return self.months [v]
            else :
                return self._sanitized_field (value)
        else :
            return int (value)
    # end def _sanitized_month

    def _sanitized_year (self, value) :
        result = self._sanitized_field (value)
        if result < 40 :
            result += 2000
        if result < 100 :
            result += 1900
        return result
    # end def _sanitized_year

    _sanitizers = { "month" : _sanitized_month, "year" : _sanitized_year}

    def __getattr__ (self, name) :
        if name in self.index :
            return self.body [self.index [name]]
        if name == "week" :
            result = self.week = self._week ()
            return result
        raise AttributeError (name)
    # end def __getattr__

    def __str__      (self)       : return str  (self.body)
    def __repr__     (self)       : return repr (self.body)
    def __len__      (self)       : return len  (self.body)
    def __getitem__  (self, item) : return self.body [item]
    def __getslice__ (self, i, j) : return self.body [i:j]

    def _week (self) :
        """Returns the week number of `self` as a decimal number between 0
           and 53.
        """
        ny_time  = mktime (self.body) - ((self.julian_day - 1) * 86400)
        new_year = Time_Tuple (* localtime (ny_time))
        return int (strftime ("%W", self.body)) + (0 < new_year.weekday < 4)
    # end def _week

# end class Time_Tuple

_dd_month_pat = ( r"(?P<day> \d{1,2})"
                  r"([-.\s])"
                  r"(?P<month> (?:\d{1,2}) | (?:[a-z]{3,9}))"
                )
_month_dd_pat = ( r"(?P<month> [a-z]{3,9})"
                  r"\s"
                  r"(?P<day> \d{1,2})"
                )
_time_pat     = ( r"(?: \s+ "
                      r"(?P<hour> \d{1,2})"
                      r"(?: : (?P<minute> \d{1,2}) "
                          r"(?: : (?P<second> \d{1,2}))?"
                      r")?"
                      r"(?P<dst> [ ] [-+]\d{4,4})?"
                  r")?"
                )

YYYY_MM_DD_pat = Regexp \
    ( r"(?P<year>  \d{4,4})"
    + r"([-/])"
    + r"(?P<month> \d{2,2})"
    + r"\2"
    + r"(?P<day>   \d{2,2})"
    + _time_pat
    + r"$"
    , re.X
    )
YYYYMMDD_pat = Regexp \
    ( r"(?P<year>  \d{4,4})"
    + r"(?P<month> \d{2,2})"
    + r"(?P<day>   \d{2,2})"
    + _time_pat
    + r"$"
    , re.X
    )

_day_patterns  = \
    ( Regexp
       ( _dd_month_pat
       + r"[.]?"
       + _time_pat
       + r"$"
       , re.X | re.I
       )
    , Regexp
       ( _dd_month_pat
       + r"\2"
       + r"(?P<year> \d{4,4})"
       + _time_pat
       + r"$"
       , re.X | re.I
       )
    , Regexp
       ( _month_dd_pat
       + r"$"
       , re.X | re.I
       )
    , Regexp
       ( _month_dd_pat
       + r",\s*"
       + r"(?P<year>  \d{4,4})?"
       + r"$"
       , re.X | re.I
       )
    , Regexp
       ( _dd_month_pat
       + r"\2"
       + r"(?P<year> \d{2,2})"
       + _time_pat
       + r"$"
       , re.X | re.I
       )
    , YYYY_MM_DD_pat
    , YYYYMMDD_pat
    )

def day_to_time_tuple (day_string) :
    """Convert `day_string` containing a date to `Time_Tuple`"""
    for pat in _day_patterns :
        match = pat.match (day_string)
        if match :
            return Time_Tuple (** match.groupdict ())
    raise ValueError (day_string)
# end def time_tuple

@totally_ordered
class Date :
    """Model a date."""

    def __init__ (self, date = None) :
        d = time ()
        if date is None :
            date = d
        else :
            if isinstance (date, pyk.string_types) :
                date  = day_to_time_tuple (date)
            if isinstance (date, Time_Tuple) :
                date  = mktime (date.body)
            elif isinstance (date, tuple) :
                date  = mktime (date)
            elif isinstance (date, Date) :
                date  = mktime (date.local_tuple ())
            elif not isinstance (date, d.__class__) :
                raise ValueError (date)
        self.value = date
    # end def __init__

    def dec (self, n = 1) :
        """Decrement `self` by `n` days."""
        self.value = self.value - n * 86400
        if hasattr (self, "tuple") :
            del self.tuple
    # end def inc

    def formatted (self, format = "%d-%m-%Y") :
        return strftime (format, localtime (self.value))
    # end def formatted

    def inc (self, n = 1) :
        """Increment `self` by `n` days."""
        self.value = self.value + n * 86400
        if hasattr (self, "tuple") :
            del self.tuple
    # end def inc

    def local_tuple (self) :
        """Return `self` as `Time_Tuple` (local time)"""
        return Time_Tuple (* localtime (self.value))
    # end def local_tuple

    def gm_tuple (self) :
        """Return `self` as `Time_Tuple` (Greenwich time)"""
        return Time_Tuple (* gmtime (self.value))
    # end def gm_tuple

    def __add__ (self, n) :
        """Return value of `self` incremented by `n` days."""
        return self.__class__ (self.value + n * 86400)
    # end def __add__

    def __eq__ (self, other) :
        return self.value == getattr (other, "value", other)
    # end def __eq__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if name == "tuple" :
            result = self.tuple = self.local_tuple ()
            return result
        return getattr (self.tuple, name)
    # end def __getattr__

    def __hash__ (self) :
        return hash (self.value)
    # end def __hash__

    def __lt__ (self, other) :
        return self.value < getattr (other, "value", other)
    # end def __lt__

    def __str__ (self) :
        return self.formatted ()
    # end def formatted

    def __sub__ (self, n) :
        """Return value `self` decremented by `n` days."""
        return self.__class__ (self.value - n * 86400)
    # end def __sub__

# end class Date

def _main (cmd) :
    format = cmd.format
    delta  = cmd.delta * 86400
    now    = localtime (time () + delta)
    print (strftime (format, now))
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler       = _main
    , args          =
        ( "format:S=%Y%m%d?Format for date"
        ,
        )
    , opts          =
        ( "-delta:I=0?delta to current date in days"
        ,
        )
    , max_args      = 1
    )

if __name__ != "__main__":
    TFL._Export ("*")
else :
    _Command ()
### __END__ TFL.Date_Time
