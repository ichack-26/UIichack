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
#    TFL.G8R
#
# Purpose
#    Support for reverse localization, i.e., globalization
#
# Revision Dates
#    10-Feb-2016 (CT) Creation
#    15-Feb-2016 (CT) Add `localized`, `map_r`, `replacer_r`, `G8R_Multi`
#    30-Nov-2016 (CT) Add `words`
#    30-Nov-2016 (CT) Add `LC`
#    30-Nov-2016 (CT) Add `keys`, `words`, `globalized` to `G8R_Multi`
#    ««revision-date»»···
#--

"""Support for reverse localization, i.e., globalization."""

from   _TFL                import TFL
from   _TFL.I18N           import _T
from   _TFL.Regexp         import Regexp, Dict_Replacer, Multi_Re_Replacer, re
from   _TFL.pyk            import pyk

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL._Meta.Property

from   itertools           import chain as ichain

class G8R (TFL.Meta.Object) :
    """Globalizer for a specific set of words."""

    _lowercase     = False
    _re_head       = r"\b"
    _re_tail       = r"\b"
    _skip_language = "en"

    def __init__ (self, * word_lists, ** kw) :
        self._words = ws  = tuple (ichain (* word_lists))
        self._keys        = set (ws)
        self._maps        = {}
        self._maps_r      = {}
        self._replacers   = {}
        self._replacers_r = {}
        self.pop_to_self \
            ( kw
            , "lowercase", "re_head", "re_tail", "skip_language"
            , prefix = "_"
            )
    # end def __init__

    def __call__ (self, text, count = 0) :
        """Globalize `text`, i.e., replace localized words in `text` with their
           primary — normally english — version.
        """
        return self._transformed (text, count, self.replacer)
    # end def __call__

    @TFL.Meta.Once_Property
    def LC (self) :
        """Globalizer enforcing lower case. """
        if self._lowercase :
            return self
        else :
            return self.__class__ \
                ( self._words
                , lowercase     = True
                , re_head       = self._re_head
                , re_tail       = self._re_tail
                , skip_language = self._skip_language
                )
    # end def LC

    @property
    def keys (self) :
        """Set of words globalized by this globalizer."""
        return self._keys
    # end def keys

    @property
    def map (self) :
        """Map of localized words to their globalized versions."""
        lang = TFL.I18N.Config.choice [0]
        if lang and lang != self._skip_language :
            try :
                result = self._maps [lang]
            except KeyError :
                result = self._maps [lang] = {}
                lcase  = self._lowercase
                sk     = lambda k : (-len (k), k)
                for k in sorted (self._keys, key = sk) :
                    l = _T (k)
                    if lcase :
                        l = l.lower ()
                        k = k.lower ()
                    if l != k or l in result :
                        ### Don't map identical strings unless there is a
                        ### translation already, e.g., english `Mon` and `Mo`
                        ### both translate to german `Mo`: in this case we want
                        ### to retain the shorter translation
                        result [l] = k
            return result
    # end def map

    @property
    def map_r (self) :
        """Map of globalized words to their localized versions."""
        lang = TFL.I18N.Config.choice [0]
        if lang :
            try :
                result = self._maps_r [lang]
            except KeyError :
                map = self.map
                result = self._maps_r [lang] = \
                    {v:k for k, v in pyk.iteritems (map)}
            return result
    # end def map_r

    @property
    def replacer (self) :
        """A Dict_Replacer that will replace any element of `maps`."""
        map = self.map
        if map :
            lang = TFL.I18N.Config.choice [0]
            try :
                result = self._replacers [lang]
            except KeyError :
                result = self._replacers [lang] = Dict_Replacer \
                    (map, 0, self._re_head, self._re_tail)
            return result
    # end def replacer

    @property
    def replacer_r (self) :
        """A Dict_Replacer that will replace any element of `maps`."""
        map_r = self.map_r
        if map_r :
            lang = TFL.I18N.Config.choice [0]
            try :
                result = self._replacers_r [lang]
            except KeyError :
                result = self._replacers_r [lang] = Dict_Replacer \
                    (map_r, 0, self._re_head, self._re_tail)
            return result
    # end def replacer

    @property
    def words (self) :
        """Words globalized by this globalizer."""
        return self._words
    # end def words

    def globalized (self, text, count = 0) :
        """Globalize `text`, i.e., replace localized words in `text` with their
           primary — normally english — version.
        """
        return self._transformed (text, count, self.replacer)
    # end def globalized

    def localized (self, text, count = 0) :
        """Localize `text`, i.e., replace globalized words in `text` with their
           localized version.
        """
        return self._transformed (text, count, self.replacer_r)
    # end def localized

    def _transformed (self, text, count, replacer) :
        result = text.lower () if self._lowercase else text
        if replacer is not None :
            result = replacer (result, count)
        return result
    # end def _transformed

# end class G8R

class G8R_Multi (Multi_Re_Replacer) :
    """Wrap multiple `G8R` instances."""

    _lowercase     = False

    @TFL.Meta.Once_Property
    def LC (self) :
        """Globalizer enforcing lower case."""
        if self._lowercase :
            return self
        else :
            rereps_lc = tuple (g8r.LC for g8r in self.rereps)
            result    = self.__class__ (* rereps_lc)
            result._lowercase = True
            return result
    # end def LC

    @TFL.Meta.Once_Property
    def keys (self) :
        return set (self.words)
    # end def keys

    @TFL.Meta.Once_Property
    def words (self) :
        return sorted (ichain (* (g8r.words for g8r in self.rereps)))
    # end def words

    def globalized (self, text, count = 0) :
        """Globalize `text`, i.e., replace localized words in `text` with their
           primary — normally english — version.
        """
        result = text
        for g8r in self.rereps :
            result = g8r.globalized (result, count)
        return result
    # end def globalized

    def localized (self, text, count = 0) :
        """Localize `text`, i.e., replace globalized words in `text` with their
           localized version.
        """
        result = text
        for g8r in self.rereps :
            result = g8r.localized (result, count)
        return result
    # end def localized

# end class G8R_Multi

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.G8R
