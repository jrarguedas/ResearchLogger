# !/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
#
# ResearchLogger: Python Keylogger scientific purposes in Linux and Windows
# Copyright (C) 2015  Roxana Lafuente <roxana.lafuente@gmail.com>
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
##############################################################################

import unittest
import sys
import time
import string

# For testing MyTimer
import mytimer

# For testing BaseEventClass
from configobj import ConfigObj
from tests_constants import *
from Queue import Queue
from myutils import (_settings, _cmdoptions)
from baseeventclasses import (BaseEventClass, FirstStageBaseEventClass,
                              SecondStageBaseEventClass)
from ResearchLogger import KeyLogger
from pyxhook import HookManager
from emulate_keyboard import *
from Xlib.display import Display


class TestBase(unittest.TestCase):

    # Testing environment ...
    def setUp(self):
        pass

    def tearDown(self):
        pass


def sprint(string="string"):
    """
        Simulates to write a string on the screen.
    """
    global screen
    screen += string


class TestBaseEventModule(TestBase):
    """
        Tests if a sample task_function is applied correctly to some event
        queue.
    """

    def setUp(self):
        _settings['settings'] = ConfigObj(
            {'General':
                {'Log Directory': 'logs'},
                'TestLogger': {'General': {'Log Subdirectory': 'testlog',
                                           'Log Filename': 'testlog.txt',
                                           }
                               }
             }
        )
        _cmdoptions['cmdoptions'] = {}
        self.q = Queue(0)

    def test_quick_ten_times(self):
        # Fill the queue with the events from which it pops off events.
        for i in range(10):
            self.q.put('test %d' % i)
        # The loggername is where the logs go.
        loggername = 'TestLogger'
        fsbec = FirstStageBaseEventClass('test', self.q, loggername)
        self.assertEqual(10, self.q.qsize())
        fsbec.start()
        self.assertGreaterEqual(10, self.q.qsize())
        # Debe terminar muuuuy rápido
        time.sleep(0.0007)
        fsbec.cancel()
        self.assertTrue(self.q.empty())

    def test_quick_eighteen_times_slow(self):
        # Fill the queue with the events from which it pops off events.
        for i in range(10):
            self.q.put('test %d' % i)
        # The loggername is where the logs go.
        loggername = 'TestLogger'
        fsbec = FirstStageBaseEventClass('test', self.q, loggername)
        self.assertEqual(10, self.q.qsize())
        fsbec.start()
        time.sleep(0.00001)
        for i in range(5):
            self.q.put('test %d' % i)
        time.sleep(0.00001)
        self.assertGreaterEqual(15, self.q.qsize())
        time.sleep(0.00005)
        for i in range(3):
            self.q.put('test %d' % i)
        time.sleep(0.001)
        fsbec.cancel()
        self.assertTrue(self.q.empty())


class TestMyTimer(TestBase):
    """
        Before SECONDS passes, screen should be empty.
        After a SECONDS, it should contain 'string' TIMES times.
        Where SECONDS is the time it waits until the function is released and
        TIMES is the number of repetitions to be executed.
    """

    def setUp(self):
        global screen
        screen = ''

    def test_one_time(self):
        myt = mytimer.MyTimer(0.005, 1, sprint)
        self.assertIsNotNone(myt)
        myt.start()
        self.assertEqual(screen, '')
        time.sleep(0.005 * 2)
        myt.cancel()
        self.assertEqual(screen, 'string')

    def test_ten_times(self):
        myt = mytimer.MyTimer(0.005, 10, sprint)
        self.assertIsNotNone(myt)
        myt.start()
        self.assertEqual(screen, '')
        time.sleep(0.005 * 11)
        myt.cancel()
        self.assertEqual(screen, 'string' * 10)

    def test_infinite_times(self):
        myt = mytimer.MyTimer(0.0005, 0, sprint)
        self.assertIsNotNone(myt)
        myt.start()
        self.assertEqual(screen, '')
        time.sleep(1)
        myt.cancel()
        times = screen.count("string")
        self.assertGreaterEqual(times, 10)


class TestPyxHook(TestBase):
    """
        Tests the pyxhook library for Linux.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Key generator.
    def generator(self, s, key=None):
        for i in range(len(s)):
            if key is not None:
                yield key
            if s[i] in specialKeysyms.keys():
                yield specialKeysyms[s[i]]
            else:
                yield s[i]

    def reportevent(self, event):
        # It's not case sensitive.
        ek = string.lower(event.Key)
        ngn = string.lower(next(self.gn))
        # We don't care about underscores.
        ngn = string.replace(ngn, "_", "")
        print ek, ngn
        self.assertEqual(ek, ngn)

    def base_test(self):
        self.hm = HookManager()
        self.hm.HookKeyboard()
        self.hm.HookMouse()
        self.hm.KeyDown = self.reportevent
        self.hm.MouseAllButtonsDown = self.reportevent
        self.hm.MouseAllButtonsUp = self.reportevent
        self.hm.start()
        d = Display()

    def test_numbers(self):
        numbers = '0123456789'
        self.gn = self.generator(numbers)
        self.base_test()
        emulateWritingString(d, numbers, 0.075)  # 75ms
        self.hm.cancel()

    def test_lowercase(self):
        lc = u'abcdefghijklmnopqrstuvwxyz'
        self.gn = self.generator(lc)
        self.base_test()
        emulateWritingString(d, lc, 0.075)  # 75ms
        self.hm.cancel()

    def test_uppercase(self):
        uc = u'abcdefghijklmnopqrstuvwxyz'
        self.gn = self.generator(uc, 'shift_l')
        self.base_test()
        emulateWritingString(d, string.upper(uc), 0.075)  # 75ms
        self.hm.cancel()

    def test_simple_symbols(self):
        uc = u"º'¡\t\n<+ç"  # \r
        self.gn = self.generator(uc)
        self.base_test()
        emulateWritingString(d, uc, 0.075)  # 75ms
        self.hm.cancel()

    def test_simple_combos_symbols(self):
        keys = ['shift_l', 'shift_r', 'alt_l']
        for key in keys:
            ss = u"2"
            self.gn = self.generator(ss, key)
            self.base_test()
            emulateWritingString(d, ss, 0.075, key)  # 75ms
            self.hm.cancel()


def suite():
    suite = unittest.TestSuite()

    # Module Testing
    suite.addTest(unittest.makeSuite(TestBaseEventModule))
    suite.addTest(unittest.makeSuite(TestMyTimer))
    suite.addTest(unittest.makeSuite(TestPyxHook))

    # Functionality Testing
    suite.addTest(unittest.makeSuite(TestKeylogger))

    return suite


def main():
    import optparse
    global PATH
    parser = optparse.OptionParser()
    parser.set_usage("%prog [opciones] [clases de tests]")
    parser.add_option('-d', '--datadir', help="Directorio donde genera los datos; El log se borra en cada corrida de tests", default=PATH)
    options, args = parser.parse_args()
    PATH = options.datadir
    # Runs tests
    unittest.main(verbosity=2, argv=sys.argv[0:1] + args)

if __name__ == '__main__':
    main()
