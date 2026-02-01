# -*- coding: utf-8 -*-
# Copyright (C) 2001-2006 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.primes_1
#
# Purpose
#    Provide list of prime numbers up to 10
#
# Revision Dates
#    25-Mar-2001 (CT) Creation
#    11-Feb-2006 (CT) Moved into package `TFL`
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    ««revision-date»»···
#--



from _TFL.Primes        import Primes

primes = Primes ((2, 3, 5, 7))

### __END__ TFL.primes_1
