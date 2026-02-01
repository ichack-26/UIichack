# -*- coding: utf-8 -*-
# Copyright (C) 2016-2020 Christian Tanzer All rights reserved
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
#    TFL.ulid
#
# Purpose
#    Universally Unique Lexicographically Sortable Identifier
#
# Revision Dates
#     7-Dec-2016 (CT) Creation
#    ««revision-date»»···
#--

"""
This module provides functions computing universally unique
lexicographically sortable identifiers.

:obj:`ulid_48` and :obj:`ulid_48_secure` return an universally unique
lexicographically sortable identifier as defined by
https://github.com/alizain/ulid.

In security-relevant contexts, `ulid_48_secure`, not `ulid`, must be used.

* 128-bit compatibility with UUID
* 48-bit time stamp in milliseconds
* 1.21e+24 unique ULIDs per millisecond
* Lexicographically sortable
* Canonically encoded as a 26 character string
* Uses Crockford's base32 for better efficiency and readability
* Case insensitive
* No special characters (URL safe)

This module also implements variants :obj:`ulid_64` and :obj:`ulid_64_secure`
that use 64-bit time field with micro-second resolution.

* 128-bit compatibility with UUID
* 64-bit time stamp in microseconds
* 1.84e+19 unique ULID-64s per millisecond

Normally, `ulid_48` and `ulid_64` are called without any arguments. The
following test cases pass arguments to these functions to get reproducible
results::

    >>> ulid_48.t_factor
    1000
    >>> ulid_64.t_factor
    1000000

    >>> u48 = ulid_48 (1481114063593, 275638759670905959596219)
    >>> print (u48)
    01B3CME4Q979F6GDZ3YD8G7G5V

    >>> print (ulid_48.decoded_time (u48))
    1481114063593

    >>> print (ulid_48.decoded_random (u48))
    275638759670905959596219

    >>> u64 = ulid_64 (1481128151622732, 1139161307381642365)
    >>> print (u64)
    001A32G2NG92C0ZKRX5HP5MD3X

    >>> print (ulid_64.decoded_time (u64))
    1481128151622732

    >>> print (ulid_64.decoded_random (u64))
    1139161307381642365

"""

from   _TFL        import TFL
from   _TFL        import dc_base32

import _TFL._Meta.Object

import codecs
import os
import random
import time

class Ulid (TFL.Meta.Object) :
    """Generator of universally unique lexicographically sortable identifiers"""

    length = 26

    def __init__ (self, t_factor, t_length, r_bytes, get_random = None) :
        self.t_factor   = t_factor
        self.t_length   = t_length
        self.r_bytes    = r_bytes
        self.r_length   = self.length - t_length
        self.get_random = \
            self.get_random_nb if get_random is None else get_random
    # end def __init__

    def __call__ (self, t = None, r = None) :
        """Return an universally unique lexicographically sortable identifier.

           The arguments `t` and `r` should only be used for reproducible
           testing!
        """
        t = self.encoded_time   (t)
        r = self.encoded_random (r)
        return (t + r) [:self.length]
    # end def __call__

    def decoded_random (self, ulid) :
        """Extract random value from `ulid`."""
        return dc_base32.decoded (dc_base32.normalized (ulid) [self.t_length:])
    # end def decoded_random

    def decoded_time (self, ulid) :
        """Extract time in from `ulid`.

           The unit of the returned value is 1/self.t_factor seconds.
        """
        return dc_base32.decoded (dc_base32.normalized (ulid) [:self.t_length])
    # end def decoded_time

    def encoded (self, number, min_len) :
        result = dc_base32.encoded (number)
        l      = min_len - len (result)
        if l > 0 :
            result = ("0" * l) + result
        return result
    # end def encoded

    def encoded_random (self, r = None) :
        if r is None :
            r = self.get_random (self.r_bytes)
        return self.encoded (r, self.r_length)
    # end def encoded_random

    def encoded_time (self, t = None) :
        if t is None :
            t  = time.time () * self.t_factor
        return self.encoded (t, self.t_length)
    # end def encoded_t

    @staticmethod
    def get_random_nb (k) :
        """Return an integer with `k` random bytes. This is not secure."""
        return random.getrandbits (k * 8)
    # end def get_random_nb

    @staticmethod
    def get_random_cu (k) :
        """Return an integer with `k` random bytes based on `os.urandom`.

           In Python 3.6, calls to `os.urandom` can block if there isn't
           enough entropy available.
        """
        return int (codecs.encode (os.urandom (k), "hex"), 16)
    # end def get_random_cu

# end class Ulid

ulid_48  = Ulid (t_factor =    1000, t_length = 10, r_bytes  = 10)
ulid_64  = Ulid (t_factor = 1000000, t_length = 13, r_bytes  =  8)

ulid_48_secure   = Ulid \
    ( t_factor   = 1000
    , t_length   = 10
    , r_bytes    = 10
    , get_random = Ulid.get_random_cu
    )

ulid_64_secure   = Ulid \
    ( t_factor   = 1000000
    , t_length   = 13
    , r_bytes    = 8
    , get_random = Ulid.get_random_cu
    )

if __name__ != "__main__" :
    TFL._Export ("ulid_48", "ulid_64", "ulid_48_secure", "ulid_64_secure")
### __END__ TFL.ulid
