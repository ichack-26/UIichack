# -*- coding: utf-8 -*-
# Copyright (C) 2010-2020 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg. martin@mangari.org
# ****************************************************************************
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Babel
#
# Purpose
#    Some extension for the translation system Babel
#
# Revision Dates
#    20-Jan-2010 (MG) Creation
#    21-Jan-2010 (MG) Option to ignore files added
#    21-Jan-2010 (MG) Doc strings are only added specified in the options.
#                     Indent of doc strings is normalized
#    21-Jan-2010 (MG) Command interface added
#    21-Jan-2010 (MG) `Translations` replaced by `Existing_Translations`
#    25-Jan-2010 (MG) Multiprocess support added
#    17-Feb-2010 (CT) `compile` changed to use `__import__` instead of
#                     `execfile`
#    26-Feb-2010 (CT) `process_count` forced to `1`
#    10-Feb-2016 (CT) Add `root_dir` to `from_sys_modules`; put it in front
#    10-Oct-2016 (CT) Make Python-3 compatible
#     6-Apr-2020 (CT) Use `os.replace`, not `os.rename`
#    23-Apr-2020 (CT) Use `importlib.import_module`, not `__import__`
#    ««revision-date»»···
#--

from   _TFL                     import TFL
from   _TFL.pyk                 import pyk

import _TFL._Babel.Extract
import _TFL._Babel.Config_File
import _TFL.CAO
import _TFL.defaultdict

import glob
import importlib
import os
import shutil
import sys
import tempfile

try :
    from multiprocessing import Process, JoinableQueue
except ImportError :
    Process = None

class Language_File_Collection (object) :
    """Collect messsage catalog files."""

    def __init__ (self, directories, lang = None, suffix = "") :
        self.languages          = set ()
        self.directories        = set ()
        self.files_per_language = TFL.defaultdict (list)
        for d in directories :
            self._add_languages (d, set (lang), suffix)
    # end def __init__

    @classmethod
    def from_sys_modules (cls, lang = None, suffix = "", root_dir = None) :
        directories = set ()
        i18n_dirs   = []
        path        = os.path
        for mod in sys.modules.values () :
            if isinstance (getattr (mod, "__file__", None), pyk.string_types) :
                directories.add (path.abspath (path.dirname (mod.__file__)))
        if root_dir :
            ### Put `root_dir` in front all `i18n_dirs`
            ### + the sequence of the other directories is non-deterministic
            ### + the first PO-File read defines meta data like project name
            ###   and version
            rdir = path.abspath (root_dir)
            i18n_dirs.append    (rdir)
            directories.discard (rdir)
        for directory in directories :
            i18n = path.join (directory, "-I18N")
            if path.isdir (i18n) :
                i18n_dirs.append (directory)
        return cls (i18n_dirs, lang, suffix)
    # end def from_sys_modules

    def _add_languages (self, directory, restrict_langs, suffix) :
        i18n_dir = os.path.abspath (os.path.join (directory, "-I18N"))
        if restrict_langs :
            self.languages.update (restrict_langs)
            for lang in restrict_langs :
                self.files_per_language [lang].append \
                    (os.path.join (i18n_dir, "%s%s.po" % (lang, suffix)))
        else :
            for f in glob.glob (os.path.join (i18n_dir, "*%s.po" % suffix)) :
                lang = os.path.splitext (os.path.basename (f)) [0].replace \
                    (suffix, "")
                if restrict_langs and lang not in restrict_langs :
                    continue
                self.files_per_language [lang].append (f)
                self.languages.add                    (lang)
                self.directories.add (os.path.dirname (f))
    # end def _add_languages

    def init_or_update (self, cmd) :
        for lang, files in pyk.iteritems (self.files_per_language) :
            for f in files :
                output_dir = os.path.dirname (f)
                template   = "%s%s" % (cmd.template_file, cmd.file_suffix)
                pot_file   = os.path.join    (output_dir, "%s.pot" % template)
                templ      = TFL.Babel.PO_File.load (pot_file, locale = lang)
                if os.path.exists (f) :
                    self._update  (lang, f, cmd, templ, pot_file)
                else :
                  print ("Creating catalog %r based on %r" % (f, pot_file))
                  templ.save (f, fuzzy = False)
    # end def init_or_update

    def _update (self, lang, po_file_n, cmd, pot_file, pot_file_n) :
        print ("Update catalog `%s` based on `%s`" % (po_file_n, pot_file_n))
        po_file = TFL.Babel.PO_File.load (po_file_n, locale = lang)
        po_file.update                   (pot_file, cmd.no_fuzzy)
        tmpname = os.path.join\
            ( os.path.dirname (po_file_n)
            , "%s%s.po" % (tempfile.gettempprefix (), lang)
            )
        try :
            po_file.save \
                ( tmpname
                , ignore_obsolete  = cmd.ignore_obsolete
                , include_previous = cmd.previous
                , sort             = cmd.sort
                )
        except :
            os.remove (tmpname)
            raise
        try :
            os.replace (tmpname, po_file_n)
        except OSError:
            os.remove  (tmpname)
            raise
    # end def _update

    def _output_file_name (self, cmd, lang, po_file_n = None, suffix = "") :
        if cmd.output_file :
            return cmd.output_file
        ext = "js" if cmd.javascript else "mo"
        if not cmd.combine :
            return os.path.join \
                (os.path.dirname (po_file_n), "%s%s.%s" % (lang, suffix, ext))
        return os.path.join \
            ( cmd.output_directory, lang, "LC_MESSAGES"
            , "%s%s.%s" % (cmd.domain, suffix, ext)
            )
    # end def _output_file_name

    def compile (self, cmd) :
        for lang, files in pyk.iteritems (self.files_per_language) :
            for po_file_n in files :
                po_file    = TFL.Babel.PO_File.load (po_file_n)
                if po_file.fuzzy and not cmd.use_fuzzy :
                    print \
                        ( "Catalog %r is marked as fuzzy, skipping"
                        % (po_file_n, )
                        )
                    continue
                for message, errors in po_file.catalog.check ():
                    for error in errors :
                        print \
                            ( "Error: %s:%d: %s"
                            % (po_file_n, message.lineno, error)
                            , file = sys.stderr
                            )
                if cmd.javascript :
                    js_file_n  = self._output_file_name (cmd, lang, po_file_n)
                    print \
                        ("compiling catalog %r to %r" % (po_file_n, js_file_n))
                    po_file.generate_js (lang, js_file_n)
                else :
                    mo_file_n  = self._output_file_name \
                        (cmd, lang, po_file_n, suffix = cmd.file_suffix)
                    print \
                        ("compiling catalog %r to %r" % (po_file_n, mo_file_n))
                    po_file.generate_mo (mo_file_n)
    # end def compile

    def compile_combined (self, cmd) :
        for lang, files in pyk.iteritems (self.files_per_language) :
            po_file   = TFL.Babel.PO_File.combined (* files)
            if po_file.fuzzy and not cmd.use_fuzzy :
                print \
                    ( "Catalog %r is marked as fuzzy, skipping"
                    % (files [0], )
                    )
                continue
            for message, errors in po_file.catalog.check ():
                for error in errors :
                    print ("Error: %s" % (error), file = sys.stderr)
            if cmd.javascript :
                js_file_n = self._output_file_name     (cmd, lang)
                print \
                    ("compiling combined catalog %r to %r" % (files, js_file_n))
                po_file.generate_js (lang, js_file_n)
            else :
                mo_file_n = self._output_file_name \
                        (cmd, lang, suffix = cmd.file_suffix)
                print \
                    ("compiling combined catalog %r to %r" % (files, mo_file_n))
                po_file.generate_mo (mo_file_n)
    # end def compile_combined

# end class Language_File_Collection

def _prefix_path (filename, * prefix) :
    if not os.path.isabs (filename) :
        prefix   = prefix + (filename, )
        filename = os.path.abspath (os.path.join (* prefix))
    return filename
# end def _prefix_path

def _extract_one_directory (base_dir, cmd = None) :
    config        = TFL.Babel.Config_File \
        ( _prefix_path (cmd.extraction_config, base_dir)
        , parent = cmd.global_config
        )
    template_file = _prefix_path (cmd.template_file, base_dir, "-I18N")
    keywords      = cmd.keywords
    TFL.Babel.Extract (base_dir, template_file, config, cmd)
# end def _extract_one_directory

def extract (cmd) :
    if Process :
        ### we cannot use a Pool here because we need to start a ne wprocess
        ### for each extraction to ensure that the MOM Meta Machinery has not
        ### been executed already
        pool = []
        dirs = cmd.argv [:]
        while dirs or pool :
            while dirs and (len (pool) < 1) :
                p = Process \
                    ( target = _extract_one_directory
                    , args   = (dirs.pop (0), cmd)
                    )
                pool.append (p)
                p.start     ()
            i = 0
            while i < len (pool) :
                p = pool [i]
                if not p.is_alive () :
                    pool.pop (i)
                    i -= 1
                i += 1

    else :
        for base_dir in cmd.argv :
            _extract_one_directory (base_dir, cmd)
# end def extract

Extract = TFL.CAO.Cmd \
    ( extract
    , name = "extract"
    , args =
        ( "directories:P"
            "?Directories where the extraction should start"
        ,
        )
    , opts =
        ( "bugs_address:S=bugs@domain.com?"
            "Email address to report translation bugs"
        , "charset:S=utf-8?Encoding for the pot file"
        , "copyright_holder:S=Company?Copyright holder"
        , "extraction_config:S=babel.cfg?"
            "Name of the extraction config fileconfig"
        , "global_config:P?A global config file"
        , "keywords:S,?Additional extraction keyowrds"
        , "no_location:B?Suppress the location information"
        , "omit_header:B?Omit the header in the POT file"
        , "sort:B?Generated template should be alphabetical sorted"
        , "strip_comment_tags:B?Strip the comment tags"
        , "project:S=Project?Name of the project/application"
        , "template_file:P=template.pot?Name of the template file"
        , "version:S=1.0?Product version"
        , "width:I=76?Output width in the POT file"
        )
    , min_args = 1
    )

def language (cmd) :
    """Create or update the message catalog for a language."""
    lang_files = Language_File_Collection \
        (cmd.argv, cmd.languages, cmd.file_suffix)
    lang_files.init_or_update (cmd)
# end def language

Language = TFL.CAO.Cmd \
    ( language
    , name = "language"
    , args =
        ( "directories:P"
            "?Directories where the languages will be placed/searched"
        ,
        )
    , opts =
        ( "languages:S,?Which language should be processed"
        , "ignore_obsolete:B?"
            "Do not include obsolete messages in the output"
        , "file_suffix:S=?Add a suffix to the language file names"
        , "no_fuzzy:B?Do not use fuzzy matching (default False)"
        , "output_directory:P=-I18N?Output directory"
        , "previous:B?Keep previous msgids of translated messages"
        , "sort:B?Generated po should be alphabetical sorted"
        , "template_file:P=template?Name of the template file"
        )
    , min_args = 1
    )

def compile (cmd) :
    if cmd.import_file :
        d, p = os.path.split    (cmd.import_file)
        f, e = os.path.splitext (p)
        with TFL.Context.list_push (sys.path, d) :
            m = importlib.import_module (f)
        lang_coll = Language_File_Collection.from_sys_modules \
            (cmd.languages, cmd.file_suffix, d or "./")
    else :
        lang_coll = Language_File_Collection \
            (cmd.argv, cmd.languages, cmd.file_suffix)
    if cmd.combine :
        lang_coll.compile_combined (cmd)
    else :
        lang_coll.compile          (cmd)
# end def compile

Compile = TFL.CAO.Cmd \
    ( compile
    , name = "compile"
    , args =
        ( "directories:P?Directories where the language files should be "
            "searched"
        ,
        )
    , opts =
        ( "combine:B?Combine all files for a langage into one mo file"
        , "domain:S=messages?Domain for the meesage catalog"
        , "file_suffix:S=?File suffix which should be added to the language"
        , "import_file:P?Determine directories from imported modules after "
            "importing this files"
        , "javascript:B?Generate a js file instead of a mo"
        , "languages:S,?Which language should be processed"
        , "output_directory:P=locale?Output directory"
        , "output_file:P?Explicit name of the MO file"
        , "use_fuzzy:B?Compile fuzzy files as well (default False)"
        )
    , min_args = 0
    )

_Command = TFL.CAO.Cmd \
    ( name = "TFL.Babel"
    , args = (TFL.CAO.Cmd_Choice ("command", Extract, Language, Compile), )
    )

if __name__ == "__main__" :
    _Command ()
### __END__ TFL.Babel
