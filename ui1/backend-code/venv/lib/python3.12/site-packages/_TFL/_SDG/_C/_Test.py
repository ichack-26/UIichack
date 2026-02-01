# -*- coding: utf-8 -*-
# Copyright (C) 2004-2020 TTTech Computertechnik AG. All rights reserved
# Schönbrunnerstraße 7, A--1040 Wien, Austria. office@tttech.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.SDG.C._Test
#
# Purpose
#    Module test for the C-SDG.
#
# Revision Dates
#    10-Aug-2004 (MG) Creation
#    11-Aug-2004 (MG) Creation continued
#    13-Aug-2004 (MG) Testcase update (new features in C-document)
#    23-Sep-2004 (CT) Testcase update (cosmetic fixes in eol-comments)
#    27-Sep-2004 (CT) Testcase for array with only a single element added
#    21-Oct-2004 (CT) Testcase for Macro_If in headerfile added
#    16-Nov-2004 (MG) Testcase for multidimensional arrays added
#    24-May-2005 (CED) Test of `Enum` added
#    20-Mar-2006 (MZO) Funciton requires argument
#    30-Oct-2006 (CED) Tests for `Define_Constant`, `Preprocessor_Error` added
#    17-Apr-2007 (CED) Test for `Define_Constant` adapted
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--

"""
>>> NL = chr (10)
>>> C.Comment.out_level = 5
>>> v = C.Var ("int", "test", 2)
>>> print (NL.join (v.as_c_code ()))
int test = 2;
>>> v = C.Var (name = "test", type = "short", description = "desc")
>>> print (NL.join (v.as_c_code ()))
short test;
    /* desc                                                                  */

>>> c = C.Comment ("This is a comment", stars = 2)
>>> print (NL.join (c.as_c_code ()))
/** This is a comment                                                       **/
>>> c = C.Comment ("And now a multi line", "comment with 3 stars", stars = 3)
>>> print (NL.join (c.as_c_code ()))
/*** And now a multi line                                                  ***/
/*** comment with 3 stars                                                  ***/

>>> f = C.Function ("int", "func", "int foo, short bar")
>>> print (NL.join (f.as_c_code ()).strip ())
int func
    ( int foo
    , short bar
    )
{
};

>>> f = C.Function ( "int", "func", "int foo, short bar"
...                , description = "A function description"
...                , explanation = "A function explanation"
...                )
>>> print (NL.join (f.as_c_code ()).strip ())
int func
    ( int foo
    , short bar
    )
    /*** A function description                                            ***/
{
    /*** A function explanation                                            ***/
};

>>> f = C.Function ( "int", "func", "void")
>>> f.add (C.For ("i = 0", "i++", "i < 10"))
>>> print (NL.join (f.as_c_code ()).strip ())
int func (void)
{
    for (i = 0; i++; i < 10)
      {
      };
};

>>> print (NL.join (f.as_h_code ()).strip ())
int func (void);

>>> f = C.Function ( "int", "func", "void")
>>> f.add ("i = 0")
>>> f.add (C.While ("i < 10", "i++"))
>>> f.add (C.Do_While ("i > 0", "i--"))
>>> print (NL.join (f.as_c_code ()).strip ())
int func (void)
{
    i = 0;
    while (i < 10)
      {
        i++;
      };
    do
      {
        i--;
      }
    while (i > 0);
};

>>> f = C.Function ( "int", "if_tests", "void")
>>> f.add (C.If ("i > 0", '''error ("i has the wrong value")'''))
>>> if_s = C.If ("i < 0", "cont ()")
>>> f.add (if_s)
>>> if_s.then.add ('''next_call ("in then path")''')
>>> if_s.add (C.Else ('''error ("in else path")'''))
>>> if_e = C.If ("i < 0", "cont ()")
>>> f.add (if_e)
>>> if_e.add (C.Elseif ("y > 0", '''error ("in elseif path")'''))
>>> if_e.add (C.Else ('''error ("in else path")'''))
>>> print (NL.join (f.as_c_code ()).strip ())
int if_tests (void)
{
    if (i > 0)
      {
        error ("i has the wrong value");
      };
    if (i < 0)
      {
        cont ();
        next_call ("in then path");
      }
    else
      {
        error ("in else path");
      };
    if (i < 0)
      {
        cont ();
      }
    else if (y > 0)
      {
        error ("in elseif path");
      }
    else
      {
        error ("in else path");
      };
};

>>> f = C.Function ( "void", "switch_test", "void")
>>> f.add ( C.Switch ( "quuux"
...                  , C.Case ("1", "a = 0; b = 2")
...                  , C.Case ("2", "a = 10; b = 20")
...                  , C.Default_Case ("hugo ()")
...                  )
...       )
>>> print (NL.join (f.as_c_code ()).strip ())
void switch_test (void)
{
    switch (quuux)
      {
        case 1 :
            a = 0;
            b = 2;
            break;
        case 2 :
            a = 10;
            b = 20;
            break;
        default :
            hugo ();
      };
};

>>> t = C.Typedef ("unsigend long", "ubyte4")
>>> print (NL.join (t.as_c_code ()).strip ())
typedef unsigend long ubyte4;
>>> s = C.Struct ("my_struct")
>>> s.add ("ubyte4 field_1")
>>> s.add ("sbyte2 field_2_s")
>>> t = C.Typedef (s, "my_struct")
>>> print (NL.join (t.as_c_code ()).strip ())
typedef struct _my_struct
  {
    ubyte4 field_1;
    sbyte2 field_2_s;
  } my_struct;

>>> s = C.Struct ("my_struct_stand", standalone = True)
>>> s.add ("ubyte4 field_1")
>>> s.add ("sbyte2 field_2_s")
>>> print (NL.join (s.as_c_code ()).strip ())
struct _my_struct_stand
  {
    ubyte4 field_1;
    sbyte2 field_2_s;
  };

>>> d = dict (field_1 = 10, field_2_s = 1)
>>> v = C.Var ("my_struct", "test", init_dict = d)
>>> print (NL.join (v.as_c_code ()).strip ())
my_struct test =
  { 10 /* field_1                                                            */
  , 1 /* field_2_s                                                           */
  };

>>> print (NL.join (v.as_h_code ()).strip ())
my_struct test;

>>> s = C.Struct ( "TDFT_Sign_Mask"
...              , "unsigned long bit_mask    = 42 // mask for value"
...              , "unsigned long extend_mask // mask for sign extension"
...              )
>>> a0 = C.Array ("int", "test", 1, init = (0, ))
>>> print (NL.join ([l.rstrip () for l in a0.as_c_code ()]))
int test [1] =
  { 0 /* [0]                                                                 */
  };
>>> a1 = C.Array ("int", "ar", 2, init = (0, 1), static = True)
>>> print (NL.join ([l.rstrip () for l in a1.as_c_code ()]))
static int ar [2] =
  { 0 /* [0]                                                                 */
  , 1 /* [1]                                                                 */
  };
>>> a2 = C.Array ( "TDFT_Sign_Mask", "fubars", 2
...              , init = [ dict (bit_mask = 57, extend_mask = 137)
...                       , dict (bit_mask = 142, extend_mask = -1)
...                       ]
...              )
>>> print (NL.join ([l.rstrip () for l in a2.as_c_code ()]))
TDFT_Sign_Mask fubars [2] =
  { { 57 /* bit_mask                                                         */
    , 137 /* extend_mask                                                     */
    } /* [0]                                                               */
  , { 142 /* bit_mask                                                        */
    , -1 /* extend_mask                                                      */
    } /* [1]                                                               */
  };

>>> a = C.Array ("ubyte2", "aa", (2,2), ((0,1),(2,3)))
>>> print (NL.join (a.as_c_code ()))
ubyte2 aa [2][2] =
  { { 0 /* [0][0]                                                            */
    , 1 /* [0][1]                                                            */
    } /* [0]                                                               */
  , { 2 /* [1][0]                                                            */
    , 3 /* [1][1]                                                            */
    } /* [1]                                                               */
  };
>>> d = dict (bit_mask = 42, extend_mask = 24)
>>> v = C.Var (name = "stuct_var", type = "TDFT_Sign_Mask", init_dict = d)
>>> print (NL.join ([l.rstrip () for l in v.as_c_code ()]))
TDFT_Sign_Mask stuct_var =
  { 42 /* bit_mask                                                           */
  , 24 /* extend_mask                                                        */
  };

>>> a = C.Array ("int", "int_array", bounds = 2)
>>> s = C.Struct ("test_struct", "ubyte1 field_1", "int field_2 [2]")
>>> t = C.Typedef (s, "my_type")
>>> print (NL.join ([l.rstrip () for l in t.as_c_code ()]))
typedef struct _test_struct
  {
    ubyte1 field_1;
    int field_2 [2];
  } my_type;

>>> e1 = C.Enum ("foobar", ["VALUE_A", "VALUE_B = 2", "VALUE_C"])
>>> e2 = C.Enum ("foobaz", ["VALUE_D"])
>>> t1 = C.Typedef (e1, "foobar")
>>> t2 = C.Typedef (e2, "foobaz")
>>> print (NL.join ([l.rstrip () for l in t1.as_c_code ()]))
typedef enum _foobar
  { VALUE_A
  , VALUE_B = 2
  , VALUE_C
  } foobar;

>>> print (NL.join ([l.rstrip () for l in t2.as_c_code ()]))
typedef enum _foobaz {VALUE_D} foobaz;

>>> d = C.Macro ("define foo", "", "line1", "line2")
>>> print (NL.join ([l.rstrip () for l in d.as_c_code ()]))
#define foo line1 \\
line2

>>> d = C.Define ("foo", None, "line1")
>>> print (NL.join ([l.rstrip () for l in d.as_c_code ()]))
#define foo() line1

>>> d = C.Define ("foo", "arg1", "line1")
>>> print (NL.join ([l.rstrip () for l in d.as_c_code ()]))
#define foo(arg1) line1

>>> d = C.Define ("foo", "arg1,arg2", "line1", "line2", "line3 long")
>>> print (NL.join ([l.rstrip () for l in d.as_c_code ()]))
#define foo(arg1,arg2) line1 \\
line2 \\
line3 long

>>> dc = C.Define_Constant ("foo", "42")
>>> print (NL.join ([l.rstrip () for l in dc.as_c_code ()]))
#define foo (42)

>>> e = C.Preprocessor_Error ("this is fishy")
>>> print (NL.join ([l.rstrip () for l in e.as_c_code ()]))
#error this is fishy

>>> i = C.Include ("define.h")
>>> print (NL.join ([l.rstrip () for l in i.as_c_code ()]))
#include <define.h>
>>> i = C.Sys_Include ("define.h")
>>> print (NL.join ([l.rstrip () for l in i.as_c_code ()]))
#include <define.h>
>>> i = C.App_Include ("define.h")
>>> print (NL.join ([l.rstrip () for l in i.as_c_code ()]))
#include "define.h"

>>> i = C.Macro_If ( "cond1"
...                , C.Define ("path", "", "then")
...                , C.Macro_Elseif
...                    ( "cond2"
...                    , C.Macro ("define path", "", "elseif")
...                    )
...                , C.Macro_Else (C.Define ("path", "", "else"))
...                )
>>> print (NL.join ([l.rstrip () for l in i.as_c_code ()]))
#if cond1
  #define path then
#elif cond2
  #define path elseif
#else
  #define path else
#endif /* if cond1 */

>>> print (NL.join ([l.rstrip () for l in i.as_h_code ()]))
#if cond1
  #define path then
#elif cond2
  #define path elseif
#else
  #define path else
#endif /* if cond1 */

>>> i = C.Macro_Ifdef ("cond1", C.Define ("path", "", "then"))
>>> print (NL.join ([l.rstrip () for l in i.as_c_code ()]))
#ifdef cond1
  #define path then
#endif /* ifdef cond1 */

>>> i = C.Macro_Ifndef ("cond1", C.Define ("path", "", "then"))
>>> print (NL.join ([l.rstrip () for l in i.as_c_code ()]))
#ifndef cond1
  #define path then
#endif /* ifndef cond1 */

>>> b=C.Documentation_Block ("line1", "line2", block_name = "aaa")
>>> print (NL.join ([l.rstrip () for l in b.as_c_code ()]))
/* aaa: */
/*      line1 */
/*      line2 */
"""

### missing tests
###

from   _TFL._SDG._C.import_C import C

### __END__ TFL.SDG.C._Test
