# -*- coding: utf-8 -*-
# Copyright (C) 2009-2014 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.FCM
#
# Purpose
#    Provide context managers for handling files safely
#
# Revision Dates
#    18-Mar-2009 (CT) Creation
#     1-Jun-2012 (CT) Add `import` of `traceback` to `open_to_replace`
#     1-Oct-2014 (CT) Add `temp_dir`
#    ««revision-date»»···
#--

from   _TFL                import TFL
from   _TFL                import sos

import _TFL.Decorator

import errno
import tempfile

@TFL.Contextmanager
def open_fsynced (file_name, mode = "w", buffering = -1) :
    """Context manager that opens `file_name` and will `fsync` it before
       closing.
    """
    with open (file_name, mode, buffering) as file :
        try :
            yield file
        finally :
            file.flush ()
            sos.fsync  (file.fileno ())
# end def open_fsynced

@TFL.Contextmanager
def open_tempfile (mode = "w", buffering = -1, suffix = "", prefix = "", dir = "", auto_remove = True, create_dir = False) :
    """Context manager that opens a temporary file."""
    if create_dir and not sos.path.isdir (dir) :
        sos.mkdir (dir)
    fd, temp_name = tempfile.mkstemp \
        (suffix = suffix, prefix = prefix, dir = dir, text = "t" in mode)
    try :
        file = sos.fdopen (fd, mode, buffering)
    except :
        sos.close  (fd)
        sos.remove (temp_name)
        raise
    else :
        try :
            try :
                yield (file, temp_name)
            except :
                if sos.path.exists (temp_name) :
                    sos.remove (temp_name)
                raise
        finally :
            if not file.closed :
                file.close ()
            if auto_remove and sos.path.exists (temp_name) :
                sos.remove (temp_name)
# end def open_tempfile

@TFL.Contextmanager
def open_to_replace (file_name, mode = "w", buffering = -1, backup_name = None) :
    """Context manager that opens a file with a temporary name and renames it
       to `file_name` after syncing and closing. If `backup_name` is
       specified, the old file is renamed to `backup_name`.
    """
    dir, name = sos.path.split (file_name)
    with open_tempfile (mode, buffering, prefix = name, dir = dir) as \
             (file, temp_name) :
        yield file
        file.flush ()
        sos.fsync  (file.fileno ())
        file.close ()
        if backup_name :
            try :
                sos.rename (file_name, backup_name)
            except sos.error as exc :
                if exc.args [0] != errno.ENOENT :
                    import traceback
                    traceback.print_exc ()
        sos.rename (temp_name, file_name)
# end def open_to_replace

@TFL.Contextmanager
def temp_dir (suffix = "", prefix = "tmp", dir = "/tmp", auto_remove = True) :
    """Context manager that creates a temporary directory."""
    temp_dir_path = tempfile.mkdtemp \
        (suffix = suffix, prefix = prefix, dir = dir)
    try :
        yield temp_dir_path
    finally :
        if auto_remove and sos.path.exists (temp_dir_path) :
            sos.rmdir (temp_dir_path, deletefiles = True)
# end def temp_dir

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.FCM
