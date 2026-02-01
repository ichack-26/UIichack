# -*- coding: utf-8 -*-
# Copyright (C) 2010-2020 Martin Glueck All rights reserved
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
#    Extract
#
# Purpose
#    Handel the extraction procedure
#
# Revision Dates
#    21-Jan-2010 (MG) Creation
#    25-Jan-2010 (MG) Convert absolute path to relative path
#    30-Jan-2010 (MG) `ignore_patterns` combine with defaults
#    24-Feb-2010 (MG) Duplicate message check added
#    27-Feb-2010 (MG) Allow the extraction method to specify in which file
#                     the translation was found
#    23-Oct-2014 (CT) Add missing `__future__` import of `print_function`
#    16-Oct-2015 (CT) Add `__future__` imports
#    16-Feb-2016 (CT) Use `os.path.relpath`, not `babel.util.relpath`
#                     (broke in Babel 2.2)
#    23-Apr-2020 (CT) Use `importlib.import_module`, not `__import__`
#    10-May-2020 (CT) Adapt to Python-3
#    ««revision-date»»···
#--

from   _TFL                          import TFL
from   _TFL.predicate                import any_true

import _TFL.relative_to_search_path
import _TFL._Babel.PO_File

import importlib
import os
import sys

from   babel.util             import pathmatch
from   babel.messages.extract import empty_msgid_warning

class Existing_Translations (object) :
    """Read multiple POT files and checks whether a certain message is
       already part of another template
    """

    def __init__ (self, packages) :
        self.pot_file
        if packages :
            for pkg in (p.strip () for p in packages.split (",")) :
                module   = importlib.import_module (pkg)
                base_dir = os.path.dirname (module.__file__)
                pot_file = os.path.join (base_dir, "-I18N", "template.pot")
                self.pot_files.append (read_po (open (pot_file)))
    # end def __init__

    def __contains__ (self, message) :
        return any_true (message in pot for pot in self.pot_files)
    # end def __contains__

# end class Existing_Translations

class Skip (Exception) : pass

Default_Keywords = dict \
    ( _         = (1, )
    , _T        = (1, )
    , _Tn       = (1, 2)
    , N_        = (1, )
    , gettext   = (1, )
    , ugettext  = (1, )
    , ngettext  = (1, 2)
    , ungettext = (1, 2)
    )

def Extract (dirname, template_file, config, cmd) :
    absname = os.path.abspath (dirname)
    po_file = TFL.Babel.PO_File \
        ( project            = cmd.project
        , version            = cmd.version
        , bugs_address       = cmd.bugs_address
        , copyright_holder   = cmd.copyright_holder
        , charset            = cmd.charset
        , width              = cmd.width
        , no_location        = cmd.no_location
        , omit_header        = cmd.omit_header
        , sort               = cmd.sort
        )
    keywords = Default_Keywords.copy ()
    keywords.update (dict (k, None) for k in cmd.keywords)
    for root, dirnames, filenames in os.walk (absname) :
        dirnames.sort  ()
        for filename in sorted (filenames) :
            filename = os.path.relpath \
                (os.path.join (root, filename).replace (os.sep, '/'), dirname)
            try :
                for method_name, pattern in config.patterns.items () :
                    if pathmatch (pattern, filename) :
                        for pattern in config.get_list \
                            ("ignore_patterns", method_name, set (), True) :
                            if pathmatch (pattern, filename) :
                                raise Skip
                        filepath = os.path.join (absname, filename)
                        rfp      = TFL.relative_to_python_path (filepath)
                        print ("Method `%-10s`: `%s" % (method_name, filename))
                        trans = config.get ("loaded_translations", method_name)
                        for lineno, message, comments, found_in in \
                                _extract_from_file    \
                                    ( method_name
                                    , filepath
                                    , config
                                    , cmd
                                    , keywords
                                    ) :
                            fn = rfp
                            if found_in :
                                fn = TFL.relative_to_python_path (found_in)
                            if message not in trans :
                                po_file.add \
                                    ( message, None, [(fn, lineno)]
                                    , auto_comments = comments
                                    )
                        break
            except Skip :
                print ("Ignore             : `%s" % (filename, ))
    print ("Create template file", template_file, file = sys.stderr)
    po_file.save (template_file)
# end def Extract

def _extract_from_file (method_name, file_name, config, cmd, keywords) :
    method = config.extractors [method_name]
    file   = open (file_name, "rb")
    for lineno, funcname, messages, comments, found_in in method \
        ( file, keywords
        , comment_tags = ()
        , config       = config
        , method       = method_name
        ) :
        if funcname :
            spec = keywords [funcname] or (1,)
        else:
            spec = (1,)
        if not isinstance (messages, (list, tuple)) :
            messages = [messages]
        if not messages :
            continue
        # Validate the messages against the keyword's specification
        msgs    = []
        invalid = False
        # last_index is 1 based like the keyword spec
        last_index = len (messages)
        for index in spec :
            if last_index < index:
                # Not enough arguments
                invalid = True
                break
            message = messages [index - 1]
            if message is None :
                invalid = True
                break
            msgs.append (message)
        if invalid:
            continue
        first_msg_index = spec [0] - 1
        if not messages [first_msg_index]:
            # An empty string msgid isn't valid, emit a warning
            where = '%s:%i' % (file_name, lineno)
            print (empty_msgid_warning % where, file = sys.stderr)
            continue
        messages = tuple (msgs)
        if len (messages) == 1:
            messages = messages [0]

        if cmd.strip_comment_tags:
            _strip_comment_tags (comments, comment_tags)
        yield lineno, messages, comments, found_in
# end def _extract_from_file

def _strip_comment_tags(comments, tags):
    """Helper function for `extract` that strips comment tags from strings
       in a list of comment lines.  This functions operates in-place.
    """
    def _strip(line):
        for tag in tags:
            if line.startswith(tag):
                return line[len(tag):].strip()
        return line
    comments[:] = map(_strip, comments)
# end def _strip_comment_tags

if __name__ != "__main__" :
    TFL.Babel._Export ("*")
### __END__ TFL.Babel.Extract
