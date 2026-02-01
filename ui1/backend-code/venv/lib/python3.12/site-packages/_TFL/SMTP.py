# -*- coding: utf-8 -*-
# Copyright (C) 2010-2023 Christian Tanzer All rights reserved
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
#    TFL.SMTP
#
# Purpose
#    Support sending of emails via SMTP
#
# Revision Dates
#    19-Feb-2010 (CT) Creation (factored from `PMA.Sender`)
#    21-Feb-2010 (MG) Support for authentication added
#    16-Jun-2010 (CT) s/print/pyk.fprint/
#    27-Dec-2010 (CT) Optional init-arguments added,
#                     `open` and `close` factored and extended (`use_tls`)
#                     `connection` added and used
#    12-Jun-2012 (CT) Import `email.utils`, not `email.Utils` (<= Python 2.4)
#    19-Jun-2012 (CT) Add `header` and apply it in `send_message`
#     6-Jul-2012 (CT) Add `SMTP_Logger`
#    18-Nov-2013 (CT) Change default `charset` to `utf-8`
#    17-Feb-2014 (CT) Change `SMTP_Logger.send` to use `pyk.encoded`
#    31-Mar-2014 (CT) Simplify, and fix, `header` for Python-3
#     8-Oct-2015 (CT) Remove guard against text-type from `__call__`
#                     (Python 3.5 expects `str`, not `bytes`)
#    16-Oct-2015 (CT) Add `__future__` imports
#    20-Oct-2015 (CT) Use `pyk.as_str`
#    20-Oct-2015 (CT) Change `header` to do the same for Python-2 and -3
#    20-Oct-2015 (CT) Add doctests for `SMTP_Logger`, `SMTP_Tester`
#    22-Oct-2015 (CT) Encode `msg` argument to `server.sendmail`
#    23-Oct-2015 (CT) Remove call to `server.close` from `close`
#     4-Nov-2015 (CT) Work around Python-3 bugs
#                     * Use pyk.email_as_bytes
#                     * Use pyk.email_message_from_bytes
#                     * Call `encoders.encode_7or8bit` to ensure a proper
#                       setting of "Content-Transfer-Encoding"
#    17-Sep-2019 (CT) Work around more Python-3 bugs
#                     * Factor `_addresses_from_header`
#    25-Mar-2020 (CT) Use `policy.default`
#                     * with the default policy (`policy.compat32`),
#                       unicode headers are broken
#    25-Mar-2020 (CT) Add `content_transfer_encoding`
#    25-Mar-2020 (CT) Change `header` to `.encode` the result of `Header`
#                     * Otherwise, assigning the header to an `email` objects
#                       dies with an exception
#                         TypeError: 'Header' object is not subscriptable
#                     * Although such a usage is officially documented
#    14-May-2022 (CT) Add a `Message-Id` header, if necessary
#    12-Sep-2023 (CT) Add exception handler to `send_message` to display
#                     failing header value
#                     * Python mail.policy gives an error message that doesn't
#                       match the input
#    14-Sep-2023 (CT) Fix typos in last change
#    ««revision-date»»···
#--

from   _TFL                    import TFL
from   _TFL.pyk                import pyk
from   _TFL.portable_repr      import portable_repr

import _TFL._Meta.Object
import _TFL.Context

from   email                   import encoders, message, policy
from   email.header            import Header, decode_header, make_header
from   email.utils             import formatdate

import datetime
import logging
import smtplib
import sys
import uuid

class SMTP (TFL.Meta.Object) :
    """Send emails via SMTP"""

    charset                             = "utf-8"
    content_transfer_encoding           = None
    local_hostname                      = None
    mail_host                           = "localhost"
    mail_port                           = None
    password                            = None
    user                                = None
    use_tls                             = False

    def __init__ \
            ( self
            , mail_host                 = None
            , mail_port                 = None
            , local_hostname            = None
            , user                      = None
            , password                  = None
            , use_tls                   = None
            , charset                   = None
            , content_transfer_encoding = None
            ) :
        if mail_host is not None :
            self.mail_host = mail_host
        if mail_port is not None :
            self.mail_port = mail_port
        if local_hostname is not None :
            self.local_hostname = local_hostname
        if user is not None :
            self.user = user
        if password is not None :
            self.password = password
        if use_tls is not None :
            self.use_tls = use_tls
        if charset is not None :
            self.charset = charset
        if content_transfer_encoding is not None :
            self.content_transfer_encoding = content_transfer_encoding
        self.server = None
    # end def __init__

    def __call__ (self, text, mail_opts = (), rcpt_opts = None) :
        email = pyk.email_message_from_bytes \
            (pyk.encoded (text, self.charset), policy = policy.default)
        self.send_message (email, mail_opts = mail_opts, rcpt_opts = rcpt_opts)
    # end def __call__

    def close (self) :
        assert self.server is not None
        try :
            self.server.quit ()
        finally :
            self.server = None
    # end def close

    @TFL.Contextmanager
    def connection (self) :
        close_p = self.server is not None
        server  = self.open ()
        try :
            yield server
        finally :
            if close_p :
                self.close ()
    # end def connection

    def header (self, s, charset = None, ** kw) :
        """Wrap `s` in `email.header.Header` if necessary.

           Wrapping is done only if `s` contains non-ASCII characters;
           applying `Header` to pure ASCII strings adds stupid line noise to
           email addresses!

        >>> smtp = SMTP ()
        >>> print (smtp.header ("christian.tanzer@swing.co.at"))
        christian.tanzer@swing.co.at
        >>> print (smtp.header ("Umlautbehaftet äöüß", header_name="Subject").encode ())
        b'=?utf-8?b?VW1sYXV0YmVoYWZ0ZXQgw6TDtsO8w58=?='

        """
        if charset is None :
            charset = self.charset
        result = s
        if isinstance (result, pyk.byte_type) :
            decoded = decode_header (result)
            if any (c for ds, c in decoded) :
                result = make_header \
                    (list ((ds, c or charset) for ds, c in decoded), ** kw)
        if not isinstance (result, Header) :
            if isinstance (result, pyk.byte_type) :
                try :
                    result  = result.decode (charset)
                except UnicodeError :
                    charset = "utf-8"
                    result  = result.decode (charset)
            try :
                result.encode ("ascii")
            except UnicodeError :
                result = Header (s, charset = charset, ** kw).encode ()
        return result
    # end def header

    def open (self) :
        if self.server is None :
            result = self.server = smtplib.SMTP \
                (self.mail_host, self.mail_port, self.local_hostname)
            if self.use_tls :
                result.ehlo     ()
                result.starttls () ### Still need another `ehlo` after this
            result.ehlo ()
            if self.user :
                result.login (self.user, self.password)
        return self.server
    # end def open

    def send (self, from_addr, to_addrs, msg, mail_opts = (), rcpt_opts = None) :
        with self.connection () as server :
            msg_x = pyk.encoded (msg, self.charset)
            server.sendmail (from_addr, to_addrs, msg_x, mail_opts, rcpt_opts)
    # end def send

    def send_message (self, email, envelope = None, mail_opts = (), rcpt_opts = None) :
        assert isinstance (email, message.Message)
        if envelope is None :
            envelope = email
        to_addrs = envelope ["To"]
        to       = set (self._addresses_from_header (to_addrs))
        for k in "cc", "bcc", "dcc" :
            for h in envelope.get_all (k, []) :
                if h :
                    to.update (self._addresses_from_header (h))
            if k != "cc" :
                del email [k]
        if "Date" not in email :
            email ["Date"] = formatdate ()
        if "Content-Type" not in email :
            charset = self.charset
            email ["Content-Type"] = \
                """text/plain; charset="%s" """ % (charset, )
        else :
            charset = email.get_charset ()
        if self.content_transfer_encoding :
            if "Content-transfer-encoding" in email :
                del email ["Content-transfer-encoding"]
            email ["Content-transfer-encoding"] = self.content_transfer_encoding
        elif "Content-transfer-encoding" not in email \
                and not email.is_multipart () :
            encoders.encode_7or8bit (email)
        for k in "Subject", "To", "From", "CC", "BCC" :
            vs = email.get_all (k)
            if vs :
                del email [k]
                for v in vs :
                    vh = self.header (v, charset, header_name = k)
                    try :
                        email [k] = vh
                    except Exception as exc :
                        ### 12-Sep-2023 18:15
                        ### Suddenly get an exception::
                        """
                          File "/swing/Project/Python/_TFL/SMTP.py", line 232, in send_message
                            email [k] = vh
                            ~~~~~^^^^
                          File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/email/message.py", line 436, in __setitem__
                            self._headers.append(self.policy.header_store_parse(name, val))
                                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                          File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/email/policy.py", line 146, in header_store_parse
                            raise ValueError("Header values may not contain linefeed "
                        ValueError: Header values may not contain linefeed or carriage return characters
                        """
                        print \
                            ( "Exception `%s`"
                              "\n  from mail header `%s`"
                              "\n  with value `%s`"
                              "\n  linefeed in header : %s"
                              "\n  c-return in header : %s"
                            % (exc, k, v, "\n" in v, "\r" in v)
                            )
                        ### The print statement shows ::
                        """
                        Exception `Header values may not contain linefeed or carriage return characters`
                          from mail header `To`
                          with value `Alan Third <alan@idiocy.org>, Christian Tanzer <tanzer@gg32.com>, Gerd Möllmann <gerd.moellmann@gmail.com>, 65843-done@debbugs.gnu.org`
                          linefeed in header : False
                          c-return in header : False
                        """
                        ### WTF ???
                        raise
        if "Message-Id" not in email :
            self._add_message_id (email)
        ### In Python 3, `email.as_string` is useless because it returns a
        ### base64 encoded body if there are any non-ASCII characters
        ### (setting Content-Transfer-Encoding to "8bit" does *not* help)
        self.send \
            ( envelope ["From"], list (to), pyk.email_as_bytes (email)
            , mail_opts, rcpt_opts
            )
    # end def send_message

    def _addresses_from_header (self, addrs) :
        ### Unfortunately, the `email` package is a fucking mess of
        ### incompatibilities between various Python versions and
        ### **badly documented** on top
        ###
        ### * Python 2 returns strings for address headers, e.g., `To`, `cc`
        ### * Python 3 returns objects for address headers, but which type of
        ###   object isn't documented, except for
        ###       `the returned value is an instance of a subclass of
        ###       email.headerregistry.BaseHeader.`
        ###   - I'd have guessed, the returned object type to be
        ###       `email.headerregistry.AddressHeader` or
        ###       `.SingleAddressHeader`
        ###     but python3.6 then died with::
        ###       'Header' object has no attribute 'addresses'
        try :
            splitter = addrs.split
        except AttributeError :
            try :
                results = addrs.addresses
            except AttributeError :
                results = [pyk.as_str (addrs)]
            else :
                results = list (pyk.as_str (r) for r in addrs.addresses)
        else :
            results = list (r.strip () for r in splitter (","))
        return results
    # end def _addresses_from_header

    def _add_message_id (self, email) :
        from email.parser import Parser
        from email.policy import default
        parser   = Parser (policy = default).parsestr
        from_adr = parser ("From: %s" % email ["From"]) ["from"].addresses [0]
        domain   = from_adr.domain
        id       = uuid.uuid1 ()
        email ["Message-Id"] = "<%s@%s>" % (id, domain or "unknown")
    # end def _add_message_id

# end class SMTP

class SMTP_Logger (SMTP) :
    """Log email using `logging` instead of connecting to SMTP server.

    ::

    >>> smtp = SMTP_Logger (charset = "utf-8")
    >>> smtp (_test_email)

"""

    level = "error"

    def __init__ (self, * args, ** kw) :
        self.pop_to_self      (kw, "level")
        self.__super.__init__ (** kw)
    # end def __init__

    def send (self, from_addr, to_addrs, msg, mail_opts = None, rcpt_opts = None) :
        charset = self.charset
        msg_s   = pyk.decoded (msg, charset)
        self._log \
            ( pyk.as_str ("[%s] Email via %s from %s to %s\n    %s", charset)
            , datetime.datetime.now ().replace (microsecond = 0)
            , pyk.as_str (self.mail_host, charset)
            , pyk.as_str (from_addr, charset)
            , list (pyk.as_str (t, charset) for t in to_addrs)
            , pyk.as_str ("\n    ".join (msg_s.split ("\n")), charset)
            )
    # end def send

    @property
    def _log (self) :
        return getattr (logging, self.level, logging.error)
    # end def _log

# end class SMTP_Logger

class SMTP_Tester (SMTP) :
    """Tester writing to stdout instead of connecting to SMTP server.

       >>> smtp = SMTP_Tester (charset = "utf-8")
       >>> smtp (_test_email)
       Email via localhost from sender@example.com to ['receiver@example.com']
       <BLANKLINE>
       Date: Tue, 20 Oct 2015 14:42:23 -0000
       Message-Id: <2546a47c-d37f-11ec-a757-f2f1999dd7e8@example.com>
       Content-Type: text/plain; charset="utf-8"
       Content-Transfer-Encoding: 8bit
       Subject: Test email with some =?utf-8?b?w6TDtsO8w58=?= diacritics
       To: receiver@example.com
       From: sender@example.com
       <BLANKLINE>
       Test email containing diacritics like ö, ä, ü, and ß.
       <BLANKLINE>

    """

    def send (self, from_addr, to_addrs, msg, mail_opts = None, rcpt_opts = None) :
        print \
            ( "Email via", self.mail_host, "from", from_addr, "to"
            , portable_repr (to_addrs), "\n"
            )
        print (pyk.decoded (msg, self.charset))
    # end def send

# end class SMTP_Tester

_test_email = """\
From: sender@example.com
To: receiver@example.com
Subject: Test email with some äöüß diacritics
Date: Tue, 20 Oct 2015 14:42:23 -0000
Message-Id: <2546a47c-d37f-11ec-a757-f2f1999dd7e8@example.com>

Test email containing diacritics like ö, ä, ü, and ß.
"""

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.SMTP
