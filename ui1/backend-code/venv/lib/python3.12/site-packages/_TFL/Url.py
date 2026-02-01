# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Christian Tanzer All rights reserved
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
#    TFL.Url
#
# Purpose
#    Model a URL and its parts
#
# Revision Dates
#    23-Jun-2010 (CT) Creation
#    24-Jun-2010 (CT) `new` added
#    24-Jun-2010 (CT) Optional argument `fs_path` added
#    13-Jul-2010 (CT) `__contains__` and `split` added
#    13-Jul-2010 (CT) `__init__` changed to accept `Url` instance as `value`
#    28-Jan-2013 (CT) Add `abs_path`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL        import TFL
from   _TFL.pyk    import pyk

from   _TFL.Regexp import *

import _TFL._Meta.Object
import _TFL._Meta.Once_Property

import _TFL.Accessor
import _TFL.Record

class Url (TFL.Meta.Object) :
    """Model a URL and its parts as defined by RFC 3986.

        >>> Url ("http://www.ics.uci.edu/pub/ietf/uri/#Related")
        Url (authority = 'www.ics.uci.edu', fragment = 'Related', path = '/pub/ietf/uri/', query = '', scheme = 'http')
        >>> Url ("scheme://username:password@domain:port/path?foo=bar#anchor")
        Url (authority = 'username:password@domain:port', fragment = 'anchor', path = '/path', query = 'foo=bar', scheme = 'scheme')
        >>> Url ("foo://example.com:8042/over/there?name=ferret#nose")
        Url (authority = 'example.com:8042', fragment = 'nose', path = '/over/there', query = 'name=ferret', scheme = 'foo')
        >>> Url ("/tmp/foo.bar")
        Url (authority = '', fragment = '', path = '/tmp/foo.bar', query = '', scheme = '')
        >>> Url ("http://a/b/c/g;x?y#s")
        Url (authority = 'a', fragment = 's', path = '/b/c/g;x', query = 'y', scheme = 'http')
        >>> Url ("ftp://cnn.example.com&story=breaking_news@10.0.0.1/top_story.htm")
        Url (authority = 'cnn.example.com&story=breaking_news@10.0.0.1', fragment = '', path = '/top_story.htm', query = '', scheme = 'ftp')

        >>> Url ("sqlite://")
        Url (authority = '', fragment = '', path = '', query = '', scheme = 'sqlite')
        >>> Url ("sqlite:///foo.db")
        Url (authority = '', fragment = '', path = '/foo.db', query = '', scheme = 'sqlite')
        >>> Url ("sqlite:////foo.db")
        Url (authority = '', fragment = '', path = '//foo.db', query = '', scheme = 'sqlite')

        >>> Url ("postgresql://scott:tiger@localhost/mydatabase")
        Url (authority = 'scott:tiger@localhost', fragment = '', path = '/mydatabase', query = '', scheme = 'postgresql')
        >>> Url ("postgresql+pg8000://scott:tiger@localhost/mydatabase")
        Url (authority = 'scott:tiger@localhost', fragment = '', path = '/mydatabase', query = '', scheme = 'postgresql+pg8000')

        >>> Url ("hps://test.foo")
        Url (authority = 'test.foo', fragment = '', path = '', query = '', scheme = 'hps')
        >>> Url ("hps:///test.foo")
        Url (authority = '', fragment = '', path = '/test.foo', query = '', scheme = 'hps')
        >>> Url ("hps://")
        Url (authority = '', fragment = '', path = '', query = '', scheme = 'hps')
        >>> Url ("hps:")
        Url (authority = '', fragment = '', path = '', query = '', scheme = 'hps')

        >>> u = Url ("hps://")
        >>> Url.new (u, path = "test.foo")
        Url (authority = '', fragment = '', path = '/test.foo', query = '', scheme = 'hps')
        >>> Url.new (u, path = "/test.foo")
        Url (authority = '', fragment = '', path = '//test.foo', query = '', scheme = 'hps')

        >>> Url.new (u, path = "test.foo", fs_path = True)
        Url (authority = '', fragment = '', path = 'test.foo', query = '', scheme = 'hps')
        >>> Url.new (u, path = "/test.foo", fs_path = True)
        Url (authority = '', fragment = '', path = '/test.foo', query = '', scheme = 'hps')

    """

    _format = "%(scheme)s://%(authority)s/%(path)s"

    ### Use regexp as given by http://www.ietf.org/rfc/rfc3986.txt
    ### and http://www.apps.ietf.org/rfc/rfc3986.html
    ###
    ### (urlparse is broken because it doesn't parse `query` and `fragments`
    ### for unknown schemes)
    _matcher  = Regexp \
        ( r"""^(?:(?P<scheme>[^:/?#]+):)?"""
          r"""(?://(?P<authority>[^/?#]*))?"""
          r"""(?P<path>[^?#]*)"""
          r"""(?:\?(?P<query>[^#]*))?"""
          r"""(?:#(?P<fragment>.*))?"""
        )

    authority = property (TFL.Getter._parsed.authority)
    fragment  = property (TFL.Getter._parsed.fragment)
    path      = property (TFL.Getter._parsed.path)
    query     = property (TFL.Getter._parsed.query)
    scheme    = property (TFL.Getter._parsed.scheme)
    value     = property (TFL.Getter._value)

    def __init__ (self, value, fs_path = False) :
        if isinstance (value, Url) :
            self._value  = value._value
            self._parsed = TFL.Record (** value._parsed._kw)
        elif self._matcher.match (value) :
            self._value  = value
            attrs        = dict \
                ( (k, v or "")
                for (k, v) in pyk.iteritems (self._matcher.groupdict ())
                )
            self._parsed = p = TFL.Record (** attrs)
            if fs_path and p.path.startswith ("/") :
                p.path = p.path [1:]
        else :
            raise ValueError (value)
    # end def __init__

    @classmethod
    def new (cls, proto = None, ** kw) :
        dct = {}
        if proto is not None :
            dct.update (proto._parsed._kw)
        dct.update (kw)
        result = cls._format % dct
        q = dct ["query"]
        if q :
            result = "%s?%s" % (result, q)
        f = dct ["fragment"]
        if f :
            result = "%s#%s" % (result, f)
        return cls (result, fs_path = kw.get ("fs_path"))
    # end def new

    @TFL.Meta.Once_Property
    def abs_path (self) :
        from _TFL import sos
        return sos.path.abspath (self.path)
    # end def abs_path

    def split (self, sep, * args, ** kw) :
        return self._value.split (sep, * args, ** kw)
    # end def split

    def __contains__ (self, item) :
        return item in self._value
    # end def __contains__

    def __repr__ (self) :
        return "Url " + str (self._parsed)
    # end def __repr__

    def __str__ (self) :
        return self._value
    # end def __str__

# end class Url

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Url
