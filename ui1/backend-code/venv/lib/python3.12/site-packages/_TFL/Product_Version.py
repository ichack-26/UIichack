# -*- coding: utf-8 -*-
# Copyright (C) 1999-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Product_Version
#
# Purpose
#    Model product version of form `major.minor.patchlevel'
#
# Revision Dates
#    25-Oct-1999 (CT) Creation
#    27-Oct-1999 (CT) `productnick' added
#    27-Oct-1999 (CT) `ivn' put in here (was in TTA_Product_Version)
#     2-Nov-1999 (CT) Comment added
#    18-Nov-1999 (CT) Don't allow integers as parameters for `IV_Number's
#    18-Nov-1999 (CT) Add `producer' info to `product_info'
#    19-Nov-1999 (CT) `producer' consistently handled as list
#    19-Nov-1999 (CT) `/' appended to TeX macros
#    19-Nov-1999 (CT) Use `consumer'  info in `product_info'
#    22-Nov-1999 (MG) Blank after `;' removed joining the extentions
#     8-Feb-2000 (CT) Don't apply `int' to `patchlevel'
#    17-Feb-2000 (CT) `plugins' added
#    19-May-2000 (MG) Definition of tool name added `_tex_macros'
#    16-Jan-2002 (CT) Allow non-IV_Number instances in `** kw` of `__init__`
#    15-Apr-2002 (CT) Raise `TypeError` instead of string exception
#                     (__setattr__)
#    23-Oct-2002 (CT) `_product_info` changed to show compatibility range
#    10-Mar-2003 (CT) Moved to package `TOM`
#    24-Mar-2003 (CT) `Toolbasename` added to `_tex_macros`
#    26-Mar-2003 (CT) Derived from `TFL.Meta.Object`
#    16-Sep-2004 (CT) Usage of `string` module removed (use `str` methods
#                     instead)
#    16-Sep-2004 (CT) `Lic_Comp` added
#    16-Sep-2004 (CT) `lic_comps` and `_setup_lic_comps` added
#    16-Sep-2004 (CT) `_product_info` changed to display `lic_comps`, if any
#     4-Oct-2004 (CT) `add_plugin` added (factored in here)
#     9-Aug-2006 (CT) `__hash__` changed to return `hash (id (self))`
#                     instead of `id self`
#    24-Aug-2008 (CT) Factored from `TOM.Product_Version`
#    18-Dec-2009 (CT) `author`, `copyright_start`, and `tuple` added
#    30-Jun-2010 (CT) `id` added
#    19-Apr-2020 (CT)  Use "``" for doc strings, not "`'"
#    23-Apr-2020 (CT)  Use `importlib.import_module`, not `TFL.import_module`
#    ««revision-date»»···
#--

from   _TFL                  import TFL

import _TFL._Meta.Object

from   _TFL.IV_Number        import *
from   _TFL.pyk              import pyk

from   importlib              import import_module

import sys
import time

class Lic_Comp (TFL.Meta.Object) :
    """Model a licensed software component used."""

    def __init__ (self, name, version, license) :
        self.name    = name
        self.version = version
        self.license = license
    # end def __init__

    def __repr__ (self) :
        return """%s ("%s", %r, %s)""" % \
            (self.__class__.__name__, self.name, self.version, self.license)
    # end def __repr__

    def __str__ (self) :
        if self.version is None :
            return self.name
        else :
            return "%s %s" % (self.name, self.version)
    # end def __str__

# end class Lic_Comp

class _TFL_Product_Version_ (TFL.Meta.Object) :
    """Models the version of a software product."""

    def __init__ ( self
                 , productid, productnick, productdesc
                 , date, major, minor, patchlevel
                 , author, copyright_start
                 , lic_comps       = ()
                 , ** kw
                 ) :
        self.productid       = productid.strip   ()
        self.productnick     = productnick.strip ()
        self.productdesc     = productdesc.strip ()
        self.date            = date.strip        ()
        self.major           = int (major)
        self.minor           = int (minor)
        release              = "%s.%s" % (self.major, self.minor)
        if patchlevel :
            self.patchlevel  = int (patchlevel)
            self.version     = "%s.%s" % (release, self.patchlevel)
        else :
            self.patchlevel  = 0
            self.version     = release
        self.author          = author = author.strip ()
        self.copyright_start = copyright_start
        self.copyright       = self._copyright (author, copyright_start)
        self.message         = "Version %s, %s" % (self.version, self.date)
        self.tuple           = (self.major, self.minor, self.patchlevel)
        self.id              = (self.productnick, self.tuple)
        self.lic_comps       = list (lic_comps)
        self.plugins         = []
        self._setup_lic_comps  ()
        self._setup_ivn        (kw)
        maxl         = max ([len (k) for k in kw] + [20])
        self._format = "%%-%ds : %%s" % (maxl, )
        self._post_init (kw)
        ### this must be the last statement of `self.__init__`
        ### (`__setattr__` relies on it!!!)
        self.ivn = kw
    # end def __init__

    def add_plugin (self, p) :
        self.plugins.append (p)
    # end def add_plugin

    def as_c_macros (self) :
        """Return c-macros for definition of product version and date."""
        return "\n".join (self._c_macros ())
    # end def as_c_macros

    def as_tex_macros (self) :
        """Return TeX-macros for definition of product version and date."""
        return "\n".join (self._tex_macros ())
    # end def as_tex_macros

    def product_info (self) :
        """Return complete information about product version."""
        info = self._product_info ()
        return "\n".join          (info)
    # end def product_info

    def print_infos (self, cmd) :
        """Provide information requested by `cmd` (which must be an object
           returned by `command_spec`).
        """
        if cmd.all or cmd.c_macro :
            print (self.as_c_macros   ())
        if cmd.all or cmd.product_info :
            print (self.product_info  ())
        if cmd.all or cmd.tex_macro :
            print (self.as_tex_macros ())
    # end def print_infos

    def _c_macros (self) :
        result = []
        add    = result.append
        add ( """#define %s %s """ % (self._toolname (), self.productid))
        add ( """#define %s_VERSION         "%s" """
            % (self.productid.upper (), self.version)
            )
        add ( """#define %s_DATE            "%s" """
            % (self.productid.upper (), self.date)
            )
        for k in sorted (self.ivn.keys ()) :
            v = self.ivn [k]
            add ( """#define %s_%-15s "%s" """
                % (self.productid.upper (), k.upper (), v.program_version)
                )
        return result
    # end def _c_macros

    def _copyright (self, author, copyright_start) :
        year  = time.strftime ("%Y", time.localtime (time.time ()))
        range = year
        if copyright_start :
            start = str (copyright_start).strip ()
            if year != start :
                range = "%s-%s" % (start, year)
        return "Copyright (C) %s %s. All rights reserved." % (range, author)
    # end def _copyright

    def _post_init (self, kw) :
        self.productname = self.productid
    # end def _post_init

    def _product_info (self) :
        result = []
        add    = result.append
        format = self._format
        add (format % ("Product", self.productname))
        add (format % ("Date",    self.date))
        add (format % ("Release", self.version))
        for k in sorted (self.ivn) :
            v = self.ivn [k]
            add ( (format + " (produced by %s)")
                % (k, "%3d" % v.program_version, ", ".join (v.producer))
                )
            l = result [-1].find (" (produced by")
            if v.consumer :
                add ("%s (consumed by %s)" % (" " * l, ", ".join (v.consumer)))
                if self.productname in v.consumer :
                    if v.comp_min == v.comp_max :
                        r = "version %s" % (v.comp_max, )
                    else :
                        r = "versions %s to %s" % (v.comp_min, v.comp_max)
                    add (" " * l + " (%s accepts %s)" % (self.productname, r))
        if self.lic_comps :
            lc = self.lic_comps [0]
            add (format % ("Licensed Components", lc))
            indent = " " * (result [-1].find (":") + 2)
            for lc in self.lic_comps [1:] :
                add ("%s%s" % (indent, lc))
        return result
    # end def _product_info

    def _setup_ivn (self, kw) :
        for k, v in list (pyk.iteritems (kw)) :
            if not isinstance (v, IV_Number) :
                del kw [k]
            setattr (self, k, v)
    # end def _setup_ivn

    def _setup_lic_comps (self) :
        pns_name = self.productnick
        pkg_name = "_%s" % pns_name
        pkg      = sys.modules.get (pkg_name)
        if pkg :
            pns  = getattr (pkg, pns_name)
            try :
                lp_module = import_module ("%s.Lic_Comps" % pkg_name)
            except ImportError :
                pass
            else :
                self.lic_comps.extend (getattr (lp_module, "list"))
    # end def _setup_lic_comps

    def _tex_macros (self) :
        result  = []
        variant = self.variant
        if variant :
            variant = "-" + variant
        add = result.append
        add (r"""\def\Toolname/{%s}"""     % self.productname)
        add (r"""\def\Tooldate/{%s}"""     % self.date)
        add (r"""\def\Toolversion/{%s}"""  % self.version)
        for k in sorted (self.ivn) :
            v = self.ivn [k]
            k = k.replace ("_", "").upper ()
            add (r"""\def\Tool%s/{%s}""" % (k, v.program_version))
        return result
    # end def _tex_macros

    def _toolname (self, name = None) :
        """Returns the name of the "toolname" macro for usage in
           `_c_macros` and `_startup_macros`.
        """
        return "TOOL_NAME"
    # end def _toolname

    def __hash__ (self) :
        return hash (id (self))
    # end def __hash__

    def __repr__ (self) :
        return """%s ("%s", "%s", %s, %s, %s)""" % \
            ( self.__class__.__name__, self.productid, self.date
            , self.major, self.minor, self.patchlevel
            )
    # end def __repr__

    def __setattr__ (self, name, value) :
        """Prevent the changing of attributes other than entries of `ivn`.

           Once an attribute is set, it cannot be changed to another value.
        """
        if not hasattr (self, "ivn") :
            ### object still under construction -- don't prevent attribute
            ### settings or changes
            self.__dict__ [name] = value
            return
        ### object fully constructed -- do what must be done
        if name in self.ivn :
            self.ivn [name].external_version = value
        elif name in self.__dict__ :
            raise TypeError \
                ( "Attribute %s is readonly. Cannot change value from %s to %s"
                % (name, getattr (self, name), value)
                )
        else :
            self.__dict__ [name] = value
    # end def __setattr__

    def __str__ (self) :
        return self.message
    # end def __str__

Product_Version = _TFL_Product_Version_ # end class

if __name__ != "__main__" :
    TFL._Export ("Product_Version", "Lic_Comp")
### __END__ TFL.Product_Version
