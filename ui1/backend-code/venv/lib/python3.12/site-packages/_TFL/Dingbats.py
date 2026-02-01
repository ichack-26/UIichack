# -*- coding: utf-8 -*-
# Copyright (C) 2014-2020 Christian Tanzer All rights reserved
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
#    TFL.Dingbats
#
# Purpose
#    Dingbats as unicode characters
#
# Revision Dates
#    13-Feb-2014 (CT) Creation
#    20-Feb-2014 (CT) Sort dingbats by name
#    20-Feb-2014 (CT) Add `trigram_for_heaven`
#    13-Mar-2014 (CT) Add some symbols for triangles and blocks
#    23-Jan-2015 (CT) Add some symbols for various space characters
#    29-Jun-2016 (CT) Add `infinity`
#     4-Jan-2017 (CT) Add `white...triangle` symbols (geometric_shapes)
#     4-Jan-2017 (CT) Add some miscellaneous_technical symbols
#    20-Aug-2017 (CT) Add astronomical symbols (earth, moon, star, sun)
#    29-Sep-2017 (CT) Add `*cloud*` and `rain`
#    24-May-2020 (CT) Add `__main__` to display glyphs
#     3-Jun-2020 (CT) Base on new module `TFL.UCD`
#    ««revision-date»»···
#--

from   _TFL       import TFL
from   _TFL.UCD   import UCD, id_to_chr_map

### http://www.unicode.org/charts/PDF/U2700.pdf
### http://www.alanwood.net/unicode/dingbats.html
### http://www.alanwood.net/unicode/geometric_shapes.html
### http://www.alanwood.net/unicode/block_elements.html
### http://www.alanwood.net/unicode/mathematical_operators.html
### http://www.alanwood.net/unicode/miscellaneous_symbols.html
### http://www.alanwood.net/unicode/miscellaneous_technical.html

def __dir__ () :
    return sorted (id_to_chr_map)
# end def __dir__

def __getattr__ (name) :
    if name.startswith ("_") :
        raise AttributeError
    globs  = globals ()
    result = globs [name] = UCD [name]
    return result
# end def __getattr__

if __name__ != "__main__" :
    TFL._Export_Module ()
else :
    from _TFL import Dingbats
    for name in __dir__ () :
        x = getattr (Dingbats, name, None)
        if isinstance (x, str) :
            print ("%-60s : %s" % (name, x))
### __END__ TFL.Dingbats
