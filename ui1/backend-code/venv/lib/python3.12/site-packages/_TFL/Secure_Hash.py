# -*- coding: utf-8 -*-
# Copyright (C) 2014-2020 Christian Tanzer All rights reserved
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
#    TFL.Secure_Hash
#
# Purpose
#    Portable interface to secure hash algorithms as supplied by `hashlib`
#
# Revision Dates
#    11-Oct-2014 (CT) Creation
#    12-Oct-2014 (CT) Continue creation
#    14-Oct-2015 (CT) Change `b64digest` to return `pyk.text_type`
#    27-Feb-2017 (CT) Make doctest Python 3.6 compatible
#                     * Remove enumeration of `.algorithms`
#    19-Aug-2019 (CT) Use `print_prepr`
#    ««revision-date»»···
#--

from   _TFL                import TFL

from   _TFL.portable_repr  import portable_repr, print_prepr
from   _TFL.pyk            import pyk

import _TFL._Meta.Object
import _TFL._Meta.Once_Property

import base64
import hashlib
import hmac

class _M_Secure_Hash_ (TFL.Meta.Object.__class__) :
    """Meta class for `Secure_Hash`"""

    Base   = None
    name   = None
    unsafe = set (["md4", "md5"])

    @TFL.Meta.Once_Property
    def algorithms (cls) :
        try :
            result = hashlib.algorithms_guaranteed
        except AttributeError :
            result = hashlib.algorithms
        return set (r for r in result if r.lower () not in cls.unsafe)
    # end def algorithms

    def __getattr__ (cls, name) :
        if name in cls.algorithms :
            Base = cls.Base
            if Base is not None :
                ### don't derive a new algorithm from another concrete algorithm
                return getattr (Base, name)
            else :
                sha    = getattr (hashlib, name)
                result = cls.__class__ \
                    ( name, (cls._Mixin_, cls)
                    , dict
                        ( Base       = cls
                        , name       = name
                        , _hash_fct  = sha
                        , __module__ = cls.__module__
                        )
                    )
                setattr (result.Base, name, result)
                return result
        raise AttributeError (name)
    # end def __getattr__

    def __repr__ (cls) :
        if cls.Base is not None :
            return pyk.reprify ("<%s %s>" % (cls.Base.__name__, cls.name))
        else :
            return cls.__m_super.__repr__ ()
    # end def __repr__

# end class _M_Secure_Hash_

class _Wrapper_ (TFL.Meta.Object) :
    """Wrapper around a `hashlib` or `hmac` algorithm"""

    _hash_fct = None

    class _Wrapper_Mixin_ (TFL.Meta.Object) :
        """_Mixin_ defines methods that are only callable for concrete hash
           algorithms. `_M_Secure_Hash_.__getattr__` creates classes
           for concrete hash algorithms derived from `_Mixin_`.
        """

        @classmethod
        def compare_b64digest (cls, lhs, rhs) :
            """Return 'lhs == rhs' in constant time"""
            std_len = len (cls._encoded (cls._hash_fct ().b64digest ()))
            return cls.compare (lhs, rhs, std_len)
        # end def compare

        @classmethod
        def compare_digest (cls, lhs, rhs) :
            """Return 'lhs == rhs' in constant time"""
            std_len = len (cls._encoded (cls._hash_fct ().digest ()))
            return cls.compare (lhs, rhs, std_len)
        # end def compare

        @classmethod
        def compare_hexdigest (cls, lhs, rhs) :
            """Return 'lhs == rhs' in constant time"""
            std_len = len (cls._hash_fct ().hexdigest ())
            return cls.compare (lhs, rhs, std_len)
        # end def compare_hexdigest

        def __repr__ (self) :
            return pyk.reprify \
                ("<%s object %s>" % (self.Base.__name__, self.name))
        # end def __repr__

    # end class _Wrapper_Mixin_

    def __init__ (self, * args, ** kw) :
        cls      = self.__class__
        cls_name = cls.__name__
        names    = sorted (cls.algorithms)
        raise TypeError \
            ( "Please use one of: %s"
            % ", ".join (".".join ((cls_name, name)) for name in names)
            )
    # end def __init__

    @TFL.Meta.Once_Property
    def block_size (self) :
        """The internal block size of the hash algorithm in bytes."""
        return self._hasher.block_size
    # end def block_size

    @TFL.Meta.Once_Property
    def digest_size (self) :
        """The length of the `digest`."""
        return self._hasher.digest_size
    # end def digest_size

    @TFL.Meta.Once_Property
    def hexdigest_size (self) :
        """The length of the `hexdigest`."""
        return self.digest_size * 2
    # end def hexdigest_size

    def b64digest (self, altchars = "_-", strip = False) :
        if isinstance (altchars, str) :
            altchars = pyk.encoded (altchars)
        result = base64.b64encode (self.digest (), altchars)
        if strip :
            result = result.rstrip (b"=")
        return str (result, "ASCII")
    # end def b64digest

    @classmethod
    def compare (cls, lhs, rhs, std_len) :
        """Return 'lhs == rhs' in constant time"""
        l       = cls._encoded (lhs)
        r       = cls._encoded (rhs)
        len_l   = len (l)
        len_r   = len (r)
        if len_l != len_r :
            ### Choose argument with non-standard length for comparison
            s    = l if len_l != std_len else r
            l, r = (s, s)
        result  = cls._fixed_time_compare (l, r)
        return result if len_l == len_r else False
    # end def compare

    def copy (self) :
        result         = self.__new__      ()
        result._hasher = self._hasher.copy ()
        return result
    # end def copy

    def digest (self) :
        """Return the digest value as a string of binary data."""
        return self._hasher.digest ()
    # end def digest

    def hexdigest (self) :
        """Return the digest value as a string of hexadecimal digits."""
        return self._hasher.hexdigest ()
    # end def hexdigest

    def update (self, obj) :
        """Update this hash object's state with the provided obj."""
        value = self._encoded (obj)
        self._hasher.update (value)
    # end def update

    @classmethod
    def _encoded (cls, obj) :
        return pyk.encoded (portable_repr (obj).strip (""""'"""), "utf-8")
    # end def _encoded

    try :
        _fixed_time_compare = staticmethod (hmac.compare_digest)
    except AttributeError :
        ### `hmac.compare_digest` is new in Python 3.3
        ### for older versions, use a home-grown method
        @classmethod
        def _fixed_time_compare (cls, lhs, rhs) :
            s = 0
            for l, r in zip (lhs, rhs) :
                s |= ord (l) ^ ord (r)
            return s == 0
        # end def _fixed_time_compare

# end class _Wrapper_

class HMAC (_Wrapper_, metaclass = _M_Secure_Hash_) :
    """Wrapper around an HMAC algorithm with portable interface."""

    class _Mixin_ (_Wrapper_._Wrapper_Mixin_) :
        """_Mixin_ defines methods that are only callable for concrete hash
           algorithms. `_M_Secure_Hash_.__getattr__` creates classes
           for concrete hash algorithms derived from `_Mixin_`.
        """

        def __init__ (self, key, msg = None) :
            k            = self._encoded (key)
            m            = self._encoded (msg)
            self._hasher = hmac.new (k, m, self._hash_fct)
        # end def __init__

    # end class _Mixin_

# end class HMAC

class Secure_Hash (_Wrapper_, metaclass = _M_Secure_Hash_) :
    """Wrapper around a secure hash algorithm with portable interface."""

    _rounds_map      = dict \
        ( sha1       = 10000
        , sha224     =  2300
        , sha256     =  2000
        , sha384     =  1300
        , sha512     =  1000
        )

    class _Mixin_ (_Wrapper_._Wrapper_Mixin_) :
        """_Mixin_ defines methods that are only callable for concrete hash
           algorithms. `_M_Secure_Hash_.__getattr__` creates classes
           for concrete hash algorithms derived from `_Mixin_`.
        """

        def __init__ (self, init = None) :
            self._hasher = self._hash_fct ()
            if init is not None :
                self.update (init)
        # end def __init__

        @classmethod
        def hmac (cls, key, msg = None) :
            """Create a new HMAC object and return it."""
            T = getattr (HMAC, cls.name)
            return T (key, msg)
        # end def hmac

        @classmethod
        def pbkdf2_hmac (cls, password, salt, rounds = None, dklen = None) :
            """pbkdf2_hmac (password, salt, rounds = None, dklen = None) -> key

               Password based key derivation function 2 (PKCS #5 v2.0) with HMAC
               as pseudorandom function.
            """
            n = cls.name
            p = cls._encoded (password)
            s = cls._encoded (salt)
            r = cls._rounds_map.get (n, 1000) if rounds is None else rounds
            return hashlib.pbkdf2_hmac (n, p, s, r, dklen)
        # end def pbkdf2_hmac

    # end class _Mixin_

# end class Secure_Hash

__doc__ = r"""
In Python 3, the secure hash algorithms provided by `hashlib` require their
argument to be a instance of `bytes`, whereas in Python 2 the argument can be
a string.

`Secure_Hash` provides a wrapper around the hashlib algorithms that takes
care of this difference. You can also feed arbitrary Python objects to
`update`; `update` applies `portable_repr` to its argument.

    >>> import sys

    >>> Secure_Hash.sha1
    <Secure_Hash sha1>

    >>> Secure_Hash.sha224
    <Secure_Hash sha224>

    >>> Secure_Hash.sha224.sha384
    <Secure_Hash sha384>

    >>> Secure_Hash.sha512
    <Secure_Hash sha512>

    >>> try :
    ...     Secure_Hash ()
    ... except TypeError as exc :
    ...     print (exc) # doctest:+ELLIPSIS
    Please use one of: ...

    >>> sh_1 = Secure_Hash.sha1 ("foo")
    >>> sh_1.update ("bar")
    >>> sh_1.update ((1, 2, 3, 4))
    >>> print_prepr (sh_1.hexdigest ())
    '7d3d6632e1916e4fd08f1fd8e07c4363a2265be1'

    >>> byte_foo = b"foo"
    >>> text_foo = "foo"
    >>> intl_foo = list (ord (x) for x in text_foo)

    >>> print_prepr (Secure_Hash.sha1 (text_foo).hexdigest ())
    '0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33'

    >>> print_prepr (Secure_Hash.sha1 (byte_foo).hexdigest ())
    '0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33'

    >>> print_prepr (Secure_Hash.sha1 (intl_foo).hexdigest ())
    'd1896add0af72017e4c5a74d55b904887e790a7a'

    >>> print_prepr (Secure_Hash.sha1 (text_foo).b64digest ())
    'C_7Hteo-D9vJXQ3UfzxbwnXaijM='

    >>> print_prepr (Secure_Hash.sha1 (byte_foo).b64digest ())
    'C_7Hteo-D9vJXQ3UfzxbwnXaijM='

    >>> print_prepr (Secure_Hash.sha1 (byte_foo).b64digest (None))
    'C+7Hteo/D9vJXQ3UfzxbwnXaijM='

    >>> print_prepr (Secure_Hash.sha1 (intl_foo).b64digest ())
    '0Ylq3Qr3IBfkxadNVbkEiH55Cno='

    >>> s384 = Secure_Hash.sha384
    >>> m384 = HMAC.sha384

    >>> Secure_Hash.sha384 is s384
    True

    >>> HMAC.sha384 is m384
    True

    >>> s384 is m384
    False

    >>> Secure_Hash.sha384.sha1 is Secure_Hash.sha1
    True

    >>> import binascii
    >>> sha_256 = Secure_Hash.sha256

    >>> print_prepr (sha_256 (text_foo).hexdigest ())
    '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'

    >>> dk2 = binascii.hexlify (sha_256.pbkdf2_hmac (b'password', b'salt', 100))
    >>> print_prepr (dk2)
    '07e6997180cf7f12904f04100d405d34888fdf62af6d506a0ecc23b196fe99d8'

    >>> dk5 = binascii.hexlify (sha_256.pbkdf2_hmac (b'password', b'salt', 100000))
    >>> print_prepr (dk5)
    '0394a2ede332c9a13eb82e9b24631604c31df978b4e2f0fbd2c549944f9d79a5'

    >>> hmac = sha_256.hmac ("key", "message")
    >>> print_prepr (hmac.hexdigest ()) ### freshly minted
    '6e9ef29b75fffc5b7abae527d58fdadb2fe42e7219011976917343065f58ed4a'

    >>> hmac.update ("another message")
    >>> hmac.update ([1, 2, 3])
    >>> print_prepr (hmac.hexdigest ()) ### after update
    'bc02ee3ca85743ac30c928baed2989c05024a23d5e19c37c5260807ae784d83f'

"""

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Secure_Hash
