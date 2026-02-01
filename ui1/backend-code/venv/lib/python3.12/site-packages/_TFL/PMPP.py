# -*- coding: utf-8 -*-
# Copyright (C) 2005-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.PMPP
#
# Purpose
#    Poor-Man's Pre-Processor
#
# Revision Dates
#     6-Feb-2005 (CT) Creation
#    25-Mar-2005 (MG) Import of `Filename` changed
#    ««revision-date»»···
#--

from   _TFL              import TFL
from   _TFL.pyk          import pyk

import _TFL._Meta.Object

from   _TFL.Filename     import Filename
from   _TFL.Regexp       import Regexp, re

class PMPP (TFL.Meta.Object) :
    """Poor-Man's Pre-Processor: rewrite a file according to preprocessor
       comments.

       >>> pp     = PMPP ("TESTTAG")
       >>> source = '''Line before start-tag
       ...    Indented line before start-tag
       ...    # _TESTTAG_LINE_ single tagged line
       ...    Another indented line before start-tag
       ...    # _TESTTAG_START_
       ...    # First tagged line
       ...    #     Second tagged line
       ...    # Third tagged line
       ...    # _TESTTAG_ELSE_
       ...    # First line to be removed by PMPP
       ...    #     Second line to be removed by PMPP
       ...    # _TESTTAG_END_
       ...    Line after end-tag
       ... Last line
       ... '''
       >>> for l in pp (pyk.StringIO (source)) :
       ...     print (l, end = "")
       ...
       Line before start-tag
          Indented line before start-tag
          single tagged line
          Another indented line before start-tag
          First tagged line
              Second tagged line
          Third tagged line
          Line after end-tag
       Last line

    """

    comment_pat   = Regexp (r"\s+ (?P<comment> \# \s*)", re.X)
    pattern_pat   = r"^(?P<indent> \s*) \# \s* _%s_%s_ \s*"

    def __init__ (self, tag) :
        pattern_pat   = self.pattern_pat
        self.head_tag = Regexp (pattern_pat % (tag, "START"), re.X)
        self.else_tag = Regexp (pattern_pat % (tag, "ELSE"),  re.X)
        self.tail_tag = Regexp (pattern_pat % (tag, "END"),   re.X)
        self.line_tag = Regexp (pattern_pat % (tag, "LINE"),  re.X)
    # end def __init__

    def rewrite (self, fname, target_dir) :
        target = Filename (target_dir, fname)
        f      = open     (fname,  "r")
        o      = open     (target, "w")
        print ("Processing %s" % (target, ))
        for l in self (f) :
            o.write (l)
    # end def rewrite

    def __call__ (self, source) :
        head_tag    = self.head_tag
        else_tag    = self.else_tag
        tail_tag    = self.tail_tag
        line_tag    = self.line_tag
        comment_pat = self.comment_pat
        comment     = "# "
        for l in source :
            if not head_tag.match (l) :
                if line_tag.match (l) :
                    ### return text without line-tag
                    yield line_tag.sub (r"\g<indent>", l, 1)
                else :
                    ### return untagged text unchanged
                    yield l
            else :
                l = next (source)
                if comment_pat.match (l) :
                    comment = comment_pat.comment
                while not (else_tag.match (l) or tail_tag.match (l)) :
                    ### return text between start-tag and else- or tail-tag
                    ### without the leading comment
                    yield l.replace (comment, "", 1)
                    l = next (source)
                if else_tag.match (l) :
                    ### skip over text between else- and tail-tag
                    while not tail_tag.match (l) :
                        l = next (source)
    # end def __call__

# end class PMPP

"""
Usage examples:
    Demoize  = PMPP ("DEMOVERSION")
    makedemo = Demoize.rewrite

    TMCoize  = PMPP ("TMCVERSION")
"""

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.PMPP
