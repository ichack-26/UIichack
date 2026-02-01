# -*- coding: utf-8 -*-
# Copyright (C) 2002-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Generators
#
# Purpose
#    Provide useful generators
#
# Revision Dates
#    18-Apr-2002 (CT) Creation
#    19-Apr-2002 (CT) `Lazy_List` added
#    29-Jul-2002 (CT) s/paired/paired_zip/
#     6-Oct-2003 (CT) s/paired/paired_zip/ in doc-string, too
#     9-Mar-2004 (CT) `_doc_test` changed to not use `import`
#    30-Jul-2004 (CT) `Look_Ahead_Gen` added
#    30-Jul-2004 (CT) `pairwise` changed to use `Look_Ahead_Gen`
#    12-Aug-2004 (CT) Additional doctest for `Look_Ahead_Gen` added to show
#                     behavior for single element sequence
#    21-Sep-2004 (CT) `Look_Ahead_Gen` changed to call `.next` lazily instead
#                     of (over)-eagerly
#    26-Oct-2004 (CT) `alt_iter` added
#    24-Mar-2005 (CT) Cruft removed
#     1-Jul-2005 (CT) `pairwise_circle` defined here
#     8-Dec-2006 (CT) `window_wise` added
#    16-Feb-2007 (CT) `enumerate_slice` added
#     1-Mar-2007 (CT) Adapted to signature change of `DL_Ring`
#     3-Nov-2009 (CT) `paired_map` fixed, `paired_zip` removed
#    11-Nov-2009 (CT) Exception handler changed for 3-compatibility
#    22-Feb-2013 (CT)  Use `TFL.Undef ()` not `object ()`
#    12-Jun-2013 (CT) Add `bool_split_iters`
#     7-Oct-2014 (CT) Change `paired_map` not to use `len`
#    16-Oct-2015 (CT) Add `__future__` imports
#    24-Feb-2017 (CT) Add `iter_split`
#    16-May-2017 (CT) Add property `succ` to `Look_Ahead_Gen`
#    11-Jul-2018 (CT) Add guards for `StopIteration`, `RuntimeError`
#                     + Python 3.7 breakage due to PEP 479
#    19-Aug-2019 (CT) Use `print_prepr`
#    ««revision-date»»···
#--

from   _TFL             import TFL
from   _TFL.pyk         import pyk

import _TFL.Undef

import itertools

def alt_iter (* iterables) :
    """Alternating iterator

       >>> s1 = range (4)
       >>> s2 = [chr (i + 65) for i in range (3)]
       >>> s3 = range (42, 55, 3)
       >>> _show (alt_iter ())
       []
       >>> _show (alt_iter (s1))
       [0, 1, 2, 3]
       >>> _show (alt_iter (s1, s2))
       [0, 'A', 1, 'B', 2, 'C', 3]
       >>> _show (alt_iter (s2, s1))
       ['A', 0, 'B', 1, 'C', 2, 3]
       >>> _show (alt_iter (s1, s2, s3))
       [0, 'A', 42, 1, 'B', 45, 2, 'C', 48, 3, 51, 54]
    """
    iters = [iter (x) for x in iterables]
    while iters :
        i = 0
        while i < len (iters) :
            try :
                yield next (iters [i])
            except StopIteration :
                del iters [i]
            else :
                i += 1
# end def alt_iter

def bool_split_iters (seq, predicate = bool) :
    """Return an iterator pair yielding the false, respectively true,
       elements of `seq`, as determined by `predicate`

    >>> seq = list (range (10))
    >>> _show (list (x) for x in bool_split_iters (seq))
    [[0], [1, 2, 3, 4, 5, 6, 7, 8, 9]]
    >>> _show (list (x) for x in bool_split_iters (seq, lambda i : i % 2))
    [[0, 2, 4, 6, 8], [1, 3, 5, 7, 9]]
    >>> _show (list (x) for x in bool_split_iters (seq, lambda i : i % 3))
    [[0, 3, 6, 9], [1, 2, 4, 5, 7, 8]]
    >>> _show (list (x) for x in bool_split_iters (seq, lambda i : i < 5))
    [[5, 6, 7, 8, 9], [0, 1, 2, 3, 4]]

    """
    a, b = itertools.tee ((predicate (x), x) for x in seq)
    f_it = (x for (p, x) in a if not p)
    t_it = (x for (p, x) in b if p)
    return f_it, t_it
# end def bool_split_iters

class Look_Ahead_Gen (object) :
    """Wrap a generator/iterator to provide look ahead

       >>> for i in Look_Ahead_Gen (range (3)) :
       ...   print (i)
       ...
       0
       1
       2
       >>> lag = Look_Ahead_Gen (range (1))
       >>> for i in lag :
       ...   print (i, lag.is_finished)
       ...
       0 True
       >>> lag = Look_Ahead_Gen (range (3))
       >>> for i in lag :
       ...   print (i, lag.succ, lag.is_finished)
       ...
       0 1 False
       1 2 False
       2 <Undef/sentinel> True
    """

    is_finished        = property (lambda s : not s)

    def __init__ (self, source) :
        self.source    = source     = iter (source)
        self._sentinel = self._succ = TFL.Undef ("sentinel")
    # end def __init__

    @property
    def succ (self) :
        if self._succ is self._sentinel :
            try :
                self._succ = next (self.source)
            except StopIteration :
                return self._sentinel
        return self._succ
    # end def succ

    def __bool__ (self) :
        try :
            if self._succ is self._sentinel :
                self._succ = next (self.source)
        except StopIteration :
            return False
        return True
    # end def __bool__

    def __iter__ (self) :
        source    = self.source
        _sentinel = self._sentinel
        while True :
            if self._succ is _sentinel :
                try :
                    succ   = next (source)
                except StopIteration :
                    break
            else :
                succ       = self._succ
                self._succ = _sentinel
            yield succ
    # end def __iter__

# end class Look_Ahead_Gen

def enumerate_slice (seq, head, tail = None) :
    """Generate `index, value` pairs for slice `seq [head:tail]`.

       >>> _show (enumerate_slice (range (7), 0))
       [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)]
       >>> _show (enumerate_slice (range (20), 5, 10))
       [(5, 5), (6, 6), (7, 7), (8, 8), (9, 9)]
       >>> _show (enumerate_slice ("abcdefghijklmnopqrstuvwxyz", 20))
       [(20, 'u'), (21, 'v'), (22, 'w'), (23, 'x'), (24, 'y'), (25, 'z')]
    """
    i = head
    for v in seq [head:tail] :
        yield i, v
        i += 1
# end def enumerate_slice

def Indices (seq) :
    """Generates indices of sequence `seq`.

       >>> _show (Indices ("abcdef"))
       [0, 1, 2, 3, 4, 5]
    """
    return Integers (len (seq))
# end def Indices

def Integers (n) :
    """Generates integers from 0 to `n`."""
    i = 0
    while i < n :
        yield i
        i += 1
# end def Integers

def iter_split (iterable, pred, T = tuple) :
    """Generate subsets of `iterable` with elements for which `pred` is True.

    If `pred` isn't callable, it is assumed to be the delimiter between the
    groups.

    The subsets are instances of `T`.

    >>> _show (iter_split (["check", "--", "test"], lambda a : a != "--"))
    [('check',), ('test',)]

    >>> _show (iter_split (["check", "--", "test"], "--", list))
    [['check'], ['test']]

    """
    if not callable (pred) :
        sep  = pred
        pred = lambda elem : elem != sep
    it = Look_Ahead_Gen (iterable)
    while it :
        yield T (itertools.takewhile (pred, it))
# end def iter_split

def pairwise (seq) :
    """Generates a list of pairs `(seq [0:1], seq [1:2], ..., seq [n-1:n])`.

       >>> _show (pairwise ("abcdef"))
       [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'), ('e', 'f')]
       >>> _show (pairwise (range (4)))
       [(0, 1), (1, 2), (2, 3)]
       >>> _show (pairwise ([1]))
       []
       >>> _show (pairwise ([]))
       []
    """
    lag = Look_Ahead_Gen (seq)
    for h in lag :
        if lag :
            yield h, lag.succ
# end def pairwise

def pairwise_circle (seq) :
    """Generates a list of pairs of a circle of iterable `seq`

       >>> _show (pairwise_circle ([1, 2, 3, 4, 5]))
       [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)]
       >>> _show (pairwise_circle ([1, 2]))
       [(1, 2), (2, 1)]
       >>> _show (pairwise_circle ([1]))
       [(1, 1)]
       >>> _show (pairwise_circle ([]))
       []
    """
    lag = Look_Ahead_Gen (seq)
    if lag :
        head = lag.succ
        for h in lag :
            if lag :
                yield h, lag.succ
        yield h, head ### close circle
# end def pairwise_circle

def paired_map (s1, s2) :
    """Generates a list of pairs `((s1 [0], s2 [0]), ... (s1 [-1], s2 [-1]))`.

       >>> _show (paired_map ("", []))
       []
       >>> _show (paired_map ("abc", range (4)))
       [('a', 0), ('b', 1), ('c', 2), (None, 3)]
       >>> _show (paired_map ("abc", range (3)))
       [('a', 0), ('b', 1), ('c', 2)]
       >>> _show (paired_map ("abc", range (2)))
       [('a', 0), ('b', 1), ('c', None)]
    """
    def _gen (s) :
        for x in s :
            yield x, True
        while True :
            yield None, False
    for (l, next_l), (r, next_r) in zip (_gen (s1), _gen (s2)) :
        if not (next_l or next_r) :
            break
        yield l, r
# end def paired_map

class Lazy_List :
    """List evalatuing a generator lazily.

       Idea stolen from Lib/test/test_generators.py of Python 2.2

       >>> def ones () :
       ...     while True :
       ...         yield 1
       ...
       >>> ol = Lazy_List (ones ())
       >>> ol [3]
       1
       >>> ol [0]
       1
       >>> ol [:7]
       [1, 1, 1, 1, 1, 1, 1]
       >>> ol [100:102]
       [1, 1]
       >>> def range_5 () :
       ...     for i in range (5) :
       ...         yield i
       ...
       >>> rl = Lazy_List (range_5 ())
       >>> rl [3]
       3
       >>> try :
       ...     rl [5]
       ... except IndexError :
       ...     print ("OK")
       ...
       OK
       >>> rl [::2]
       [0, 2, 4]
    """

    def __init__ (self, generator) :
        self._data = []
        self._next = lambda : next (generator)
    # end def __init__

    def __getitem__ (self, i) :
        try :
            last = i.stop
        except AttributeError :
            try :
                self._get (i + 1)
            except StopIteration :
                raise IndexError (i)
            return self._data [i]
        else :
            try :
                self._get (last)
            except StopIteration :
                pass
            return self._data [i.start:i.stop:i.step]
    # end def __getitem__

    def _get (self, last) :
        data = self._data
        next = self._next
        while last and last > len (data) :
            data.append (next ())
    # end def _get

# end class Lazy_List

def window_wise (seq, size) :
    """Return all windows of `size` elements in `seq`.

       >>> _show (window_wise (range (5), 1))
       [(0,), (1,), (2,), (3,), (4,)]
       >>> _show (window_wise (range (5), 2))
       [(0, 1), (1, 2), (2, 3), (3, 4)]
       >>> _show (window_wise (range (5), 3))
       [(0, 1, 2), (1, 2, 3), (2, 3, 4)]
       >>> _show (window_wise (range (5), 4))
       [(0, 1, 2, 3), (1, 2, 3, 4)]
       >>> _show (window_wise (range (5), 5))
       [(0, 1, 2, 3, 4)]
       >>> _show (window_wise (range (5), 6))
       []
    """
    from _TFL.DL_List import DL_Ring
    s = iter  (seq)
    try :
        h = tuple ((next (s) for i in range (size)))
    except RuntimeError :
        pass
    else :
        if len (h) == size :
            w = DL_Ring (h)
            yield tuple (w.values ())
            while True:
                w.pop_front ()
                try :
                    nxt = next (s)
                except StopIteration :
                    break
                else :
                    w.append    (nxt)
                    yield tuple (w.values ())
# end def window_wise

def _show (it) :
    from _TFL.portable_repr import print_prepr
    print_prepr (list (it))
# end def _show

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Generators
