# -*- coding: utf-8 -*-
# Copyright (C) 2015-2020 Christian Tanzer All rights reserved
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
#    TFL.sphinx_autodoc
#
# Purpose
#    Extension of Sphinx autodoc extension
#
# Revision Dates
#    22-Sep-2015 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL                     import TFL

from   _TFL.Decorator           import eval_function_body
from   _TFL.pyk                 import pyk
from   _TFL                     import sos
from   _TFL._Meta.Once_Property import Once_Property

import _TFL._Meta.M_Class
import _TFL._Meta.Object

import sphinx.ext.autodoc
from   sphinx.ext               import autodoc

class M_Class_Documenter (TFL.Meta.M_Class) :
    """Meta class for Class_Documenter"""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        for c in cls._applies_to_classes :
            setattr (c, cls._cls_documenter_name, cls)
        for m in dct.get ("_applies_to_metas", ()) :
            cls._M_Map.append ((m, cls))
    # end def __init__

# end class M_Class_Documenter

class TFL_Class_Documenter \
        (autodoc.ClassDocumenter, metaclass = M_Class_Documenter) :
    """Base class for specialized documenter classes for TFL and
       Package_Namespaces based on it.
    """

    _real_name             = "Class_Documenter"

    priority               = autodoc.ClassDocumenter.priority + 50

    _applies_to_classes    = ()
    _applies_to_metas      = ()
    _cls_documenter_name   = "TFL_Sphinx_autodoc_Class_Documenter"
    _M_Map                 = []

    def filter_members (self, * args, ** kw) :
        result = orig = self.__super.filter_members (* args, ** kw)
        keep   = self._document_member_p
        result = [r for r in result if  keep (* r)]
        return result
    # end def filter_members

    def get_doc (self, * args, ** kw) :
        result = self.__super.get_doc (* args, ** kw)
        extra  = self._extra_doc      ()
        if extra :
            result.extend (extra)
        return result
    # end def get_doc

    def import_object (self, * args, ** kw) :
        result = self.__super.import_object (* args, ** kw)
        this   = self.object
        if this.__module__ == self.modname :
            cls_documenter = getattr (this, self._cls_documenter_name, None)
            if cls_documenter is None :
                for m, cd in reversed (self._M_Map) :
                    if isinstance (this, m) :
                        cls_documenter = cd
                        break
            if cls_documenter is not None :
                self.__class__ = cls_documenter
                self._after_import_object ()
            return result
    # end def import_object

    def _after_import_object (self) :
        "Redefine if class documenter needs to do setup right after import."
    # end def _after_import_object

    def _document_member_p (self, name, member, isattr) :
        return True
    # end def _document_member_p

    def _extra_doc (self) :
        "Redefine if class documenter wants to add documentation."
        return ()
    # end def _extra_doc

Class_Documenter = TFL_Class_Documenter # end class

def setup (app):
    app.add_autodocumenter (Class_Documenter)
    return {'version': "0.7", 'parallel_read_safe': True}
# end def setup

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.sphinx_autodoc
