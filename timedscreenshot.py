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

from myutils import to_unicode
from Queue import Empty
from threading import Event
import os
import os.path
import logging
import time
import re
import sys
import datetime
import pyautogui
if os.name == 'nt' or os.name == 'posix':
    pass
else:
    print "OS is not recognised as windows or linux"
    sys.exit()
from baseeventclasses import (FirstStageBaseEventClass,
                              SecondStageBaseEventClass)
from onclickimagecapture import Point
from constants import IMG_SET, TIMEDATE


class TimedScreenshotFirstStage(FirstStageBaseEventClass):
    '''
        Takes screenshots at fixed interval.

        Only if any user keyboard or mouse activity is detected in between.
        Does not count mouse motion, only clicks.

        Sets the secondstage event to notify of activity.
    '''

    def __init__(self, username, *args, **kwargs):

        FirstStageBaseEventClass.__init__(self, username, *args, **kwargs)

        self.task_function = self.process_event

    def process_event(self):
        try:
            # Need the timeout so that thread terminates properly when exiting.
            event = self.q.get(timeout=0.05)
            self.sst_q.set()
            self.logger.debug("User activity detected")
        except Empty:
            pass  # let's keep iterating
        except:
            self.logger.debug("some exception was caught in "
                              "the logwriter loop...\nhere it is:\n",
                              exc_info=True)
            pass  # let's keep iterating

    def spawn_second_stage_thread(self):
        self.sst_q = Event()
        self.sst = TimedScreenshotSecondStage(self.username, self.dir_lock,
                                              self.sst_q, self.loggername)


class TimedScreenshotSecondStage(SecondStageBaseEventClass):

    def __init__(self, username, dir_lock, *args, **kwargs):
        SecondStageBaseEventClass.__init__(self, username, dir_lock, *args, **kwargs)
        self.task_function = self.process_event
        self.logger = logging.getLogger(self.loggername)
        self.sleep_counter = 0

    def process_event(self):
        try:
            # Break up the sleep into short bursts, to allow for quick
            # and clean exit.
            time.sleep(0.05)
            self.sleep_counter += 0.05
            if self.sleep_counter > \
                    self.subsettings['General']['Screenshot Interval']:
                if self.q.isSet():
                    self.logger.debug("capturing timed screenshot...")
                    try:
                        savefilename = os.path.join(
                            self.settings['General']['Log Directory'],
                            self.subsettings['General']['Log Subdirectory'],
                            self.parse_filename())
                        self.capture_image(savefilename)
                        self.write_to_logfile(savefilename)
                    finally:
                        self.q.clear()
                        self.sleep_counter = 0

        except:
            self.logger.debug("some exception was caught in the "
                              "screenshot loop...\nhere it is:\n",
                              exc_info=True)
            pass  # let's keep iterating

    def write_to_logfile(self, savefilename):
        # TODO: Do not hardcode pipe
        self.logger.info(str(time.time()) + "|" + savefilename)

    def capture_image(self, savefilename):
        image_data = pyautogui.screenshot()
        image_data.save(savefilename)

    def parse_filename(self):
        filepattern = self.subsettings['General']['Screenshot Image Filename']
        fileextension = self.subsettings['General']['Screenshot Image Format']
        filepattern = re.sub(r'%time%',
                             datetime.datetime.today().strftime(TIMEDATE) +
                             str(datetime.datetime.today().microsecond),
                             filepattern)
        filepattern = filepattern + '.' + fileextension
        return filepattern