# -*- coding: utf-8 -*-
# Copyright (C) 2002-2014 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Py2C_Wrapper
#
# Purpose
#    Generate C functions wrapping python code
#
# Revision Dates
#    25-Jul-2002 (CT)  Creation
#     5-Aug-2002 (MG)  Allow empty input and output parameter lists
#    09-Sep-2002 (RMA) "bool -> boolean"
#    31-Oct-2002 (mph) fixed _Py_Object_Ref_.make_copy () to work with
#                      string and length (e.g. 's#') objects
#    17-Jan-2003 (CT) `M_` prefixes added
#    26-Mar-2003 (CT)  Adapted to moving of `TTTech` to `TTT.copyright`
#    25-Aug-2004 (CT)  Use `_TFL._SDG._C` instead of `C_Document`
#    16-Sep-2004 (MPH) Changed `gen_method_wrapper` to also work with only one
#                      argument.
#    14-Feb-2006 (CT)  Moved into package `TFL`
#    29-Aug-2008 (CT)  s/super(...)/__m_super/
#    23-May-2013 (CT) Use `TFL.Meta.BaM` for Python-3 compatibility
#    ««revision-date»»···
#--

from   _TFL                  import TFL
from   _TFL.predicate        import *
from   _TFL._SDG._C.import_C import C as C_Document

import _TFL._Meta.M_Class

class Meta_Py_Object (TFL.Meta.M_Class) :
    """Meta class for Py_Object and descendents"""

    Table = {}

    count = 0

    def __init__ (cls, name, bases, dict) :
        cls.__m_super.__init__ (name, bases, dict)
        if cls.format_code :
            assert cls.format_code not in cls.Table
            cls.Table [cls.format_code] = cls
        if cls.c_types :
            cls.Table [cls.c_types] = cls
    # end def __init__

    def __call__ (cls, * args, ** kw) :
        cls.__class__.count += 1
        result = cls.__m_super.__call__ (* args, ** kw)
        return result
    # end def __call__

    def reset_count (cls) :
        cls.__call__.count = 0
    # end def reset_count

# end class Meta_Py_Object

class _Py_Object_ (object, metaclass = Meta_Py_Object) :

    format_code     = None
    c_types         = None
    py_2_c_function = None

    def __init__ (self, prefix, type_suffix) :
        self.prefix      = prefix
        self.type_suffix = type_suffix
        self.id          = self.__class__.count
        if len (self.c_types) == 1 :
            self.names = ["%s_%d" % (prefix, self.id)]
        else :
            self.names = \
                [ "%s_%d_%d" % (prefix, self.id, n)
                  for n in range (len (self.c_types))
                ]
        self.types = ["%s%s" % (ct, type_suffix) for ct in self.c_types]
    # end def __init__

    def formal_args (self) :
        return ["%s %s" % (t, n) for (t, n) in zip (self.types, self.names)]
    # end def formal_args

    def py_2_c (self, py_object) :
        assert self.py_2_c_function
        return \
            ( "* %s = %s (%s)"
            % (self.names [0], self.py_2_c_function, py_object)
            )
    # end def py_2_c

# end class _Py_Object_

class _Py_Object_Value_ (_Py_Object_) :

    def temporary (self, C, add) :
        return self.names
    # end def temporary

    def make_copy (self, C, add) :
        pass
    # end def make_copy

# end class _Py_Object_Value_

class _Py_Object_Ref_ (_Py_Object_) :

    def temporary (self, C, add) :
        t = self.c_types [0]
        n = self.names   [0]
        l = "l_%s" % (n, )
        add (C.Var (t, l))
        return ["& %s" % l] + self.names [1:]
    # end def temporary

    def make_copy (self, C, add) :
        t = self.c_types [0]
        n = self.names   [0]
        if len (self.c_types) == 1 :
            length = "strlen (l_%s) + 1" % (n, )
            add ("* %s = malloc (%s)" % (n, length))
            add ("memcpy (* %s, l_%s, %s)" % (n, n, length))
        else :
            length = self.names [-1]
            add ("* %s = malloc (* %s)" % (n, length))
            add ("memcpy (* %s, l_%s, * %s)" % (n, n, length))
    # end def make_copy

# end class _Py_Object_Ref_

class Py_String (_Py_Object_Ref_) :

    format_code   = "s"
    c_types       = ("char *", )

# end class PY_String

class Py_String_C (_Py_Object_Ref_) :

    format_code   = "s#"
    c_types       = ("char *", "int ")

# end class Py_String_C

class Py_String_E (_Py_Object_Ref_) :

    format_code   = "z"
    c_types       = ("char *", )

# end class Py_String_E

class Py_String_ES (_Py_Object_Ref_) :

    format_code   = "z#"
    c_types       = ("char *", "int ")

# end class Py_String_ES

class Py_Byte (_Py_Object_Value_) :

    format_code   = "b"
    c_types       = ("char ", )

# end class Py_Byte

class Py_Short (_Py_Object_Value_) :

    format_code   = "h"
    c_types       = ("short ", )

# end class Py_Short

class Py_Int (_Py_Object_Value_) :

    format_code   = "i"
    c_types       = ("int ", )

# end class Py_Int

class Py_Long (_Py_Object_Value_) :

    format_code     = "l"
    c_types         = ("long ", )
    py_2_c_function = "PyLong_AsLong"

# end class Py_Long

class Py_Long_Long (_Py_Object_Value_) :

    format_code   = "L"
    c_types       = ("llong ", )

# end class Py_Long_Long

class Py_Char (_Py_Object_Value_) :

    format_code   = "c"
    c_types       = ("char ", )

# end class Py_Char

class Py_Float (_Py_Object_Value_) :

    format_code   = "f"
    c_types       = ("float ", )

# end class Py_Float

class Py_Double (_Py_Object_Value_) :

    format_code   = "d"
    c_types       = ("double ", )

# end class Py_Double

class Py_Object (_Py_Object_Value_) :

    format_code   = "O"
    c_types       = ("PyObject *", )

    def make_copy (self, C, add) :
        add ("Py_INCREF (%s)" % (self.names [0], ))
    # end def make_copy

# end class Py_Object

class Py_Object_T (_Py_Object_) :

    format_code   = "O!"
    c_types       = ("PyTypeObject ", "PyObject *")

    def temporary (self, C, add) :
        raise NotImplementedError ("Py_Object_T.temporary")
    # end def temporary

    def make_copy (self, C, add) :
        raise NotImplementedError ("Py_Object_T.make_copy")
    # end def make_copy

# end class Py_Object_T

class Py2C_Wrapper :

    def __init__ (self, c_module, C) :
        assert isinstance (c_module, C.Module)
        self.c_module = c_module
        self.C        = C
    # end def __init__

    def _function (self, ret_type, name, * args, ** kw) :
        args = \
            [ (  (hasattr (a, "formal_args") and ", ".join (a.formal_args ()))
              or a
              )
              for a in args
            ]
        return self.C.Function (ret_type, name, ", ".join (args), ** kw)
    # end def _function

    def _py_fct_call (self, fct_name, obj, pars = (), head_pars = (), add = None) :
        if add :
            names = [p.temporary (self.C, add) for p in pars]
            para  = [", ".join (p) for p in names]
        else :
            para  = [", ".join (p.names) for p in pars]
        obj       = [obj]
        head_pars = list (head_pars)
        format    = ['"%s"' % ("".join ([p.format_code for p in pars]), )]
        return \
            ( "%s (%s)"
            % (fct_name, ", ".join (obj + head_pars + format + para))
            )
    # end def _py_fct_call

    def gen_constructor (self, module_name, class_name, i_format, ** kw) :
        c_module     = self.c_module
        C            = self.C
        if "function_name" in kw :
            fct_name = kw ["function_name"]
            del        kw ["function_name"]
        else :
            fct_name = "%s_init" % class_name
        i_pars       = self.parameters (i_format, "i")
        fct          = self._function ("PyObject *", fct_name, * i_pars, ** kw)
        add          = fct.add
        c_module.add ( fct)
        c_else       = C.Else ()
        add ( C.Var ("PyObject *", "py_class"))
        add ( C.If
                ( """! (py_class = C2PY_get_class ("%s", "%s"))"""
                % (module_name, class_name)
                , C.Block
                    ( """ERROR0 ("Could not get class %s from %s")"""
                    % (class_name, module_name)
                    , "return NULL"
                    )
                , c_else
                )
            , "return NULL"
            )
        add    = c_else.add
        py_fct = self._py_fct_call ("PyObject_CallFunction", "py_class", i_pars)
        add ( C.Var ("PyObject *", "instance", py_fct)
            , C.If  ("! instance", "PyErr_Print ()")
            , "return instance"
            )
    # end def gen_constructor

    def gen_method_wrapper (self, name, method, i_format = "", o_format = "", ** kw) :
        c_module = self.c_module
        C        = self.C
        i_pars   = self.parameters (i_format, "i")
        o_pars   = self.parameters (o_format, "o", "*")
        pars     = i_pars + o_pars
        result   = self._function \
            ("boolean", name, "PyObject * instance", * pars, ** kw)
        block    = C.Block ()
        guard    = C.If    ("instance", block)
        add      = result.add
        c_module.add (result)
        add (C.Var ("boolean", "ret_code", 0))
        add (guard)
        add ("return ret_code")
        add   = block.add
        in_pa = self._py_fct_call \
            ("PyObject_CallMethod", "instance", i_pars, ('"%s"' % method, ))
        add (C.Var ("PyObject *", "result",  in_pa))
        block = C.Else ()
        add   (C.If ("! result", "PyErr_Print ()", block))
        cadd  = block.add
        if o_pars :
            if len (o_pars) >= 1 :
                block = C.Block ("ret_code = 1")
                ou_pa = self._py_fct_call \
                    ("PyArg_ParseTuple", "result", o_pars, add = add)
                cadd (C.If ( ou_pa, block))
                for p in o_pars :
                    p.make_copy (C, block.add)
            else :
                cadd (o_pars [0].py_2_c ("result"), "ret_code = 1")
        else :
            cadd ("ret_code = 1")
        cadd ("Py_DECREF (result)")
        return result
    # end def gen_method_wrapper

    def parameters (self, format, prefix, type_suffix = "") :
        result = []
        add    = result.append
        for f in format.split () :
            add (_Py_Object_.Table [f] (prefix, type_suffix))
        return result
    # end def parameters

# end class Py2C_Wrapper

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Py2C_Wrapper
