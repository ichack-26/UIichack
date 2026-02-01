# -*- coding: utf-8 -*-
# Copyright (C) 2001-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Package_Namespace
#
# Purpose
#    Implement a namespace for python packages providing direct access to
#    classes and functions implemented in the modules of the package
#
# Revision Dates
#     7-May-2001 (CT)  Creation
#     2-Jul-2001 (CT)  Docstring extended
#     2-Jul-2001 (CT)  Use `` instead of `' to quote inside docstrings and
#                      comments
#    27-Jul-2001 (CT)  `Import` changed to support `*`
#    30-Jul-2001 (CT)  `*` import corrected
#    30-Jul-2001 (CT)  `_import_1` and `_import_name` factored
#    31-Jul-2001 (CT)  `From_Import` added (and `_import_symbols` factored)
#     2-Aug-2001 (CT)  `_Module_Space` added and used to separate namespace
#                      for modules provided by the package from the namespace
#                      for classes and functions provided by the package
#     3-Aug-2001 (CT)  `Import_Module` added
#    16-Aug-2001 (CT)  `_import_1` fixed to correctly check for name clashes
#    19-Aug-2001 (CT)  `_import_names` changed to raise `ImportError` if
#                      necessary
#    19-Aug-2001 (CT)  `__getattr__` raises `AttributeError` instead of
#                      `ImportError` for `__*__`
#    22-Aug-2001 (CT)  `transitive` added
#    20-Sep-2001 (MG)  `_import_names`: import name they are defined in the
#                      modul to be imported or if `getmodule` returns `None`
#    20-Sep-2001 (CT)  Change of MG revoked
#    20-Sep-2001 (CT)  Don't *-import names with leading underscores
#     3-Nov-2001 (MG)  import `TFL.Caller` instead of `Caller`
#     8-Nov-2001 (CT)  `Essence` added to handle TOM.Class_Proxy correctly
#    13-Nov-2001 (CT)  `_import_symbols` corrected to handle empty `symbols`
#                      correctly
#    13-Nov-2001 (CT)  Unncessary restriction of nested packages removed
#     5-Dec-2001 (MG)  Special code for `Proxy_Type` changed
#    20-Feb-2002 (CT)  `_Export` and `XXX PPP` comments added
#    21-Feb-2002 (CT)  `_Module_Space._load` factored
#    22-Feb-2002 (CT)  `_leading_underscores` added and used to remove leading
#                      underscores from `Package_Namespace.__name`
#    22-Feb-2002 (CT)  `_debug` added and used to guard `XXX PPP` prints
#    25-Feb-2002 (CT)  `_complain_implicit` factored
#    25-Feb-2002 (CT)  Kludge to add `FOO` alias to sys.modules for package
#                      `_FOO` (otherwise binary databases with old-style
#                      packages don't load <sigh>)
#    26-Feb-2002 (CT)  `_debug` set to `__debug__`
#    26-Feb-2002 (CT)  `_complain_implicit` changed to provide more useful
#                      output (included addition of `last_caller`)
#    27-Feb-2002 (CT)  Argument `module_name` removed from `_Export` (get that
#                      from `caller_globals`)
#    12-Mar-2002 (CT)  `_Export_Module` added
#    12-Mar-2002 (CT)  Use `TFL.Module.names_of` instead of half-broken
#                      `inspect.getmodule`
#    15-Mar-2002 (CT)  `Import` renamed to `__Import`
#                      `_import_symbols` renamed to `__import_symbols`
#    15-Mar-2002 (CT)  `From_Import` and `Import_Module` removed
#    18-Mar-2002 (MG)  `_Add` added
#    18-Mar-2002 (CT)  `_complain_implicit` changed to write new syntax
#    28-Mar-2002 (CT)  Last remnants of implicit imports removed
#     3-Sep-2002 (CT)  Comment added to `_Module_Space._load` to explain why
#                      `__import__` is used in the particular way it is
#     8-Oct-2002 (CT)  Pass `None` as fourth argument to `__import__` to avoid
#                      annoying Gordon McMillan
#    11-Oct-2002 (CT)  Change of `8-Oct-2002` backed out because it doesn't
#                      work with McMillan
#     4-Feb-2003 (CT)  `Derived_Package_Namespace` added
#     8-Apr-2003 (CT)  `_leading_underscores` changed to consider `._` too
#     8-Apr-2003 (CT)  `qname` added
#     8-Apr-2003 (CT)  `pname` added
#     8-Apr-2003 (CT)  Compatibility kludge of putting `Package_Namespace`
#                      into `sys.modules` removed (it was too smelly)
#    28-Jul-2003 (CT)  `_Reload` added
#     1-Aug-2003 (CT)  `_Reload` changed to reload in same sequence as
#                      original import
#    12-Sep-2003 (CT)  `_Reload` changed to clear the damned `linecache`
#    20-Nov-2003 (CT)  `_Export_Module` changed to take `mod` from `kw` if
#                      there
#    16-Jun-2004 (CT)  `_Module_Space._load` changed to
#                      - use `sys.modules` instead of `__import__`
#                      - accept `q_name` as argument
#    16-Jun-2004 (CT)  `Package_Namespace._Load_Module` factored
#     5-Jul-2004 (CT)  `__name__` set for `Package_Namespace` instances to
#                      make them more similar to modules
#     4-Aug-2004 (MG)  `Package_Namespace._Import_Module` added
#    28-Sep-2004 (CT)  Use `isinstance` instead of type comparison
#    23-Oct-2004 (CT)  `_check_clashes` added
#    28-Oct-2004 (CT)  `_Export_Module` changed to honor `_check_clashes`
#    10-Jan-2005 (CT)  `__repr__` changed to not future warn about negative
#                      values of `id`
#    14-Jan-2005 (CT)  `_DPN_Auto_Importer_` added and called by
#                      `Derived_Package_Namespace`
#    20-Jan-2005 (CT)  `_DPN_Auto_Importer_.__call__` changed to ignore
#                      transitive import errors
#    24-Jan-2005 (CT)  Change of `20-Jan-2005` fixed
#    24-Jan-2005 (CT)  `_Import_Module` changed to return the imported module
#                      (and rest-args removed)
#    10-Feb-2005 (CT)  `_Export` changed to streamline `*` handling
#    10-Feb-2005 (CT)  More documentation added
#    24-Mar-2005 (CT)  Dependencies on non-standard-lib modules removed
#                      - Use `re` instead of `Regexp`
#                      - Unused import of `caller_info` removed
#                      - Import of `caller_globals` replaced by home-grown code
#    30-Mar-2005 (CED) `_name`, `_qname` added to `_Module_Space`
#    26-Apr-2006 (PGO) [rup18983] renamed classes with leading underscore
#    28-Jul-2006 (PGO) Replaced `_DPN_Auto_Importer_` with TFL.DPN_Importer
#    31-Jul-2006 (PGO) `DPN_Importer.register` introduced
#     7-Nov-2006 (PGO) Reloading now also works with `_Add`
#     3-Feb-2009 (CT)  Style improvements
#     6-Feb-2009 (CT)  Documentation improved
#    11-Nov-2009 (CT)  Use `print` as function, not statement (3-compatibility)
#    23-Nov-2009 (CT)  `Package_Namespace.__init__`: order of arguments changed
#    14-Jan-2010 (CT)  `_Outer` added (and methods sorted alphabetically)
#    16-Jun-2010 (CT)  s/print/pyk.fprint/
#    30-Aug-2010 (CT) `_import_names` changed to check against `basestring`
#     8-Aug-2012 (CT) Improve names of name-attributes
#     8-Aug-2012 (CT) Add `__doc__` to `Package_Namespace`
#    11-Aug-2012 (MG) Add support for import callbacks
#    11-Aug-2012 (MG) Support args/kw for import callback
#    11-Aug-2012 (MG) Fix import callback
#    23-Sep-2012 (MG) Fix import callbacks again
#     9-Oct-2012 (CT) Add `c_scope` to `Package_Namespace.__init__` call
#     9-Oct-2012 (CT) Add `_desc_` to `Package_Namespace.__init__`
#     6-Dec-2012 (CT) Fix `_Add_Import_Callback`
#     6-Dec-2012 (CT) Change  `_run_import_callback` to `classmethod`
#    15-Jun-2013 (CT) Add `lazy_resolvers`; factor `_args_from_kw`
#     4-Aug-2013 (CT) Add `_Derived_Module_` to properly support
#                     `_Export_Module` for `Derived_Package_Namespace`
#    13-Apr-2015 (CT) Change `_Add_Import_Callback` to be useable as decorator
#    12-Aug-2015 (CT) Add `_Import_All`, `__file__`
#    13-Aug-2015 (CT) Change `_Import_All` to ignore names starting with "__"
#    16-Aug-2015 (CT) Add `__PNS__`, `GET`
#    17-Aug-2015 (CT) Factor property `MODULES`
#    17-Aug-2015 (CT) Add `__is_PNS__` to modules defining Package_Namespace
#                     instances
#    18-Aug-2015 (CT) Add `self._Export` to `__init__` for proper bootstrap
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    13-Nov-2015 (CT) Restrict `__getattr__` change to `__wrapped__`
#                     [Otherwise, accessing `__PNS__` fails]
#    10-Oct-2016 (CT) Add `__version__`
#    11-Oct-2016 (CT) Hide `import` behind `#` in `__doc__`
#    12-Oct-2016 (CT) Change `_Import_All` to skip `setup.py`
#    22-Apr-2020 (CT) Add and use `DPN_Import_Finder`, `importlib`
#                     + Add `DPN_Loader`
#                     + Use `_add_module_getattr`, remove `_Derived_Module_`
#                     + Factor `_Finish_Module`
#    ««revision-date»»···
#--

from   collections import defaultdict
from   importlib   import abc, import_module, machinery, reload, util

import logging
import re
import sys

def _caller_globals (depth = 1) :
    return sys._getframe (depth).f_back.f_globals
# end def _caller_globals

class _Module_Space_ :

    def __init__ (self, bname, module_name, qname) :
        self._bname       = bname
        self._module_name = module_name
        self._qname       = self.__name__ = qname
    # end def __init__

    def _load (self, q_name, module_name) :
        module = sys.modules [q_name]
        setattr (self, module_name, module)
        return module
    # end def _load

# end class _Module_Space_

class _DPN_Import_Finder_ (abc.MetaPathFinder) :
    """Meta path finder for inherited modules of Derived_Package_Namespace.

    For documentation, see:

    https://docs.python.org/3/reference/import.html
    https://docs.python.org/3/library/importlib.html
    https://www.python.org/dev/peps/pep-0302/
    https://www.python.org/dev/peps/pep-0451/
    """

    def __init__ (self) :
        self._dpn_map = {}
    # end def __init__

    def find_spec (self, fullname, path, target = None) :
        """Find the `ModuleSpec` for module `fullname` in `path`."""
        result  = None
        if path :
            try :
                m_name, dpn, pns_chain = self._dpn_map [path [0]]
            except KeyError :
                pass
            else :
                for pns in pns_chain :
                    cand    = fullname.replace (m_name, pns, 1)
                    p_spec  = util.find_spec   (cand)
                    if p_spec is not None :
                        break
                if p_spec is not None :
                    result = machinery.ModuleSpec \
                        ( fullname, _DPN_Loader_ ()
                        , origin        = p_spec.origin
                        , loader_state  = dict
                            (dpn = dpn, m_name = m_name, p_spec = p_spec)
                        , is_package    =
                            p_spec.submodule_search_locations is not None
                        )
                    result.cached       = None
                    result.has_location = False
                    result.submodule_search_locations \
                                        = p_spec.submodule_search_locations
        return result
    # end def find_spec

    def register (self, dpn, parent) :
        """Register Derived_Package_Namespace `dpn`."""
        m_name     = dpn._._module_name
        dpn_module = sys.modules [m_name]
        if not hasattr (dpn_module, "__path__") :
            return ### nothing to do: non-package Derived_Package_Namespace
        def _parent_names (p) :
            while p :
                yield p._._module_name
                p = getattr (parent, "_parent", None)
        path    = dpn_module.__path__ [0]
        parents = tuple (_parent_names (parent))
        self._dpn_map [path] = (m_name, dpn, parents)
    # end def register

DPN_Import_Finder = _DPN_Import_Finder_ () # end class _DPN_Import_Finder_

class _DPN_Loader_ (abc.Loader) :
    """Loader for inherited modules of Derived_Package_Namespace."""

    def create_module (self, spec) :
        """Return the module object to use for importing."""
        dpn     = spec.loader_state ["dpn"]
        p_spec  = spec.loader_state ["p_spec"]
        parent  = import_module (p_spec.name)
        q_name  = spec.name
        result  = self._new_module (spec, parent.__doc__, p_spec.origin)
        sys.modules [q_name]    = result
        dpn._add_module_getattr (result, parent)
        dpn._Finish_Module      (q_name, result)
        dpn._._load             (q_name, q_name.split (".") [-1])
        return result
    # end def create_module

    def exec_module (self, module) :
        """Execute the module in its own namespace when imported or reloaded."""
        pass ### nothing to do here
    # end def exec_module

    def _new_module (self, spec, doc, origin) :
        result              = type (sys) (spec.name, doc)
        result.__file__     = origin
        result.__loader__   = self
        result.__package__  = spec.parent
        result.__path__     = spec.submodule_search_locations
        result.__spec__     = spec
        return result
    # end def _new_module

# end class _DPN_Loader_

class Package_Namespace (object) :
    """Namespace that provides direct access to classes and
       functions implemented in the modules of a Python package.

       You can access the modules of the package with the attribute ``_``.

       .. attribute:: _

         Allows access to the modules of the package namespace.

    """

    _leading_underscores = re.compile (r"(\.|^)_+")
    _check_clashes       = True

    _Import_Callback_Map = defaultdict (lambda : defaultdict (list))
    __PKG__              = None

    __Table              = {}

    def __init__ (self, * lazy_resolvers, ** kw) :
        c_scope, module_name, name = self._args_from_kw (kw)
        qname                      = self._leading_underscores.sub (r"\1", name)
        bname                      = qname.split (".") [-1]
        self.__lazy_resolvers      = list (lazy_resolvers)
        self.__bname               = bname
        self.__qname               = self.__name__ = qname
        self.__module_name         = module_name
        self.__module_space        = self._ = _Module_Space_ \
            (bname, module_name, qname)
        self.__modules             = {}
        self.__seen                = {}
        self.__reload              = 0
        self._Outer                = None
        self.__doc__               = c_scope.get ("__doc__",     str (self))
        self._desc_                = c_scope.get ("_desc_",      None)
        self.__file__              = c_scope.get ("__file__",    None)
        p_name                     = c_scope.get ("__package__", None)
        if p_name :
            Table                  = self.__Table
            for k in p_name, qname, ".".join ((p_name, "__init__")) :
                Table [k]          = self
        c_scope ["__PNS__"]        = self
        c_scope ["__is_PNS__"]     = True
        self.__version__           = c_scope.get ("__version__", None)
        if qname == "TFL" :
            ### Normally, the `_Export` would happen in the
            ### `if __name__ != "__main__" ` stanza at the bottom
            ### of the module but that would require a circular
            ### import of `TFL` from `_TFL`
            self._Export ("*")
        else :
            self._Load_Module (c_scope)
    # end def __init__

    @classmethod
    def GET (cls, name) :
        """Return the Package_Namespace instance that the module, package, or
           package namespace with `name` belongs to, if any.
        """
        return cls.__Table.get (name)
    # end def GET

    @property
    def MODULES (self) :
        """List of all modules in Package_Namespace, in sequence of import"""
        mps = sorted (self.__modules.values (), key = lambda x : x [1])
        return [m for (m, p) in mps]
    # end def MODULES

    def _Add (self, ** kw) :
        """Add elements of `kw` to Package_Namespace `self`."""
        module_name, mod = self._Load_Module (_caller_globals ())
        check_clashes    = self._check_clashes and not self.__reload
        self._Cache_Module (module_name, mod)
        for s, p in kw.items () :
            self._import_1 (mod, s, s, p, self.__dict__, check_clashes)
    # end def _Add

    @classmethod
    def _Add_Import_Callback (cls, module_name, callback = None, ** kw) :
        if callback is None :
            return lambda cb : cls._Add_Import_Callback (module_name, cb, ** kw)
        args   = kw.pop ("args", ())
        module = sys.modules.get (module_name)
        if module is not None :
            ### run the callbacks immediately
            cls._run_import_callback (module, ((callback, args, kw), ))
        else :
            package = "__main__"
            if "." in module_name :
                package, module_name = module_name.rsplit (".", 1)
            cls._Import_Callback_Map [package] [module_name].append \
                ((callback, args, kw))
    # end def _Add_Import_Callback

    def _Add_Lazy_Resolver (self, * lazy_resolvers) :
        """Add the callables in `lazy_resolvers` to Package_Namespace `self`."""
        self.__lazy_resolvers.extend (lazy_resolvers)
    # end def _Add_Lazy_Resolver

    def _args_from_kw (self, kw) :
        c_scope     = kw.pop ("c_scope",     None) or _caller_globals (2)
        module_name = kw.pop ("module_name", None) or c_scope ["__name__"]
        if module_name.endswith (".__init__") :
            ### this only happens on explicit import of `__init__`
            ### `don't do that`, but protect against it anyway
            module_name = module_name [:-9]
        name        = kw.pop ("name",        None) or module_name
        if kw :
            raise TypeError \
                ( "%s `%s` called with unknwon arguments: (%s)"
                % ( self.__class__.__name__, name, ", ".join
                      ("%s = %r" % (k, v) for k, v in sorted (kw.items ()))
                  )
                )
        return c_scope, module_name, name
    # end def _args_from_kw

    def _Cache_Module (self, module_name, mod) :
        if not module_name in self.__modules :
            p = len (self.__modules)
        else :
            m, p = self.__modules [module_name]
        self.__modules [module_name] = (mod, p)
    # end def _Cache_Module

    def _Export (self, * symbols, ** kw) :
        """To be called by modules of `Package_Namespace` to inject their
           symbols into the package namespace `self`.
        """
        result         = {}
        caller_globals = _caller_globals ()
        mod            = kw.pop ("mod", None)
        assert not kw
        if mod is None :
            module_name, mod = self._Load_Module (caller_globals)
        else :
            module_name      = caller_globals ["__name__"].split (".") [-1]
        primary        = getattr (mod, module_name, None)
        check_clashes  = self._check_clashes and not self.__reload
        if primary is not None :
            result [module_name] = primary
        if symbols [0] == "*" :
            all_symbols = getattr (mod, "__all__", ())
            if all_symbols :
                self._import_names (mod, all_symbols, result, check_clashes)
            else :
                from _TFL import Module
                for s in Module.names_of (mod) :
                    if not s.startswith ("_") :
                        p = getattr (mod, s)
                        self._import_1 (mod, s, s, p, result, check_clashes)
            symbols = symbols [1:]
        if symbols :
            self._import_names (mod, symbols, result, check_clashes)
        mod.__PNS_Export__ = sorted (result)
        self.__dict__.update        (result)
        self._Finish_Module         (module_name, mod)
    # end def _Export

    def _Export_Module (self) :
        """To be called by modules to inject themselves into the package
           namespace `self`.
        """
        module_name, mod = self._Load_Module (_caller_globals ())
        if __debug__ :
            old = self.__dict__.get (module_name, mod)
            check_clashes = self._check_clashes and not self.__reload
            if old is not mod and check_clashes :
                raise ImportError \
                    ( "ambiguous name %s refers to %s and %s"
                    % (module_name, mod, old)
                    )
        self.__dict__  [module_name] = self._exported_module (module_name, mod)
        self._Finish_Module (module_name, mod)
    # end def _Export_Module

    def _Finish_Module (self, module_name, mod) :
        self._Cache_Module        (module_name, mod)
        self._Register_Module     (mod)
        self._run_import_callback (mod)
    # end def _Finish_Module

    def _Import_Module (self, name) :
        """Import module `name` from this package namespace"""
        return import_module (".".join ((self.__module_name, name)))
    # end def _Import_Module

    def _Import_All (self, mod_skip_pat = None) :
        """Import all modules of this package namespace"""
        from _TFL import sos
        dir = sos.path.dirname  (self.__file__)
        pns = self.__module_name
        for f in sos.listdir (dir) :
            is_py = f.endswith (".py")
            want = \
                (   (  is_py
                    or sos.path.exists (sos.path.join (dir, f, "__init__.py"))
                    )
                and not
                    (  f.startswith (("__", "."))
                    or f == "setup.py"
                    or ( mod_skip_pat.search (f)
                       if mod_skip_pat is not None else False
                       )
                    )
                )
            if want :
                mn  = f [:-3] if is_py else f
                mod = ".".join ((pns, mn))
                try :
                    import_module (mod)
                except Exception as exc :
                    logging.exception \
                        ( "%s._Import_All: "
                          "exception during import of %s\n    %s"
                        % (self.__name__, mn, exc)
                        )
    # end def _Import_All

    def _exported_module (self, module_name, mod) :
        return mod
    # end def _exported_module

    def _import_names (self, mod, names, result, check_clashes) :
        for name in names :
            if isinstance (name, str) :
                name, as_name = name, name
            else :
                name, as_name = name
            try :
                obj = getattr (mod, name)
            except AttributeError :
                raise ImportError \
                    ("Cannot import name %s from %s" % (name, mod.__name__))
            else :
                self._import_1 (mod, name, as_name, obj, result, check_clashes)
    # end def _import_names

    def _import_1 (self, mod, name, as_name, obj, result, check_clashes) :
        if __debug__ :
            old = self.__dict__.get (name, obj)
            if check_clashes and old is not obj :
                raise ImportError \
                    ( "ambiguous name %s refers to %s and %s"
                    % (name, obj, old)
                    )
        result [as_name] = obj
        if isinstance (obj, Package_Namespace) :
            obj._Outer = self
    # end def _import_1

    def _Load_Module (self, caller_globals) :
        q_name = caller_globals ["__name__"]
        b_name = q_name.split   (".") [-1]
        mod    = self.__module_space._load (q_name, b_name)
        if self.__PKG__ is None :
            self.__PKG__ = mod
        return b_name, mod
    # end def _Load_Module

    def _Register_Module (self, mod) :
        try :
            ### if `mod` is a package exporting a Package_Namespace,
            ### `mod.__PNS__` was already set by `Package_Namespace.__init__`
            mod.__PNS__
        except AttributeError :
            mod.__PNS__  = self.__Table [mod.__name__] = self
    # end def _Register_Module

    def _Reload (self, * modules) :
        """Reload all the `modules` of the `Package_Namespace` specified
           (default: all modules of the `Package_Namespace` currently imported).
        """
        old_reload  = self.__reload
        if not modules :
            modules = self.MODULES
        try :
            self.__reload = 1
            print ("Reloading", self.__bname, end = " ")
            for m in modules :
                print (m.__name__, end = " ")
                m         = reload (m)
                m.__PNS__ = self
            print ("finished")
        finally :
            self.__reload = old_reload
        import linecache
        linecache.clearcache ()
    # end def _Reload

    @classmethod
    def _run_import_callback (cls, module, callback_spec = ()) :
        if not callback_spec :
            module_name = module.__name__
            package     = "__main__"
            if "." in module_name :
                package, module_name = module_name.rsplit (".", 1)
            if package in cls._Import_Callback_Map :
                pkg_map       = cls._Import_Callback_Map [package]
                callback_spec = pkg_map.pop (module_name, ())
        if callback_spec :
            for cb, args, kw in callback_spec :
                cb (module, * args, ** kw)
    # end def _run_import_callbacks

    def __getattr__ (self, name) :
        for lr in self.__lazy_resolvers :
            try :
                result = lr (self, name)
            except AttributeError :
                pass
            else :
                if result is not None :
                    setattr (self, name, result)
                return result
        raise AttributeError (name)
    # end def __getattr__

    def __repr__ (self) :
        return "<%s %s>" % (self.__class__.__name__, self.__name__)
    # end def __repr__

# end class Package_Namespace

class Derived_Package_Namespace (Package_Namespace) :
    """Implements a derived Package_Namespace, which adds to classes and
       functions of an existing Package_Namespace.

       Derivation of Package_Namespaces is similar to inheritance between
       classes -- the derived Package_Namespace

       - can add new modules to the ones inherited

       - can modify some properties of inherited modules (by defining a
         module of the same name which defines sub-classes and/or
         functions overriding the original functions)

       To transparently support inheritance-like import behavior,
       Derived_Package_Namespace allows to import modules of the base
       Package_Namespace through the Derived_Package_Namespace. For instance,
       consider a package `_B` defining a Package_Namespace `B` and a
       package `_D` defining a Derived_Package_Namespace `D` based on `B`::

           ### _B/__init__.py  <---derived-from----  _D/__init__.py
           ###    X.py                                  X.py
           ###    Y.py
           ###                                          Z.py

           # from   _D import D
           # import _D.X        ### imports from _D/X.py
           # import _D.Y        ### imports from _B/Y.py
           # import _D.Z        ### imports from _D/Z.py

       For derived imports to work, the Derived_Package_Namespace must be
       imported before the module needing import derivation is imported (this
       only is important for nested Package_Namespaces).

    """

    def __init__ (self, parent, * lazy_resolvers, ** kw) :
        c_scope, module_name, name = self._args_from_kw (kw)
        Package_Namespace.__init__ \
            ( self, * lazy_resolvers
            , module_name = module_name
            , name        = name
            , c_scope     = c_scope
            )
        self._parent  = parent
        self.__cached = {}
        DPN_Import_Finder.register (self, parent)
    # end def __init__

    def _Reload (self, * modules) :
        for c in self.__cached :
            delattr (self, c)
        self.__cached = {}
        self._parent._Reload ()
        Package_Namespace._Reload (self, * modules)
    # end def _Reload

    def _add_module_getattr (self, mod, parent_module) :
        def _getattr (name) :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            if name != "__wrapped__" :
                return getattr (parent_module, name)
            raise AttributeError (name)
        def _dir () :
            return dir (parent_module)
        mod.__dir__     = _dir
        mod.__getattr__ = _getattr
    # end def _add_module_getattr

    def _exported_module (self, module_name, mod) :
        try :
            parent_module = getattr (self._parent, module_name)
        except AttributeError :
            pass
        else :
            self._add_module_getattr (mod, parent_module)
        return mod
    # end def _exported_module

    def __getattr__ (self, name) :
        try :
            ### `Package_Namespace.__getattr__` checks `__lazy_resolvers`
            return Package_Namespace.__getattr__ (self, name)
        except AttributeError :
            result  = getattr (self._parent, name)
            self.__cached [name] = result
            setattr (self, name, result)
            return  result
    # end def __getattr__

# end class Derived_Package_Namespace

__all__ = \
    ("Package_Namespace", "Derived_Package_Namespace", "DPN_Import_Finder")

__doc__ = """
This module implements a namespace that provides direct access to classes and
functions provided by the modules of a Python package.

In the following, a package ``Foo_Package`` and module ``Bar`` are assumed as
example.

A Python package encapsulates a number of modules. Packages are useful
for avoiding name clashes between modules of different domains. For
instance, ``Frame`` might be used as module name by a GUI package and by
a communications package.

Many modules define a class or function with the same name as
the module name. There are different styles how to access such a
class::

   #1
   # import Bar
   # instance = Bar.Bar ()

   #2
   # from Bar import Bar
   # instance = Bar ()

Many Pythoneers use the `Bar.Bar` notation to refer to the class `Bar`
defined by module `Bar`. I strongly prefer to use `Bar` to refer to
the class.

In the presence of packages, there are even more possibilities::

   #3
   # import Foo_Package.Bar
   # instance = Foo_Package.Bar.Bar ()

   #4
   # from Foo_Package import Bar
   # instance = Bar.Bar ()

   #5
   # from Foo_Package.Bar import Bar
   # instance = Bar ()

If one wants to avoid name clashes only #3 is usable. Unfortunately,
this makes for very verbose and unreadable code. One way to avoid this
is to import all classes/functions of all modules of the package in
the `__init__.py`. The disadvantages of this approach are

- Import bloat. Importing the package will pull in the entire contents
  of the package even if only a tiny part of it is needed.

- If the package qualifier is used inside the package too (strongly
  recommended), circular imports will result.

    Using the package name to qualify class and function names defined
    by the modules of the package considerably eases using grep for
    finding occurences of their use.

:class:`Package_Namespace` provides another option::

   #6
   # from   Foo_Package import Foo
   # import Foo_Package.Bar
   # instance = Foo.Bar ()

In order to support this, `Foo_Package/__init__.py` must export an
instance `Foo` of :class:`Package_Namespace`::

   ### Foo_Package/__init__.py
   # from _TFL.Package_Namespace import Package_Namespace
   # Foo = Package_Namespace ()

The :class:`Package_Namespace` provides the :meth:`~Package_Namespace._Export`
method called by modules of the package to export classes/functions module into
the namespace::

   ### Foo_Package.Bar puts `Bar` and `Baz` into the Package_Namespace
   Foo._Export ("Bar", "Baz")

`_Export` accepts "*" as a wild card and uses Python's rules to expand
that with the important caveat, that here "*" only includes functions
and classes defined by the calling module (i.e., "*" doesn't work
transitively).

If a module prefers to put itself instead of some of its attributes
(functions/classes/whatever) into the Package_Namespace, it can do so
by calling :meth:`~Package_Namespace._Export_Module`::

   Foo._Export_Module ()

The modules of the package can be accessed via the :attr:`~Package_Namespace._`
attribute of the package namespace.

The standard naming convention for packages exporting a
Package_Namespace is::

   _TFL           ### the Python package
   TFL            ### the Package_Namespace

i.e., use the same name but with a leading underscore for the package.

So, the canonical use of Package_Namespaces looks like::

   #7
   # from   _TFL import TFL
   # import _TFL.Filename
   # fn = TFL.Filename ("/some/very/important/file.name")

.. note::

 The methods `_Add_Import_Callback`, `_Add_Lazy_Resolver`, `_Export`,
 `_Export_Module`, `_Import_All`, `_Import_Module`, and `_Reload` are part of
 the public interface of `Package_Namespaces` (they start with an underscore to
 avoid name clashes with user-defined attributes of package namespaces).

"""

if __name__ != "__main__" :
    if DPN_Import_Finder not in sys.meta_path :
        sys.meta_path.append (DPN_Import_Finder)
### __END__ TFL.Package_Namespace
