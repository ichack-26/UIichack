# -*- coding: utf-8 -*-
# Copyright (C) 2012-2022 Christian Tanzer All rights reserved
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
#    TFL.Command
#
# Purpose
#    Base class for an interactive command using CAO to define/process
#    arguments and options
#
# Revision Dates
#    17-May-2012 (CT) Creation
#    22-May-2012 (CT) Add `Sub_Command`, `app_dir`, and `app_path`
#    23-May-2012 (CT) Add `lib_dir`, `Sub_Command._handler_prefix`
#    24-May-2012 (CT) Add `_..._to_combine` to `_lists_to_combine`
#    25-May-2012 (CT) Add `sc_map` and `__getitem__`; add `_parent`
#    31-May-2012 (CT) Add `config_defaults`, define `Config` option in `opts`
#     1-Jun-2012 (CT) Fix `__doc__` in `_M_Command_.__new__`
#     1-Jun-2012 (CT) Add `Sub_Command_Combiner`
#     2-Jun-2012 (CT) Use `_TFL._Export_Module`, not `_TFL._Export`
#     2-Jun-2012 (CT) Factor `_Meta_Base_`, add `Option`
#     2-Jun-2012 (CT) Add `Config_Option`, remove `config_defaults`
#     3-Jun-2012 (CT) Sort `_opts_reified` by `rank`, fill `_opt_map`
#     3-Jun-2012 (CT) Factor `Rel_Path_Option`, add `Config_Dirs_Option`
#     3-Jun-2012 (CT) Add `Root_Command`
#     4-Jun-2012 (CT) Change `app_path` to use `root`
#    23-May-2013 (CT) Use `TFL.Meta.BaM` for Python-3 compatibility
#    16-Dec-2013 (CT) Factor `Rel_Path_Option._gen_base_dirs`
#    16-Dec-2013 (CT) Redefine `Config_Dirs_Option.base_dirs` to use
#                     `_defaults`, not `_base_dirs`
#    17-Dec-2013 (CT) Set `Config_Dirs_Option.type` to `False`
#    17-Dec-2013 (CT) Remove redefinition of `Config_Option.default`
#                     (resulted in double application of `base_dirs`)
#    17-Dec-2013 (CT) Improve $-expansion for `Rel_Path_Option.base_dirs`
#    18-Dec-2013 (CT) Add `abspath` to `app_dir`
#     2-Sep-2014 (CT) Change defaults to add `_init_kw` before
#                     `dynamic_defaults`
#    26-Jan-2015 (CT) Derive `_Meta_Base_` from `M_Auto_Update_Combined`,
#                     not `M_Auto_Combine`
#    21-Jul-2015 (CT) Add `Rel_Path_Option.skip_missing`
#     5-Aug-2015 (CT) Use `handler_name` instead of `_handler_prefix`
#     5-Aug-2015 (CT) Add `__doc__`
#     5-Aug-2015 (CT) Continue adding `__doc__`
#     6-Aug-2015 (CT) Add `Option.explanation`
#    15-Jun-2016 (CT) Add `_wrapped_handler` to LET `_cao`
#                     + Rename handler argument `cmd` to `cao`
#     2-Mar-2017 (CT) Add `Key_Option` and `Set_Option`
#     8-Aug-2017 (CT) Add guard for `None` to `_sub_commands`
#     4-May-2018 (CT) Factor `Command._get_cao` to allow redefinition
#     4-Sep-2018 (CT) Add `_parent_defaults` to `Command`
#                     + Don't pass `** defaults` in `sub_commands`
#    10-Sep-2018 (CT) Add `_do_shell`
#    31-May-2020 (CT) Add `explanation` to `Command`
#    22-Oct-2022 (CT) Add `Config_File_Option`
#    23-Oct-2022 (CT) Add `Config_File_Option.pre_load_cb`, `.x_context`
#    23-Oct-2022 (CT) Add `active_sub_cmd` to `_wrapped_handler_context`
#    ««revision-date»»···
#--

from   _TFL                   import TFL

from   _TFL.I18N              import _, _T, _Tn
from   _TFL.object_globals    import object_module
from   _TFL.predicate         import first, split_hst, uniq
from   _TFL.pyk               import pyk
from   _TFL                   import sos

import _TFL.Accessor
import _TFL.CAO
import _TFL._Meta.M_Auto_Update_Combined
import _TFL._Meta.Object
import _TFL._Meta.Once_Property

from   itertools              import chain as ichain

class _Meta_Base_ (TFL.Meta.M_Auto_Update_Combined) :

    def __new__ (mcls, name, bases, dct) :
        prefix = dct.get ("_rn_prefix") or first \
            (getattr (b, "_rn_prefix", None) for b in bases)
        if prefix and name.startswith (prefix) and "_real_name" not in dct :
            dct ["_real_name"] = name [len (prefix):]
        if "_name" not in dct :
            dct ["_name"] = dct.get ("_real_name", name).strip ("_").lower ()
        dct.setdefault ("is_partial", False)
        if not dct.get ("__doc__") :
            ### Find the right base to inherit doc-string from
            ### * must be an instance of `_Meta_Base_`
            ### * must contain a non-empty doc-string in its __dict__
            try :
                dct ["__doc__"] = first \
                    (  d for d in
                           (  b.__dict__.get ("__doc__") for b in bases
                           if isinstance (b, _Meta_Base_)
                           )
                    if d
                    )
            except LookupError :
                pass
        return mcls.__mc_super.__new__ (mcls, name, bases, dct)
    # end def __new__

# end class _Meta_Base_

class _M_Option_ (_Meta_Base_) :
    ### Meta class for `Option`.

    pass

# end class _M_Option_

class TFL_Option (TFL.Meta.Object, metaclass = _M_Option_) :
    ### Base class for options of interactive commands.

    _real_name              = "Option"
    _rn_prefix              = "TFL_"

    cook              = None
    explanation       = None
    hide              = False
    max_number        = None
    range_delta       = 1
    rank              = 0
    type              = None

    _auto_split       = None
    _default          = None
    _defaults         = ()
    _name             = None

    _attrs_uniq_to_update_combine = ("_defaults", )

    def __init__ (self, cmd) :
        if self.type is None :
            raise TypeError \
                ("%s::%s must define `type`" % (cmd, self.__class__.__name__))
        type = self.type
        if isinstance (type, pyk.string_types) :
            try :
                type = self.type = TFL.CAO.Opt.Table [type]
            except KeyError :
                type = self.type = getattr (TFL.CAO, type)
        self.cmd = cmd
    # end def __init__

    def __call__ (self) :
        kwds   = self.kw
        result = self.type (** kwds)
        return result
    # end def __call__

    @TFL.Meta.Once_Property
    def auto_split (self) :
        result = self._auto_split
        if result is None :
            result = self.type.auto_split
        return result
    # end def auto_split

    @TFL.Meta.Once_Property
    def default (self) :
        result = self._default
        if result is None and self._defaults :
            if self.auto_split :
                result = self.auto_split.join (self._defaults)
            else :
                raise TypeError \
                    ( "%s::%s has multiple defaults %s, but no `auto_split`"
                    % (cmd, self.__class__.__name__, self._defaults)
                    )
        return result
    # end def default

    @TFL.Meta.Once_Property
    def kw (self) :
        return dict \
            ( name            = self.name
            , default         = self.default
            , description     = self.__doc__
            , auto_split      = self.auto_split
            , max_number      = self.max_number
            , hide            = self.hide
            , range_delta     = self.range_delta
            , cook            = self.cook
            , explanation     = self.explanation
            , rank            = self.rank
            )
    # end def kw

    @TFL.Meta.Once_Property
    def name (self) :
        return self._name or self.__class__.__name__.strip ("_").lower ()
    # end def name

Option = TFL_Option # end class

class TFL_Key_Option (Option) :

    choice_dict             = None ### sub-class responsibility
    type                    = TFL.CAO.Opt.Key

    @TFL.Meta.Once_Property
    def kw (self) :
        result = self.__super.kw
        result.update (dct = None, choice_dict = self.choice_dict)
        return result
    # end def kw

Key_Option = TFL_Key_Option # end class

class TFL_Rel_Path_Option (Option) :

    auto_split              = ":"
    single_match            = False
    skip_missing            = True
    type                    = TFL.CAO.Rel_Path

    _base_dir               = None
    _base_dirs              = ("$app_dir", )

    @TFL.Meta.Once_Property
    def base_dirs (self) :
        result = tuple \
            (self._gen_base_dirs (self._base_dirs or (self._base_dir, )))
        return result
    # end def base_dirs

    @TFL.Meta.Once_Property
    def kw (self) :
        result = self.__super.kw
        if self.base_dirs :
            result ["_base_dirs"] = self.base_dirs
        result.update \
            ( single_match = self.single_match
            , skip_missing = self.skip_missing
            )
        return result
    # end def kw

    def _gen_base_dirs (self, bds) :
        cwd = sos.getcwd ()
        for bd in bds :
            if isinstance (bd, pyk.string_types) and bd.startswith ("$") :
                h, _, t = split_hst (bd, "/")
                h       = getattr (self.cmd, h [1:])
                if h == "" :
                    h   = cwd
                bd = "/".join ((h, t)) if t else h
            if bd is not None :
                yield bd
    # end def _gen_base_dirs

Rel_Path_Option = TFL_Rel_Path_Option # end class

class TFL_Config_Dirs_Option (Rel_Path_Option) :
    """Directories(s) considered for option files"""

    rank                    = -100
    type                    = False

    @TFL.Meta.Once_Property
    def base_dirs (self) :
        return tuple (self._gen_base_dirs (self._defaults or (self._default, )))
    # end def base_dirs

Config_Dirs_Option = TFL_Config_Dirs_Option # end class

class TFL_Config_File_Option (Rel_Path_Option) :
    """File(s) specifying defaults for options"""

    rank                    = -90

    type                    = TFL.CAO.Config_File

    _config_dirs_name       = "config_dirs"

    pre_load_cb             = None
    x_context               = {}

    @TFL.Meta.Once_Property
    def base_dirs (self) :
        result  = self.__super.base_dirs
        opt_map = self.cmd._opt_map
        cdo     = opt_map.get (self._config_dirs_name)
        if cdo and cdo.base_dirs :
            result = cdo.base_dirs + result
        return tuple (uniq (result))
    # end def base_dirs

    @TFL.Meta.Once_Property
    def kw (self) :
        result = self.__super.kw
        if plcb := self.pre_load_cb :
            result.update (pre_load_cb = plcb)
        if xc := self.x_context :
            result.update (x_context = xc)
        return result
    # end def kw

Config_File_Option = TFL_Config_File_Option # end class

class TFL_Config_Option (Config_File_Option) :
    """File(s) specifying defaults for options"""

    type                    = TFL.CAO.Config

Config_Option = TFL_Config_Option # end class

class TFL_Set_Option (Option) :

    choices                 = None ### sub-class responsibility
    type                    = TFL.CAO.Opt.Set

    @TFL.Meta.Once_Property
    def kw (self) :
        result = self.__super.kw
        result.update (choices = self.choices)
        return result
    # end def kw

Set_Option = TFL_Set_Option # end class

class _M_Command_ (_Meta_Base_) :
    ### Meta class for `Command`

    def __new__ (mcls, name, bases, dct) :
        mcls._update_set (dct, _M_Command_, "_sub_commands")
        mcls._update_set (dct, _M_Option_,  "_opts_reified")
        return mcls.__mc_super.__new__ (mcls, name, bases, dct)
    # end def __new__

    @classmethod
    def _update_set (cls, dct, T, name) :
        dct [name] = _set = set (dct.get (name, ()))
        _set.update \
            (  v.__name__ for v in pyk.itervalues (dct)
            if isinstance (v, T) and not getattr (v, "is_partial", 0)
            )
    # end def _update_set

# end class _M_Command_

class TFL_Command (TFL.Meta.Object, metaclass = _M_Command_) :
    ### Base class for interactive commands.

    _rn_prefix                    = "TFL_"

    _attrs_to_update_combine      = \
        ("_defaults", "_opts_reified", "_sub_commands")

    _attrs_uniq_to_update_combine = \
        ("_args", "_buns", "_opts")

    cmd_choice_name         = _ ("command")
    do_keywords             = False
    explanation             = ""
    handler                 = None
    handler_name            = "_handle"
    helper                  = None
    min_args                = 0
    max_args                = -1
    put_keywords            = False

    active_sub_cmd          = None ### `LET` during execution of `handler`
    _args                   = ()
    _buns                   = ()
    _cao                    = None ### `LET` during execution of `handler`
    _defaults               = {}
    _description            = ""
    _name                   = None
    _opts                   = ()
    _opts_reified           = set ()
    _root                   = None
    _sub_commands           = set ()

    def __init__ (self, _name = None, _parent = None, ** kw) :
        if _name is not None :
            self._name      = _name
        self._init_kw       = kw
        self._parent        = _parent
        if _parent is not None :
            self._root      = _parent._root or _parent
        self._cmd           = TFL.CAO.Cmd \
            ( args          = self.args
            , buns          = self.buns
            , defaults      = self.defaults
            , description   = self.description
            , do_keywords   = self.do_keywords
            , explanation   = self.explanation
            , handler       = self._wrapped_handler
            , helper        = self.helper
            , name          = self.name
            , max_args      = self.max_args
            , min_args      = self.min_args
            , opts          = self.opts
            , put_keywords  = self.put_keywords
            )
    # end def __init__

    def __call__ (self, _argv = None, ** _kw) :
        handler_args = _kw.pop  ("args", ())
        handler_kw   = _kw.pop  ("kw",   {})
        cao          = self._get_cao (_argv, ** _kw)
        if cao is not None :
            return cao (* handler_args, ** handler_kw)
    # end def __call__

    @TFL.Meta.Once_Property
    def app_dir (self) :
        return sos.path.abspath (sos.path.dirname (self.app_path))
    # end def app_dir

    @TFL.Meta.Once_Property
    def app_path (self) :
        root = self._root or self
        return object_module (root).__file__
    # end def app_path

    @TFL.Meta.Once_Property
    def args (self) :
        if self._sub_commands :
            assert not self._args, \
                ( "Cannot specify both args %s and sub-commands %s"
                , (self._args, self._sub_commands)
                )
            name = _T (self.cmd_choice_name)
            scs  = tuple (sc._cmd for sc in self.sub_commands)
            return (TFL.CAO.Cmd_Choice (name, * scs), )
        else :
            return self._args
    # end def args

    @TFL.Meta.Once_Property
    def buns (self) :
        return self._buns
    # end def buns

    @TFL.Meta.Once_Property
    def defaults (self) :
        result = dict (self._parent_defaults)
        result.update (self._defaults)
        result.update (self._init_kw)
        result.update (self.dynamic_defaults (result))
        return result
    # end def defaults

    @TFL.Meta.Once_Property
    def lib_dir (self) :
        return sos.path.dirname (sos.path.dirname (__file__))
    # end def lib_dir

    @TFL.Meta.Once_Property
    def description (self) :
        return self._description or self.__class__.__doc__
    # end def description

    @TFL.Meta.Once_Property
    def name (self) :
        if self._root :
            return self._name or self.__class__.__name__.strip ("_").lower ()
        else :
            return self.app_path
    # end def name

    @TFL.Meta.Once_Property
    def opts (self) :
        def _gen (self) :
            self._opt_map = map = {}
            for oc in sorted \
                    ( (  oc for oc in
                           (getattr (self, k) for k in self._opts_reified)
                      if oc is not None
                      )
                    , key = TFL.Getter.rank
                    ) :
                o = oc (self)
                map [o.name] = o
                if o.type :
                    yield o ()
        result = list (_gen (self))
        result.extend (self._opts)
        return tuple  (result)
    # end def opts

    @TFL.Meta.Once_Property
    def sc_map (self) :
        return dict ((sc.name, sc) for sc in self.sub_commands)
    # end def sc_map

    @TFL.Meta.Once_Property
    def sub_commands (self) :
        def _gen (self) :
            for sc in self._sub_commands :
                if isinstance (sc, pyk.string_types) :
                    sc = getattr  (self, sc)
                if sc is not None :
                    if not isinstance (sc, TFL.CAO.Cmd) :
                        sc = sc (_parent = self)
                    yield sc
        return tuple (_gen (self))
    # end def sub_commands

    def dynamic_defaults (self, defaults) :
        return {}
    # end def dynamic_defaults

    def _do_shell (self, glob_dct = None, locl_dct = None, depth = 1, ** kw) :
        TFL.Environment.py_shell (glob_dct, locl_dct, depth = depth, ** kw)
    # end def _do_shell

    def _get_cao (self, _argv = None, ** _kw) :
        return self._cmd.cao (_argv, ** _kw)
    # end def _get_cao

    @TFL.Meta.Once_Property
    def _parent_defaults (self) :
        return self._parent.defaults if self._parent else {}
    # end def _parent_defaults

    def _wrapped_handler (self, cao, * args, ** kw) :
        with self._wrapped_handler_context (cao, * args, ** kw) :
            return self.handler (cao, * args, ** kw)
    # end def _wrapped_handler

    @TFL.Contextmanager
    def _wrapped_handler_context (self, cao, * args, ** kw) :
        with self.LET (_cao = cao) :
            root = self._root
            if root is not None and root is not self :
                with root.LET (_cao = cao, active_sub_cmd = self) :
                    yield
            else :
                yield
    # end def _wrapped_handler_context

    def __getitem__ (self, key) :
        if " " in key :
            result = self.sc_map
            for k in key.split (" ") :
                result = result [k]
        else :
            result = self.sc_map [key]
        return result
    # end def __getitem__

Command = TFL_Command # end class

class TFL_Sub_Command (Command) :
    ### Base class for sub-commands

    _real_name              = "Sub_Command"

    def handler (self, cao) :
        return self._handler (cao)
    # end def handler

    @TFL.Meta.Once_Property
    def handler_name (self) :
        return "_".join ((self._parent.handler_name, self.name))
    # end def handler_prefix

    @TFL.Meta.Once_Property
    def _handler (self) :
        return getattr (self._root, self.handler_name)
    # end def _handler

Sub_Command = TFL_Sub_Command # end class

class TFL_Sub_Command_Combiner (Command) :
    ### Base class for sub-commands that combine a number of other sub-commands

    _real_name              = "Sub_Command_Combiner"

    ### `_sub_command_seq` can't be auto-combined because a descendent might
    ### want a different sequence
    _sub_command_seq        = []

    @TFL.Meta.Once_Property
    def sub_command_seq (self) :
        def _gen (self) :
            for sc in self._sub_command_seq :
                if isinstance (sc, pyk.string_types) :
                    yield [sc]
                else :
                    yield sc
        return tuple (_gen (self))
    # end def sub_command_seq

    def handler (self, cao) :
        opts   = self._std_opts (cao)
        parent = self._parent
        for sc in self.sub_command_seq :
            parent (sc + opts)
    # end def handler

    def _std_opts (self, cao) :
        result = []
        raws   = cao._raw
        opts   = cao._opt_dict
        for k, v in pyk.iteritems (cao._map) :
            opt = opts.get (k)
            if opt :
                mk = "-" + k
                if k in raws :
                    result.extend ((mk, opt.auto_split.join (raws [k])))
                elif v and (not isinstance (v, list) or any (v)) :
                    result.append (mk)
        return result
    # end def _std_opts

Sub_Command_Combiner = TFL_Sub_Command_Combiner # end class

class TFL_Root_Command (Command) :
    ### Base class for root commands

    class TFL_Config_Dirs (Config_Dirs_Option) :
        """Directories(s) considered for option files."""

    Config_Dirs = TFL_Config_Dirs # end class

    class TFL_Config (Config_Option) :
        """File(s) specifying defaults for options."""

    Config = TFL_Config # end class

    class TFL_Config_File (Config_File_Option) :
        """File(s) specifying defaults for options."""

    Config_File = TFL_Config_File # end class

Root_Command = TFL_Root_Command # end class

### «text» ### start of documentation
__doc__ = r"""
This module provides a framework to assemble complex **commands** with their
**sub-commands**, **argument**, and **options**.

- A simple command is defined by a single module that creates an instance of
  :class:`~_TFL.CAO.Cmd`.

- A complex command might be defined by a number of modules by defining a
  hierarchy of classes derived from :class:`Root_Command`.

  This allows frameworks to define the basic command with a set of generic
  sub-commands, arguments, and options.

  A specific application based on such a framework derives a specific command
  class which

  + might combine the generic commands of several different frameworks,

  + might add application specific sub-commands,

  + might set or override defaults for options, and

  + might redefine the handlers of some or all generic sub-commands.

  For instance,

  + the :mod:`MOM<_MOM>` framework provides a class :class:`~_MOM.Command`
    that defines sub-commands for managing object models and the databases
    where they are stored.

  + the :mod:`GTW<_GTW>` framework extends :class:`~_MOM.Command` by adding
    sub-commands for running a MOM-based application as a web service.

  + a specific application based on :mod:`MOM<_MOM>` and :mod:`GTW<_GTW>`

    * might define additional application specific sub-commands,

    * might define options for config-files,

    * might define media parameters used for CSS styles,

    * needs to define the directories containing Jinja templates, and

    * needs to define methods that instantiate the resource tree of the
      web service.

.. class:: Command

  `Command` is the common base class of the classes :class:`Root_Command`,
  :class:`Sub_Command`, and :class:`Sub_Command_Combiner`.

  A command's `arguments`_, `options`_, `sub-commands`_, and `other properties`_
  are defined by class variables and embedded :class:`Option`,
  :class:`Sub_Command`, and :class:`Sub_Command_Combiner` classes.

  When a :class:`Command` is instantiated, it creates and stores an
  instance of :class:`~_TFL.CAO.Cmd`; calling a :class:`Command` instance
  delegates the call to the internal :class:`~_TFL.CAO.Cmd` instance.

  :class:`Command`'s meta class :class:`_M_Command_` is derived from
  :class:`~_TFL._Meta.M_Auto_Update_Combined.M_Auto_Update_Combined` and
  automatically update-combines the class variables:

  .. _`arguments`:

  .. attribute:: _args

    Argument tuple: the elements of `_args` are specified exactly as for the
    :obj:`args` argument of :class:`~_TFL.CAO.Cmd`.

    A :class:`Command` can either provide :attr:`_sub_commands` or
    :attr:`_args` but not both. If `_args` is provided, it is passed to
    :class:`~_TFL.CAO.Cmd` unchanged.

  .. attribute:: _buns

    Bundle tuple: the elements of `_buns` are specified exactly as for the
    :obj:`buns` argument of :class:`~_TFL.CAO.Cmd`. `_buns` is
    passed to :class:`~_TFL.CAO.Cmd` unchanged.

  .. attribute:: _opts

    Options tuple: the elements of `_opts` are specified exactly as for the
    :obj:`opts` argument of :class:`~_TFL.CAO.Cmd`.

  Additionally, :class:`_M_Command_` combines all class attributes that are
  derived from :class:`Command` and :class:`Option` into the class variables
  :attr:`_sub_commands` and :class:`_opts_reified`, respectively:

  .. _`sub-commands`:

  .. attribute:: _sub_commands

    Sub-command set: set of names of the `sub-commands`_ of the embedding
    :class:`Command` (and its ancestors).

    Sub-Commands are defined by embedded classes derived from
    :class:`Sub_Command` or :class:`Sub_Command_Combiner`. A :class:`Command`
    with sub-commands cannot have other arguments defined in :attr:`_args`.

  .. attribute:: _opts_reified

    Reified options set: set of names of option classes embedded in
    :class:`Command` class (and its ancestors).

  .. _`options`:

  **Options**

  Options can be defined in two ways:

  + As elements of the :attr:`_opts` tuple.

  + As embedded classes derived from :class:`Option`. The meta class
    :class:`_M_Command_` combines these into the class variable
    :attr:`_opts_reified`.

  :attr:`_opts` and instances of all the elements :attr:`_opts_reified` are
  passed to :class:`~_TFL.CAO.Cmd` as the :obj:`opts` argument.

  .. _`other properties`:

  **Properties**

  .. attribute:: cmd_choice_name

    Defines the name of the :class:`~_TFL.CAO.Cmd_Choice` instance for
    :attr:`_sub_commands`; default is "command".

  .. attribute:: is_partial

    Classes with a false value of `is_partial` won't be included in the options
    and sub-commands. This can be used to factor common code between options
    or sub-commands.

  .. attribute:: _defaults

    An auto-combining dictionary with default values for options. One can
    include the default value of an option with the option's definition,
    but in many cases, such a default is application dependent even for generic
    options. `_defaults` allows the redefinition of default values with
    a minimum of code.

  .. attribute:: _rn_prefix

    :class:`_M_Command_` expects the names of all :class:`Command` classes to
    start with `_rn_prefix` and will automatically remove that prefix from the
    class name while avoiding name clashes in the class's method resolution
    order.

    The canonical use of `_rn_prefix` is to use the name of the package
    namespace containing the :class:`Command`. If one package namespace defines
    more than one command, different values based on the package namespace name
    should be used for `_rn_prefix`.

  The following properties are passed through to :class:`~_TFL.CAO.Cmd`
  unchanged and are documented there:

  .. attribute:: do_keywords

  .. attribute:: helper

  .. attribute:: max_args

  .. attribute:: min_args

  .. attribute:: put_keywords

  The following properties are calculated by :class:`Command` and passed
  to :class:`~_TFL.CAO.Cmd`:

  .. attribute:: args

    Either :attr:`_args` or a :class:`~_TFL.CAO.Cmd_Choice` instance for
    :attr:`_sub_commands`.

  .. attribute:: buns

    Just the contents of :attr:`_buns`

  .. attribute:: defaults

    Dictionary with default values for options computed from:

    - :attr:`_defaults`,

    - the keyword arguments passed to the :class:`Command` instance,

    - the result of :meth:`dynamic_defaults`.

    Keyword arguments override :attr:`_defaults`, :meth:`dynamic_defaults`
    override keyword arguments and :attr:`_defaults`.

  .. attribute:: description

    Either the value of :attr:`_description` or of :attr:`__class__.__doc__`.

  .. attribute:: name

    Either the value of :attr:`_name` or the lower case value of
    :attr:`__class__.__name__` stripped of leading and trailing underscores.

  .. attribute:: opts

    The contents of :attr:`_opts` plus instances of all the elements of
    :attr:`_opts_reified`.

  .. attribute:: sub_commands

    Instances of all elements of :attr:`_sub_commands`.

  :class:`Command` instances provide the API:

  .. attribute:: app_dir

    The absolute path to the directory containing the class defining the
    application's :class:`Root_Command`.

  .. attribute:: app_path

    The path to the python module containing the class defining the
    application's :class:`Root_Command`.

  .. attribute:: lib_dir

    The path to the directory containing the package namespace `_TFL`.

  .. method:: dynamic_defaults(defaults)

    This method can calculate dynamic default values for options and must
    return a dictionary. If one redefines `dynamic_defaults` in a descendent
    class, one should normally chain up to the super class's
    `dynamic_defaults`.

    The argument `defaults` is a dictionary computed from `_defaults` and the
    keyword arguments passed to the :class:`Command` instance.

    `dynamic_defaults` can override values of `defaults` by including a
    different value in its result.

    `dynamic_defaults` can use values like :attr:`app_dir` and :attr:`lib_dir`
    and is thus useful to setup default search paths that include directories
    containing python modules, e.g., for template directories or Babel
    configuration files.

.. class:: Root_Command

  One defines a complex command by deriving a class (directly or indirectly)
  from `TFL.Root_Command`.

  ``Root_Command`` is derived from :class:`Command` and adds the `options`_
  :attr:`Config_Dirs` and :attr:`Config`.

.. class:: Sub_Command

  One defines a sub-command by including a class derived from
  :class:`Sub_Command` inside a :class:`Root_Command` or :class:`Sub_Command`
  class.

  The name of the sub-command can be specified explicitly by defining
  the class attribute :attr:`_name`; otherwise the lowercase name of the
  ``Sub_Command`` class stripped of leading and trailing underscores is used
  for the name.

  ``Sub_Command`` is derived from :class:`Command` and adds a default
  :meth:`handler` method that delegates to a method of the root command (by
  default that method's name is combined from ``parent.handler_name`` and the
  sub-command's ``name``).

  Alternatively, one can define the `handler` method by overriding
  :meth:`handler` inside the ``Sub_Command`` class.

.. class:: Sub_Command_Combiner

  A sub-command combiner is a class derived from :class:`Sub_Command` that
  defines a sequence of sub-commands to be executed in that order in the class
  variable :attr:`_sub_command_seq`.

  .. attribute:: _sub_command_seq

    A sequence of sub-commands. Each element either is a name of a sub-command
    or a argv-style list starting with the name of a sub-command followed by
    argument and option values.

.. class:: Option

  Once can define an option by embedding a subclass of `Option` in a
  :class:`Command` class. When the command is instantiated, it instantiates a
  :class:`~_TFL.CAO.Arg` or :class:`~_TFL.CAO.Opt` instance for each of its
  `Option` classes.

  The class attributes of the :class:`Option` class define the semantics of
  the option:

  .. attribute:: type

    Specifies the :class:`~_TFL.CAO.Arg` or :class:`~_TFL.CAO.Opt` class of the
    option.

    One can either specify a class directly or specify the name or abbreviation
    of such a class.

  .. attribute:: name

    Either the value of :attr:`_name` or the lower case value of
    :attr:`__class__.__name__` stripped of leading and trailing underscores.

  .. attribute:: default

    Either the value of :attr:`_default` or the elements of :attr:`_defaults`
    joined by :attr:`auto_split`.

    This can be overriden by the :attr:`Command.defaults`.

  .. attribute:: __doc__

    The description of the option.

  .. attribute:: auto_split

    Either the value of :attr:`_auto_split` or the value of
    :attr:`type.auto_split`.

  .. attribute:: max_number

    The maximum number of values that can be specified for
    this option, either via auto-split or by multiple
    occurences of the option in the command line.

  .. attribute:: hide

    Don't include this option in `-help` if :attr:`hide` has a true value.

  .. attribute:: range_delta

    Delta to be used between option values if a range is specified on the
    command line, default is 1.

  .. method:: cook

    A method or function converting the raw value to the internal
    representation.

  .. attribute:: explanation

    More detailed information about the option.

  .. attribute:: rank

    Defines the rank of the option. During command setup, configuration options
    are processed in the order of increasing rank (default rank is 0).

.. class:: Rel_Path_Option

  An option with type :class:`~_TFL.CAO.Arg.Rel_Path`.

  :class:`Rel_Path_Option` offers additional class attributes:

  .. attribute:: single_match

    If true, restrict option values to a single match per value specified on
    the command line; otherwise include all matches. Default value is False.

  .. attribute:: skip_missing

    If true, skip matching values that don't exist in the file system (useful
    for input paths); otherwise, include matching values that don't exist
    (possibly useful for output paths). Default value is True.

  .. attribute:: _base_dir

    Specify a single base directory; overrides :attr:`_base_dirs`. Same
    semantics as for entries of `_base_dirs`.

  .. attribute:: _base_dirs

    List of base directories for matching relative paths. One can include
    properties of the embedding :class:`Command` by prefixing them with a "$"
    sign, e.g, "$app_dir" refers to the :attr:`Command.app_dir`. Default value
    is ``("$app_dir", )``.


.. class:: Config_Option

  An option derived from :class:`Rel_Path_Option` with type
  :class:`~_TFL.CAO.Arg.Config`.

  :class:`Config_Option` offers additional class attributes:

  .. attribute:: _config_dirs_name

    The name of a :class:`Config_Dirs_Option` option. Default value is
    "config_dirs".

    The :attr:`Option.defaults` of that option will be added to the front of
    the base directories of the :class:`Config_Option`.

.. class:: Config_Dirs_Option

  An option of type :class:`~_TFL.CAO.Arg.Rel_Path` that specifies directories
  for option files for one or more :class:`Config_Option` options.

  The directories are specified via the :attr:`Option.defaults` attribute.

.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

"""

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.Command

#+  LocalWords:  Reified reified
