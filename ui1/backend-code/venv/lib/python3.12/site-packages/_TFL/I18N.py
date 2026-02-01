# -*- coding: utf-8 -*-
# Copyright (C) 2009-2019 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.I18N
#
# Purpose
#    Support for internationalization (I18N)
#
# Revision Dates
#    28-Oct-2009 (CT) Creation
#    19-Jan-2010 (CT) `_Tn` changed to make `plural` and `n` optional
#    21-Jan-2010 (MG) Real translation added
#    21-Jan-2010 (CT) Module-level aliases added, `I18N.ungettext` corrected
#    21-Jan-2010 (CT) `load_languages` and `use_language` added
#    21-Jan-2010 (MG) Reworked
#    21-Jan-2010 (MG) `save_eval` added
#    25-Jan-2010 (MG) Support list of languages in `use` and `context`
#    31-Jan-2010 (CT) `import  babel.support` moved inside functions
#    18-Feb-2010 (CT) `Name` added
#    22-Feb-2010 (CT) `choose` factored, `Config.choice` added
#    15-Apr-2010 (MG) `Translations` added and used
#    16-Jun-2010 (CT) `encoding` added
#    16-Jun-2010 (CT) `encoding` changed to Record with fields `file_system`,
#                     `input`, and `output`
#    16-Jun-2010 (CT) s/print/pyk.fprint/
#    17-Jun-2010 (CT) `encode_f` and `encode_o` added
#    18-Jun-2010 (CT) `Translations` factored to `TFL.Babel`
#    18-Jun-2010 (CT) `decode` added
#     4-Aug-2010 (MG) `load`: `log_level` added
#    30-Nov-2010 (CT) s/save_eval/safe_eval/ and removed `strip`-call from it
#    23-Mar-2011 (CT) `_T` defined (instead of aliased) to guard against
#                     empty argument
#    20-Jul-2011 (CT) `_Config_._properties` added
#    20-Jul-2011 (CT) Use encoding information from `TFL.user_config`
#     4-Dec-2013 (CT) Change `safe_eval` to not add coding cookie;
#                     `eval` fails for `unicode` value containing coding cookie
#     9-Dec-2013 (CT) Fix 3-compatibility
#    26-Mar-2014 (CT) Change `ungettext` to use `ugettext` for `n == 1`
#    31-Mar-2014 (CT) Add guard for `AttributeError` to `ugettext`, `ungettext`
#                     (3-compatibility for `gettext.NullTranslations`)
#    31-Mar-2014 (CT) Use `print` in doctest of `context` (3-compatibility)
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    11-Feb-2016 (CT) Add `test_language`
#     9-Dec-2019 (CT) Change `decode` to use `pyk.decoded`, not home-grown code
#                     * Python 3 compatibility
#    ««revision-date»»···
#--

from   _TFL            import TFL
from   _TFL.pyk        import pyk
from   _TFL.Record     import Record
from   _TFL.predicate  import first, split_hst

import _TFL.Decorator
import _TFL.User_Config

import gettext
import locale
import sys

class _Config_ (Record) :

    _properties = ("choice", )

    @property
    def choice (self) :
        """Language choice."""
        return TFL.user_config.language
    # end def choice

    @choice.setter
    def choice (self, value) :
        TFL.user_config.language = value
    # end def choice

# end class _Config_

Config = _Config_ \
   ( Languages  = {"" : gettext.NullTranslations ()}
   , locale_dir = "locale"
   , domains    = ("messages", )
   )
Config.current = Config.Null = Config.Languages [""]

class _Name_ (TFL.Meta.Object) :
    """Translator for names"""

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return _T (name)
    # end def __getattr__

    def __getitem__ (self, key) :
        return _T (key)
    # end def __getitem__

# end class _Name_

def add (self, * languages, ** kw) :
    locale_dir = kw.pop ("locale_dir", Config.locale_dir)
    domains    = kw.pop ("domains",    Config.domains)
    use_lang   = kw.pop ("use", "")
    _load_languages (locale_dir, languages, domains)
    if use_lang :
        use (use_lang)
# end def add

def choose (* lang) :
    def _gen (lang) :
        for l in lang :
            yield l, l
        for l in lang :
            if l :
                a, _, b = split_hst (l, "_")
                yield a, b or a
        yield "", ""
    return first (l for l in _gen (lang) if l [0] in Config.Languages)
# end def choose

@TFL.Contextmanager
def context (* lang) :
    """Temporarily change the translation language
    ### Let's fake some Translations
    >>> from _TFL._Babel.Translations import Translations
    >>> Config.Languages ["l1"] = l1 = Translations ()
    >>> Config.Languages ["l2"] = l2 = Translations ()
    >>> l1._catalog = dict (text1 = u"L1: Text 1", text2 = u"L1: Text 2")
    >>> l2._catalog = dict (text1 = u"L2: Text 1", text2 = u"L2: Text 2")
    >>> print (_T ("text1"))
    text1
    >>> with context ("l1") :
    ...     print (_T ("text1"))
    ...     print (_T ("text2"))
    L1: Text 1
    L1: Text 2
    >>> with context ("l2") :
    ...     print (_T ("text1"))
    ...     print (_T ("text2"))
    L2: Text 1
    L2: Text 2
    """
    old = Config.current, Config.choice
    try :
       use (* lang)
       yield
    finally :
        Config.current, Config.choice = old
# end def context

def decode (s) :
    """Decode `s` using `TFL.user_config.input_encoding`."""
    s = pyk.decoded (s, TFL.user_config.input_encoding)
    return s
# end def decode

def encode_f (s, errors = "replace") :
    """Encodes `s` using `TFL.user_config.file_system_encoding`."""
    return s.encode (TFL.user_config.file_system_encoding, errors)
# end def encode_f

def encode_o (s, errors = "replace") :
    """Encodes `s` using `TFL.user_config.output_encoding`."""
    return s.encode (TFL.user_config.output_encoding, errors)
# end def encode_o

def load (* languages, ** kw) :
    locale_dir        = kw.pop ("locale_dir", Config.locale_dir)
    domains           = kw.pop ("domains",    Config.domains)
    use_lang          = kw.pop ("use",        "")
    log_level         = kw.pop ("log_level",  5)
    Config.domains    = domains
    Config.locale_dir = locale_dir
    _load_languages (locale_dir, languages, domains, log_level)
    if use_lang:
        use (use_lang)
# end def load

def _load_languages (locale_dir, languages, domains, log_level) :
    from _TFL._Babel.Translations import Translations
    if not isinstance (domains, (list, tuple)) :
        domains = (domains, )
    first_dom   = domains [0]
    domains     = domains [1:]
    for lang in languages :
        Config.Languages [lang] = lang_trans = Translations.load \
            (locale_dir, lang, first_dom)
        if not isinstance (lang_trans, Translations) and log_level >= 5 :
            print \
                ( "*** Warning, language %s for domain %s not found!"
                % (lang, first_dom)
                )
        for d in domains :
            new_domain = Translations.load (locale_dir, lang, d)
            if not isinstance (new_domain, Translations) and log_level >= 5 :
                print \
                    ( "*** Warning, language %s for domain %s not found!"
                    % (lang, d)
                    )
            lang_trans.merge (new_domain)
# end def _load_languages

def mark (text):
    """Mark `text` for translation."""
    return str (text)
# end def mark

def safe_eval (value, encoding = None) :
    if encoding and not isinstance (value, str) :
        try :
            value = value.decode (encoding)
        except Exception as exc :
            print (repr (value), encoding)
            raise
    try :
        result = TFL.r_eval (value)
    except SyntaxError :
        print (value)
        raise
    return result
# end def safe_eval

@TFL.Contextmanager
def test_language (lang) :
    """Load and use language `lang` from `locale` in library directory."""
    from _TFL.sos import path
    ld = path.join \
         (path.abspath (path.dirname (path.dirname (__file__))), "locale")
    load (lang, locale_dir = ld)
    with context (lang) :
        yield
# end def test_language

def ugettext (text, trans = None) :
    """Return the localized translation of `text` (as unicode)."""
    try :
        translator = (trans or Config.current).ugettext
    except AttributeError :
        return text
    else :
        return translator (text)
# end def ugettext

def ungettext (singular, plural = None, n = 99, trans = None) :
    """Return the localized translation of `singular/plural` for the plural form
       appropriate for `n` (as unicode).
    """
    if n == 1 :
        return ugettext (singular, trans)
    else :
        if plural is None :
            plural = singular + "s"
        try :
            translator = (trans or Config.current).ungettext
        except AttributeError :
            return plural
        else :
            return translator (singular, plural, n)
# end def ungettext

def use (* lang) :
    Config.choice  = (l, v) = choose (* lang)
    Config.current = Config.Languages [l]
# end def use

_    = mark

def _T (s) :
    if s :
        return ugettext (s)
    return s
# end def _T

_Tn  = ungettext

Name = _Name_ ()

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.I18N
