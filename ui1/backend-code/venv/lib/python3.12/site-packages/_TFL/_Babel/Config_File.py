# -*- coding: utf-8 -*-
# Copyright (C) 2010-2023 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package TFL.Babel.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Babel.Config_File
#
# Purpose
#    Parse the config file for the translations extraction
#
# Revision Dates
#    21-Jan-2010 (MG) Creation
#    30-Jan-2010 (MG) `get_list`: `combine_default` added
#    15-Apr-2012 (CT) Fix doctests
#     7-Oct-2014 (CT) Make Python-3 compatible
#    16-Oct-2015 (CT) Add `__future__` imports
#    19-Aug-2019 (CT) Use `print_prepr`
#    23-Apr-2020 (CT) Use `importlib.import_module`, not `__import__`
#     8-Sep-2023 (CT) Use `config.read_file`, not `.readfp`
#                     (PY 3.12 compatibility)
#    ««revision-date»»···
#--

from   _TFL                    import TFL
from   _TFL.pyk                import pyk

import _TFL._Meta.Object
import _TFL._Babel.Extractor
import _TFL._Babel.PO_File

from   babel.util             import odict

import importlib

class Config_File (TFL.Meta.Object) :
    """A extractor config file.

    >>> from   _TFL.portable_repr import print_prepr

    >>> source = '''[defaults]
    ... load_translations = _MOM, _GTW
    ...
    ... [extractors]
    ... MOM = _MOM.Babel:Extract
    ...
    ... [MOM: **/__babel__.py]
    ...
    ... [python: **.py]
    ... ignore_pattern = **/__*__.py, **/_OMP/**.py
    ... '''

    >>> file = pyk.StringIO (source)
    >>> cfg  = Config_File (file)

    >>> print_prepr (cfg.defaults)
    {'load_translations' : '_MOM, _GTW', 'loaded_translations' : <PO_File MOM/GTW/JNJ>}

    >>> sorted (pyk.iteritems (cfg.extractors))# doctest:+ELLIPSIS
    [('mom', ...), ('python', <function Python at ...>)]

    >>> print (", ".join (sorted (cfg.patterns)))
    mom, python

    """

    load_translation_key = "load_translations"

    def __init__ (self, filename, parent = None) :
        self.__super.__init__ ()
        config = self._as_config_parser (filename)
        parent = self._as_config_parser (parent)
        self.patterns        = odict ()
        self.extractors      = dict (python = TFL.Babel.Extractor.Python)
        self.defaults        = dict  ()
        self._method_options = dict  ()
        for cfg in parent, config :
            if cfg :
                self._add_config (cfg)
    # end def __init__

    def _add_config (self, config) :
        for section in config.sections () :
            if section == "extractors" :
                for name, module_spec in config.items (section) :
                    self.extractors [name] = self._load_function (module_spec)
            elif section == "defaults" :
                self.defaults = dict (config.items (section))
            else :
                extractor, pattern               = section.split (":")
                extractor                        = extractor.lower ()
                self.patterns [extractor]        = pattern.strip ()
                self._method_options [extractor] =  dict (config.items
                                                          (section))
        self.defaults ["loaded_translations"] = self._load_pkg_translations \
           (self.defaults.get (self.load_translation_key))
        for mo in list (pyk.itervalues (self._method_options)) :
           self._method_options ["loaded_translations"] = \
               self._load_pkg_translations (mo.get (self.load_translation_key))
    # end def _add_config

    def _as_config_parser (self, filename) :
        config = None
        if filename :
            config = pyk.config_parser.RawConfigParser (dict_type = odict)
            if not hasattr (filename, "read") :
                filename = open ((filename))
            config.read_file (filename)
        return config
    # end def _as_config_parser

    def _load_pkg_translations (self, pkg) :
        if pkg :
            return TFL.Babel.PO_File.combine_package_translations \
                (pkg.split (","))
        return dict ()
    # end def _load_pkg_translations

    def get (self, option, method = None, default = None) :
        mo = self._method_options.get (method, {})
        de = self.defaults
        return mo.get (option, de.get (option, default))
    # end def get

    def get_list \
            ( self, option
            , method          = None
            , default         = ()
            , combine_default = False
            ) :
        value = self.get (option, method, default)
        if isinstance (value, pyk.string_types) :
            value = set (p.strip () for p in value.split (","))
        if combine_default :
            default_value = self.get (option, "defaults", None)
            if default_value :
                value.update (p.strip () for p in default_value.split (","))
        return value
    # end def get_list

    def _load_function (self, spec) :
        module_spec, fct_name = spec.split (":")
        module                = importlib.import_module (module_spec)
        return getattr (module, fct_name)
    # end def _load_function

    def options (self, method) :
        result = self.defaults.copy ()
        result.update (self._method_options [method])
        return result
    # end def options

# end class Config_File

if __name__ != "__main__" :
    TFL.Babel._Export ("*")
### __END__ TFL.Babel.Config_File
