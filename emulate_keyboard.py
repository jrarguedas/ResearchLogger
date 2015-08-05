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

import os
import time

# Ubuntu
if os.name == 'posix':

    from Xlib.display import Display
    from Xlib.ext import xtest
    from Xlib import X, XK

    d = Display()

    # Mapeo entre strings y keycodes.
    # Mapeo entre strings y keycodes.
    kmap = {u'shift_l': d.keysym_to_keycode(XK.XK_Shift_L),
            u'shift_r': d.keysym_to_keycode(XK.XK_Shift_R),
            u'ctrl_l': d.keysym_to_keycode(XK.XK_Control_L),
            u'ctrl_r': d.keysym_to_keycode(XK.XK_Control_R),
            u'alt_l': d.keysym_to_keycode(XK.XK_Alt_L),
            u'alt_r': d.keysym_to_keycode(XK.XK_Alt_R),
            u'f12': d.keysym_to_keycode(XK.XK_F12),
            u'.': d.keysym_to_keycode(XK.XK_period),
            u' ': d.keysym_to_keycode(XK.XK_space),
            u'down': d.keysym_to_keycode(XK.XK_Down),
            u'up': d.keysym_to_keycode(XK.XK_Up),
            u'right': d.keysym_to_keycode(XK.XK_Right),
            u'left': d.keysym_to_keycode(XK.XK_Left),
            u'^': d.keysym_to_keycode(XK.XK_asciicircum),
            u'á': d.keysym_to_keycode(XK.XK_Aacute),
            u'`': d.keysym_to_keycode(XK.XK_grave),
            u'´': d.keysym_to_keycode(XK.XK_acute),
            u'\t': d.keysym_to_keycode(XK.XK_Tab),
            u'\n': d.keysym_to_keycode(XK.XK_Return),
            u'\r': d.keysym_to_keycode(XK.XK_Return),
            u'\e': d.keysym_to_keycode(XK.XK_Escape),
            u'!': d.keysym_to_keycode(XK.XK_exclam),
            u'#': d.keysym_to_keycode(XK.XK_numbersign),
            u'%': d.keysym_to_keycode(XK.XK_percent),
            u'$': d.keysym_to_keycode(XK.XK_dollar),
            u'&': d.keysym_to_keycode(XK.XK_ampersand),
            u'"': d.keysym_to_keycode(XK.XK_quotedbl),
            u'\'': d.keysym_to_keycode(XK.XK_apostrophe),
            u'(': d.keysym_to_keycode(XK.XK_parenleft),
            u')': d.keysym_to_keycode(XK.XK_parenright),
            u'*': d.keysym_to_keycode(XK.XK_asterisk),
            u'+': d.keysym_to_keycode(XK.XK_plus),
            u',': d.keysym_to_keycode(XK.XK_comma),
            u'-': d.keysym_to_keycode(XK.XK_minus),
            u'/': d.keysym_to_keycode(XK.XK_slash),
            u'\\': d.keysym_to_keycode(XK.XK_backslash),
            u':': d.keysym_to_keycode(XK.XK_colon),
            u';': d.keysym_to_keycode(XK.XK_semicolon),
            u'<': d.keysym_to_keycode(XK.XK_less),
            u'>': d.keysym_to_keycode(XK.XK_greater),
            u'=': d.keysym_to_keycode(XK.XK_equal),
            u'?': d.keysym_to_keycode(XK.XK_question),
            u'@': d.keysym_to_keycode(XK.XK_at),
            u'[': d.keysym_to_keycode(XK.XK_bracketleft),
            u']': d.keysym_to_keycode(XK.XK_bracketright),
            u'_': d.keysym_to_keycode(XK.XK_underscore),
            u'º': d.keysym_to_keycode(XK.XK_masculine),
            u'¡': d.keysym_to_keycode(XK.XK_exclamdown),
            u'ñ': d.keysym_to_keycode(XK.XK_ntilde),
            u'ç': d.keysym_to_keycode(XK.XK_ccedilla)
            }

    # Mapeo entre strings y keysyms (solo de caracteres especiales).
    specialKeysyms = {u' ': "space",
                      u'\t': "tab",
                      u'\n': "return",
                      u'!': "exclam",
                      u'#': "numbersign",
                      u'%': "percent",
                      u'$': "dollar",
                      u'&': "ampersand",
                      u'"': "quotedbl",
                      u'\'': "apostrophe",
                      u'(': "parenleft",
                      u')': "parenright",
                      u'*': "asterisk",
                      u'=': "equal",
                      u'+': "plus",
                      u',': "comma",
                      u'-': "minus",
                      u'.': "period",
                      u'/': "slash",
                      u':': "colon",
                      u';': "semicolon",
                      u'<': "less",
                      u'>': "greater",
                      u'?': "question",
                      u'@': "at",
                      u'[': "bracketleft",
                      u']': "bracketright",
                      u'\\': "backslash",
                      u'^': "asciicircum",
                      u'_': "underscore",
                      u'`': "grave",
                      u'{': "braceleft",
                      u'|': "bar",
                      u'}': "braceright",
                      u'~': "asciitilde",
                      u'á': "aacute",
                      u'º': "masculine",
                      u'¡': "exclamdown",
                      u'ç': "ccedilla",
                      u'ñ': "ntilde",
                      }

    def emulateWritingString(d, cmd, delay, k=None):
        '''
            Processes a string by writing it to the screen with a certain delay
        '''
        for c in cmd:
            if k is not None:
                # Emulate the key.
                emulateSpecialKey(d, k, delay)
            keysym = XK.string_to_keysym(c)
            if keysym == 0:
                # Its a symbol, not a letter.
                emulateSpecialKey(d, c, delay)
            else:
                # It's a letter
                keycode = d.keysym_to_keycode(keysym)
                # If it's uppercase, we press shift.
                if c.isupper():
                    xtest.fake_input(d, X.KeyPress, kmap[u'shift_l'])
                # Its even a specialer key :P
                if keycode == 0:
                    emulateSpecialKey(d, c, delay)
                else:
                    xtest.fake_input(d, X.KeyPress, keycode)
                    d.flush()
                    time.sleep(delay)
                    xtest.fake_input(d, X.KeyRelease, keycode)
                    # Delay time between letters
        #            time.sleep(0.025)
                # If it's uppercase, we release shift.
                if c.isupper():
                    xtest.fake_input(d, X.KeyRelease, kmap[u'shift_l'])
            d.flush()

    def emulateSpecialKey(d, skey, delay):
        '''
            Emulates Press and Release of Special Keys with a certain delay.
        '''
        print skey
#        assert(skey in kmap)
        if skey in u'\|@#~½¬{[]}\[}{~─|':
            xtest.fake_input(d, X.KeyPress, kmap[u'alt_l'])
            xtest.fake_input(d, X.KeyPress, kmap[skey])
            d.flush()
            time.sleep(delay)
            xtest.fake_input(d, X.KeyRelease, kmap[skey])
            xtest.fake_input(d, X.KeyRelease, kmap[u'alt_l'])
            d.flush()
        elif skey in u'!"·$%&/()=?¿ª:;>':
            xtest.fake_input(d, X.KeyPress, kmap[u'shift_l'])
            xtest.fake_input(d, X.KeyPress, kmap[skey])
            d.flush()
            time.sleep(delay)
            xtest.fake_input(d, X.KeyRelease, kmap[skey])
            xtest.fake_input(d, X.KeyRelease, kmap[u'shift_l'])
            d.flush()
        else:
            xtest.fake_input(d, X.KeyPress, kmap[skey])
            d.flush()
            time.sleep(delay)
            xtest.fake_input(d, X.KeyRelease, kmap[skey])
            d.flush()

# Windows
elif os.name == 'nt':
    import win32com.client
    import win32api
    import win32con
    import win32gui

    # Not working on Windows yet
