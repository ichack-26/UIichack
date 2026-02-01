# -*- coding: utf-8 -*-
# Copyright (C) 2015-2017 Christian Tanzer All rights reserved
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
#    json_dump
#
# Purpose
#    Generic function for `default` argument of `json.dump`, `json.dumps`
#
# Revision Dates
#    13-Apr-2015 (CT) Creation
#     6-May-2015 (CT) Add `to_file`, `to_open_file`, `to_string`
#     6-May-2015 (CT) Add `add_date_time_serializers`
#    16-Jul-2015 (CT) Use `expect_except` in doc-tests
#    22-Oct-2015 (CT) Add workaround for Python-3 issue25457 (`_fix_keys`)
#    14-Aug-2017 (CT) Change `to_file` to pass `w`, not `wb`, for `open`
#                     * Python-3 `json` always produces str objects, not byte
#    ««revision-date»»···
#--

from   _TFL              import TFL
from   _TFL.pyk          import pyk

import _TFL._Meta.Single_Dispatch

import json
import sys

__date_time_serializers_added = False

def add_date_time_serializers () :
    """Add json serializers for `datetime.date`, `.datetime`, and `.time`."""
    if not __date_time_serializers_added :
        TFL.json_dump.__date_time_serializers_added = True
        import datetime
        @default.add_type (datetime.date, datetime.time)
        def json_encode_date_or_time (o) :
            return o.isoformat ()
        # end def json_encode_date_or_time

        @default.add_type (datetime.datetime)
        def json_encode_datetime (dt) :
            ### Don't use `isoformat` because its output structure varies
            ### depending on `microsecond` and is thus more difficult to parse
            return dt.strftime ("%Y-%m-%dT%H:%M:%S.%f")
        # end def json_encode_datetime
# end def add_date_time_serializers

@TFL.Meta.Single_Dispatch
def default (o) :
    """Generic function to serialize `o` as json-compatible type.

       Pass `default` to `json.dump` or `json.dumps`.
    """
    raise TypeError (repr (o) + " is not JSON serializable")
# end def default

### workaround http://bugs.python.org/issue25457
__keys_need_fixing = sys.version_info >= (3, )

if __keys_need_fixing :
    ### workaround http://bugs.python.org/issue25457
    @TFL.Meta.Single_Dispatch
    def _fix_keys (o) :
        return o
    # end def _fix_keys

    @_fix_keys.add_type (dict)
    def _fix_keys_dict (dct) :
        return dict (_fix_keys_dict_iter (dct))
    # end def _fix_keys_dict

    def _fix_keys_dict_iter (dct) :
        for k, v in pyk.iteritems (dct) :
            if isinstance (k, (int, float)) :
                k = str (k).lower () ### `.lower` because `bool`
            elif k is None :
                k = "null"
            yield k, _fix_keys (v)
    # end def _fix_keys_dict_iter

    @_fix_keys.add_type (list, tuple)
    def _fix_keys_seq (seq) :
        return seq.__class__ (_fix_keys (v) for v in seq)
    # end def _fix_keys_seq

def _do_dump (dumper, cargo, * args, ** kw) :
    try :
        return dumper (cargo, * args, ** kw)
    except TypeError :
        if __keys_need_fixing and kw.get ("sort_keys") :
            cargo = _fix_keys (cargo)
            return dumper (cargo, * args, ** kw)
        raise
# end def _do_dump

def to_file (cargo, file_name, default = default, sort_keys = True, ** kw) :
    """Serialize `cargo` as a JSON formatted stream to a file name `file_name`.

       By default, use `TFL.json_dump.default` as serializer function and sort
       output of dictionaries by key.

       The arguments have the same meaning as in `json.dump`.
    """
    with open (file_name, "w") as fp :
        return _do_dump \
            ( json.dump, cargo, fp
            , default = default, sort_keys = sort_keys, ** kw
            )
# end def to_file

def to_open_file (cargo, fp, default = default, sort_keys = True, ** kw) :
    """Serialize `cargo` as a JSON formatted stream to `fp` (a .write()-supporting file-like object).

       By default, use `TFL.json_dump.default` as serializer function and sort
       output of dictionaries by key.

       The arguments have the same meaning as in `json.dump`.
    """
    return _do_dump \
        (json.dump, cargo, fp, default = default, sort_keys = sort_keys, ** kw)
# end def to_open_file

def to_string (cargo, default = default, sort_keys = True, ** kw) :
    """Serialize `cargo` to a JSON `str`.

       By default, use `TFL.json_dump.default` as serializer function and sort
       output of dictionaries by key.

       The arguments have the same meaning as in `json.dump`.
    """
    return _do_dump \
        (json.dumps, cargo, default = default, sort_keys = sort_keys, ** kw)
# end def to_string

__doc__ = """
This modules provides functions to customize json serialization.

.. function:: default(o)

  Return `o` serialized in a format usable as json or raise a TypeError.

  `default` is a generic function that can be specialized for specific
  types. For instance::

      @default.add_type (datetime.date)
      def json_encode_date (o) :
          return str (o)

.. autofunction:: add_date_time_serializers

.. autofunction:: to_file(cargo, file_name, default = 'default', sort_keys = True, ** kw)

.. autofunction:: to_open_file(cargo, fp, default = 'default', sort_keys = sort_keys, ** kw)

.. autofunction:: to_string(cargo, default = 'default', sort_keys = True, ** kw)

Examples::

    >>> import datetime
    >>> dt = datetime.datetime (2015, 5, 6, 12, 50)

    >>> with expect_except (TypeError) :
    ...     print (to_string (dt))
    TypeError: datetime.datetime(2015, 5, 6, 12, 50) is not JSON serializable

    >>> add_date_time_serializers ()
    >>> print (to_string (dt))
    "2015-05-06T12:50:00.000000"

    >>> mixed_keys = [
    ...   { None: "nada", 23 : 42, "foo" : "bar" , True : False, False : True}]
    >>> (to_string (mixed_keys) ==
    ... '[{"23": 42, "false": true, "foo": "bar", "null": "nada", "true": false}]'
    ... if __keys_need_fixing else True)
    True

    >>> (to_string (mixed_keys) ==
    ... '[{"null": "nada", "false": true, "true": false, "23": 42, "foo": "bar"}]'
    ... if not __keys_need_fixing else True)
    True

"""

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ json_dump
