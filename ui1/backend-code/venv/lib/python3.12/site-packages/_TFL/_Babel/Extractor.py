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
#    TFL.Babel.Extractor
#
# Purpose
#    «text»···
#
# Revision Dates
#    21-Jan-2010 (MG) Creation
#    24-Feb-2010 (MG) Duplicate check moved one level up
#    27-Feb-2010 (MG) Support for different file name added
#    30-Nov-2010 (CT) s/save_eval/safe_eval/ and added `strip`-calls
#    18-Nov-2013 (CT) Change default `encoding` to `utf-8`
#    16-Oct-2015 (CT) Add `__future__` imports
#    10-May-2020 (CT) Adapt to Python-3
#    ««revision-date»»···
#--

from   _TFL                    import TFL
import _TFL.I18N
from    babel.util             import parse_encoding
from    tokenize               import generate_tokens, COMMENT, NAME, OP, STRING
from    tokenize               import NL, NEWLINE, INDENT

def Python (fobj, keywords, comment_tags, config, method) :
    """Code taken from babel directly but extended:
       * collect doc strings of functions and classes as well
       * it is possible to specify a list existing message catalog's so that
         only new translation keys will be added to the new catalog.
    """
    encoding = parse_encoding (fobj) or config.get \
        ("encoding", method, default = "utf-8")
    add_doc_strings = config.get ("add_doc_strings", method, "") == "True"

    ### `generate_tokens` expects strings, `fobj` is binary
    def _readline () :
        result = fobj.readline ()
        return result.decode   (encoding)
    ### now that we know that we have to parse this file, lets start
    tokens   = generate_tokens (_readline)
    in_def   = in_translator_comments  = False
    wait_for_doc_string                = False
    funcname = lineno = message_lineno = None
    call_stack                         = -1
    buf                                = []
    messages                           = []
    translator_comments                = []
    comment_tag                        = None
    doc_string_ignore_tok              = set ((NL, NEWLINE, INDENT, STRING))

    for tok, value, (lineno, _), _, _ in tokens :
        if wait_for_doc_string and tok not in doc_string_ignore_tok :
            wait_for_doc_string = False
        if call_stack == -1 and tok == NAME and value in ("def", "class") :
            in_def              = True
        elif tok == OP and value == "(" and funcname :
                message_lineno = lineno
                call_stack    += 1
        elif tok == OP and value == ":" :
            in_def              = False
            wait_for_doc_string = add_doc_strings
            continue
        elif call_stack == -1 and tok == COMMENT :
            # Strip the comment token from the line
            value = value [1:].strip ()
            if (   in_translator_comments
               and translator_comments [-1] [0] == lineno - 1
               ) :
                # We're already inside a translator comment, continue appending
                translator_comments.append ((lineno, value))
                continue
            # If execution reaches this point, let's see if comment line
            # starts with one of the comment tags
            for comment_tag in comment_tags :
                if value.startswith (comment_tag) :
                    in_translator_comments = True
                    translator_comments.append ((lineno, value))
                    break
        elif wait_for_doc_string and tok == STRING :
            ### found a doc_string
            msg = TFL.normalized_indent \
                (TFL.I18N.safe_eval (value, encoding)).strip ()
            yield (lineno, funcname, msg, [], None)
            wait_for_doc_string = False
        elif funcname and call_stack == 0 :
            if tok == OP and value == ")" :
                if buf :
                    messages.append ("".join (buf).strip ())
                    del buf [:]
                else:
                    messages.append (None)

                if len (messages) > 1 :
                    messages = tuple (messages)
                else:
                    messages = messages [0]
                # Comments don't apply unless they immediately preceed the
                # message
                if (   translator_comments
                   and translator_comments [-1][0] < message_lineno - 1
                   ) :
                    translator_comments = []

                yield \
                    ( message_lineno
                    , funcname
                    , messages
                    , [comment [1] for comment in translator_comments]
                    , None
                    )
                funcname = lineno = message_lineno = None
                call_stack                         = -1
                messages                           = []
                translator_comments                = []
                in_translator_comments             = False
            elif tok == STRING :
                # Unwrap quotes in a safe manner, maintaining the string's
                # encoding
                # https://sourceforge.net/tracker/?func=detail&atid=355470&
                # aid=617979&group_id=5470
                value = TFL.I18N.safe_eval (value, encoding)
                if isinstance (value, bytes) :
                    value = value.decode (encoding)
                buf.append (value)
            elif tok == OP and value == "," :
                if buf :
                    messages.append ("".join (buf).strip ())
                    del buf [:]
                else:
                    messages.append (None)
                if translator_comments :
                    # We have translator comments, and since we're on a
                    # comma(,) user is allowed to break into a new line
                    # Let's increase the last comment's lineno in order
                    # for the comment to still be a valid one
                    old_lineno, old_comment = translator_comments.pop ()
                    translator_comments.append ((old_lineno + 1, old_comment))
        elif call_stack > 0 and tok == OP and value == ")" :
            call_stack -= 1
        elif funcname and call_stack == -1 :
            funcname = None
        elif tok == NAME and value in keywords :
            funcname = value
# end def Python

if __name__ != "__main__" :
    TFL.Babel._Export_Module ()
### __END__ TFL.Babel.Extractor
