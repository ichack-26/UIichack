# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Martin Glueck All rights reserved
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
#    TFL.Babel._Test
#
# Purpose
#    Test file which will be parsed.
#
# Revision Dates
#    15-Apr-2010 (MG) Creation
#    10-Oct-2016 (CT) Make Python-3 compatible
#    ««revision-date»»···
#--

from   _TFL.I18N import _, _T, _Tn, Translations, Config
import  os

_ ("Just markup")
print (_T  ("Markup and translation"))
print (_Tn ("Singular", "Plural", 2))

path  = os.path.join (os.path.dirname (__file__), "-I18N", "de.mo")
Config.current = Translations (open (path), "messages")

print ("_T tests")
print (_T  ("Just markup"))
print (_T  ("Markup and translation"))
print (_T  ("Singular"))
print (_T  ("Plural"))
print ("_Tn tests")
print (_Tn ("Singular", "Plural", 0))
print (_Tn ("Singular", "Plural", 1))
print (_Tn ("Singular", "Plural", 2))

### __END__ TFL.Babel._Test
