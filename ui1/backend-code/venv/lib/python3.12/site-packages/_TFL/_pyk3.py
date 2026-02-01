# -*- coding: utf-8 -*-
# Copyright (C) 2010-2020 Christian Tanzer All rights reserved
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
#    TFL._pyk3
#
# Purpose
#    Python3 specific implementation of TFL.pyk
#
# Revision Dates
#    16-Jun-2010 (CT) Creation
#     5-Jan-2011 (CT) `pickle` added
#    23-May-2013 (CT) Add `string_types`, `text_type`, `Classic_Class_Type`
#    23-May-2013 (CT) Add class decorator `adapt__bool__`
#    24-May-2013 (CT) Add `adapt__div__`, `adapt__str__`
#    24-May-2013 (CT) Add `iteritems`, `iterkeys`, `itervalues`, `xrange`
#    24-May-2013 (CT) Add `int_types`
#    25-May-2013 (CT) Add `new_instancemethod`, `izip`, `zip`
#    26-May-2013 (CT) Convert to class/instance to allow lazy imports
#    28-May-2013 (CT) Fix `new_instancemethod`
#     9-Oct-2013 (CT) Fix `zip`, `izip`
#    27-Nov-2013 (CT) Add `number_types`
#     3-Jan-2014 (CT) Add `encoded`, `user_config`
#    17-Feb-2014 (CT) Add `decoded`
#    22-Aug-2014 (CT) Allow multiple `encodings` for `encoded`
#     7-Oct-2014 (CT) Change `iter*` to wrap `result` in `iter`
#     7-Oct-2014 (CT) Add `config_parser`, `ifilter`, `reprify`
#     7-Oct-2014 (CT) Fix `encoded`
#     9-Oct-2014 (CT) Add `builtins`
#    10-Oct-2014 (CT) Add `urlencode`, `urlparse`
#    13-Oct-2014 (CT) Add `byte_type`
#    13-Oct-2015 (CT) Add `copyreg`
#    20-Oct-2015 (CT) Add `as_str`
#    25-Oct-2015 (CT) Add `pickle_protocol`
#     3-Nov-2015 (CT) Move argument "replace" to `else` clause of `decoded`
#     4-Nov-2015 (CT) Add `email_as_bytes`, `email_message_from_bytes`
#    10-Oct-2016 (CT) Make Python-2 compatible
#                     + Define `fprint` as a function that calls `print`
#                       - `staticmethod (print)` triggers a syntax error
#                     + Import `print_function` from `__future__`
#    31-Mar-2020 (CT) Remove `adapt__bool__`
#     1-Apr-2020 (CT) Remove `adapt__div__`, `adapt__str__`
#     2-Apr-2020 (CT) Remove `range`, `xrange`
#     2-Apr-2020 (CT) Remove `builtins`
#     2-Apr-2020 (CT) Remove `Classic_Class_Type`
#     2-Apr-2020 (CT) Remove `copyreg`
#     2-Apr-2020 (CT) Add `number_types_x`
#     2-Apr-2020 (CT) Increase `pickle_protocol` to 4
#     2-Apr-2020 (CT) Remove `fprint`
#     2-Apr-2020 (CT) Remove `ifilter`
#     2-Apr-2020 (CT) Remove `long_types`
#     2-Apr-2020 (CT) Remove `text_type`
#     2-Apr-2020 (CT) Remove `unichr`
#     2-Apr-2020 (CT) Remove `urlencode`, `urlparse`
#     2-Apr-2020 (CT) Remove `zip`
#    ««revision-date»»···
#--

import functools

def lazy_property (fct) :
    name = fct.__name__
    @functools.wraps (fct)
    def _ (self) :
        try :
            result = self.__dict__ [name]
        except KeyError :
            result = self.__dict__ [name] = fct (self)
        return result
    return property (_)
# end def lazy_property

class _Pyk_ (object) :
    """Python2 specific implementation of TFL.pyk.

       Use a class instead of module-level definitions to allow lazy imports.
    """

    byte_type  = bytes
    byte_types = (bytes, )

    @lazy_property
    def config_parser (self) :
        import configparser
        return configparser
    # end def config_parser

    @staticmethod
    def decoded (v, * encodings) :
        if not encodings :
            encodings = [pyk.user_config.input_encoding]
        if isinstance (v, bytes) :
            for encoding in encodings :
                try :
                    v = v.decode (encoding)
                except Exception as exc :
                    pass
                else :
                    break
            else :
                v = v.decode (encoding, "replace")
        elif not isinstance (v, str) :
            v = str (v)
        return v
    as_str = decoded # end def decoded

    @lazy_property
    def email_as_bytes (self) :
        from email.message import Message
        return Message.as_bytes
    # end def email_as_bytes

    @lazy_property
    def email_message_from_bytes (self) :
        ### Don't use `email.message_from_string` in Python 3 as that is
        ### utterly broken for strings containing non-ASCII characters
        from email import message_from_bytes
        return message_from_bytes
    # end def email_message_from_bytes

    @staticmethod
    def encoded (v, encoding = None) :
        if encoding is None :
            encoding = pyk.user_config.output_encoding
        if not isinstance (v, (str, bytes)) :
            v = str (v)
        if isinstance (v, str) :
            v = v.encode (encoding, "replace")
        return v
    # end def encoded

    int_types          = (int, )

    @staticmethod
    def iteritems (dct) :
        try :
            items = dct.items
        except AttributeError :
            items = dct.iteritems
        return iter (items ())
    # end def iteritems

    @staticmethod
    def iterkeys (dct) :
        try :
            keys = dct.keys
        except AttributeError :
            keys = dct.iterkeys
        return iter (keys ())
    # end def iterkeys

    @staticmethod
    def itervalues (dct) :
        try :
            values = dct.values
        except AttributeError :
            values = dct.itervalues
        return iter (values ())
    # end def itervalues

    @staticmethod
    def new_instancemethod (function, instance, cls) :
        if instance is None :
            @functools.wraps (function)
            def _ (* args, ** kw) :
                return function (* args, ** kw)
            return _
        else :
            return function
    # end def new_instancemethod

    number_types = (int, float)

    @lazy_property
    def number_types_x (self) :
        import decimal
        return self.number_types + (decimal.Decimal, )
    # end def number_types_x

    @lazy_property
    def pickle (self) :
        import pickle
        return pickle
    # end def pickle

    pickle_protocol = 4 ### `5` needs Python 3.8+, still need to support 3.7

    @staticmethod
    def reprify (r) :
        return pyk.decoded (r)
    # end def reprify

    @lazy_property
    def StringIO (self) :
        import io
        return io.StringIO
    # end def StringIO

    string_types       = (str, )

    @lazy_property
    def user_config (self) :
        from   _TFL.User_Config import user_config
        return user_config
    # end def user_config

# end class _Pyk_

pyk = _Pyk_ ()

### __END__ TFL._pyk3
