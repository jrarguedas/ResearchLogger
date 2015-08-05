# -*- coding: utf-8 -*-
# !/usr/bin/python

#
# pyxhook -- an extension to emulate some of the PyHook library on linux.
#
#    Copyright (C) 2008 Tim Alexander <dragonfyre13@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307uSA
#
#    Thanks to Alex Badea <vamposdecampos@gmail.com> for writing the Record
#    demo for the xlib libraries. It helped me immensely working with these
#    in this library.
#
#    Thanks to the python-xlib team. This wouldn't have been possible without
#    your code.
#    This requires:
#    at least python-xlib 1.4
#    xwindows must have the "record" extension present, and active.
#
#    This file has now been somewhat extensively modified by
#    Daniel Folkinshteyn <nanotube@users.sf.net>
#    So if there are any bugs, they are probably my fault. :)
#
#    2015 Modifications by Roxana Lafuente <roxana.lafuente@gmail.com>

import sys
import re
import time
import threading

from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq

from constants import KDOWN, KUP, MLEFT, MMIDDLE, MRIGHT, MWHEELUP, MWHEELDOWN, KMAP

#########################################################################
# #######################START CLASS DEF############################### #
#########################################################################


class HookManager(threading.Thread):
    """
        This is the main class. Instantiate it, and you can hand it KeyDown and
        KeyUp (functions in your own code) which execute to parse the
        PyXHookKeyEvent class that is returned.

        This simply takes these two values for now:
            - KeyDown = The function to execute when a key is pressed, if it
        returns anything. It hands the function an argument that is the
        PyXHookKeyEvent class.
            - KeyUp = The function to execute when a key is released, if it
        returns anything. It hands the function an argument that is the
        PyXHookKeyEvent class.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.finished = threading.Event()

        # Give these some initial values
        self.mouse_position_x = 0
        self.mouse_position_y = 0
        self.ison = {"shift": False, "caps": False}

        # Compile our regex statements.
        self.isshift = re.compile('^Shift')
        self.iscaps = re.compile('^Caps_Lock')
        self.shiftablechar = re.compile('^[a-z0-9]$|^minus$|^equal$|'
                                        '^bracketleft$|^bracketright$|'
                                        '^semicolon$|^backslash$|^apostrophe$|'
                                        '^comma$|^period$|^slash$|^grave$')
        self.logrelease = re.compile('.*')
        self.isspace = re.compile('^space$')

        # Assign default function actions (do nothing).
        self.KeyDown = lambda x: True
        self.KeyUp = lambda x: True
        self.MouseAllButtonsDown = lambda x: True
        self.MouseAllButtonsUp = lambda x: True

        self.contextEventMask = [X.KeyPress, X.MotionNotify]

        # Hook to our display.
        self.local_dpy = display.Display()
        self.record_dpy = display.Display()

    def run(self):
        # Check if the extension is present.
        if not self.record_dpy.has_extension("RECORD"):
            print "RECORD extension not found"
            sys.exit(1)
        r = self.record_dpy.record_get_version(0, 0)
        print "RECORD extension version %d.%d" % \
            (r.major_version, r.minor_version)

        # Create a recording context; we only want key and mouse events.
        self.ctx = self.record_dpy.record_create_context(
            0,
            [record.AllClients],
            [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),
                # (X.KeyPress, X.ButtonPress),
                'device_events': tuple(self.contextEventMask),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
            }])

        # Enable the context; this only returns after a call to
        # record_disable_context, while calling the callback function in the
        # meantime.
        self.record_dpy.record_enable_context(self.ctx, self.processevents)
        # Finally free the context.
        self.record_dpy.record_free_context(self.ctx)

    def cancel(self):
        self.finished.set()
        self.local_dpy.record_disable_context(self.ctx)
        self.local_dpy.flush()

    def printevent(self, event):
        print event

    def HookKeyboard(self):
        pass
        # We don't need to do anything here anymore, since the default mask
        # is now set to contain X.KeyPress
        # self.contextEventMask[0] = X.KeyPress

    def HookMouse(self):
        pass
        # We don't need to do anything here anymore, since the default mask
        # is now set to contain X.MotionNotify

        # need mouse motion to track pointer position, since ButtonPress events
        # don't carry that info.
        # self.contextEventMask[1] = X.MotionNotify

    def processevents(self, reply):
        if reply.category != record.FromServer:
            return
        if reply.client_swapped:
            print "* received swapped protocol data, cowardly ignored"
            return
        if not len(reply.data) or ord(reply.data[0]) < 2:
            # not an event
            return
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(
                data, self.record_dpy.display, None, None)
            if event.type == X.KeyPress:
                hookevent = self.keypressevent(event)
                self.KeyDown(hookevent)
            elif event.type == X.KeyRelease:
                hookevent = self.keyreleaseevent(event)
                self.KeyUp(hookevent)
            elif event.type == X.ButtonPress:
                hookevent = self.buttonpressevent(event)
                self.MouseAllButtonsDown(hookevent)
            elif event.type == X.ButtonRelease:
                hookevent = self.buttonreleaseevent(event)
                self.MouseAllButtonsUp(hookevent)
            elif event.type == X.MotionNotify:
                # use mouse moves to record mouse position, since press and
                # release events do not give mouse position info (event.root_x
                # and event.root_y have bogus info).
                self.mousemoveevent(event)

    def keypressevent(self, event):
        matchto = self.lookup_keysym(self.local_dpy.keycode_to_keysym(
            event.detail, 0))
        # This is a character that can be typed.
        if self.shiftablechar.match(self.lookup_keysym(
                self.local_dpy.keycode_to_keysym(event.detail, 0))):
            if self.ison["shift"] is False:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
                return self.makekeyhookevent(keysym, event)
            else:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 1)
                return self.makekeyhookevent(keysym, event)
        # Not a typable character.
        else:
            keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
            if self.isshift.match(matchto):
                self.ison["shift"] = self.ison["shift"] + 1
            elif self.iscaps.match(matchto):
                if self.ison["caps"] is False:
                    self.ison["shift"] = self.ison["shift"] + 1
                    self.ison["caps"] = True
                if self.ison["caps"] is True:
                    self.ison["shift"] = self.ison["shift"] - 1
                    self.ison["caps"] = False
            return self.makekeyhookevent(keysym, event)

    def keyreleaseevent(self, event):
        if self.shiftablechar.match(self.lookup_keysym(
                self.local_dpy.keycode_to_keysym(event.detail, 0))):
            if self.ison["shift"] is False:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
            else:
                keysym = self.local_dpy.keycode_to_keysym(event.detail, 1)
        else:
            keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
        matchto = self.lookup_keysym(keysym)
        if self.isshift.match(matchto):
            self.ison["shift"] = self.ison["shift"] - 1
        return self.makekeyhookevent(keysym, event)

    def buttonpressevent(self, event):
        return self.makemousehookevent(event)

    def buttonreleaseevent(self, event):
        return self.makemousehookevent(event)

    def mousemoveevent(self, event):
        self.mouse_position_x = event.root_x
        self.mouse_position_y = event.root_y

    # Need the following because XK.keysym_to_string() only does printable
    # chars rather than being the correct inverse of XK.string_to_keysym().
    def lookup_keysym(self, keysym):
        try:
            return KMAP[keysym]
        except KeyError:
            return str(keysym)

    def asciivalue(self, keysym):
        asciinum = XK.string_to_keysym(self.lookup_keysym(keysym))
        if asciinum < 256:
            return asciinum
        else:
            return 0

    def makekeyhookevent(self, keysym, event):
        storewm = self.xwindowinfo()
        if event.type == X.KeyPress:
            MessageName = KDOWN
        elif event.type == X.KeyRelease:
            MessageName = KUP
        return PyXHookKeyEvent(storewm["handle"], storewm["name"],
                               storewm["class"], self.lookup_keysym(keysym),
                               self.asciivalue(keysym), False, event.detail,
                               MessageName, event.root_x, event.root_y,
                               event.time)

    def makemousehookevent(self, event):
        storewm = self.xwindowinfo()
        if event.detail == 1:
            MessageName = MLEFT
        elif event.detail == 3:
            MessageName = MRIGHT
        elif event.detail == 2:
            MessageName = MMIDDLE
        elif event.detail == 5:
            MessageName = MWHEELDOWN
        elif event.detail == 4:
            MessageName = MWHEELUP
        else:
            MessageName = "mouse " + str(event.detail) + " "

        if event.type == X.ButtonPress:
            MessageName = MessageName + "_down"
        elif event.type == X.ButtonRelease:
            MessageName = MessageName + "_up"
        return PyXHookMouseEvent(storewm["handle"], storewm["name"],
                                 storewm["class"], (self.mouse_position_x,
                                 self.mouse_position_y), MessageName,
                                 event.time)

    def xwindowinfo(self):
        try:
            windowvar = self.local_dpy.get_input_focus().focus
            wmname = windowvar.get_wm_name()
            wmclass = windowvar.get_wm_class()
            wmhandle = str(windowvar)[20:30]
        except:
            # This is to keep things running smoothly. It almost never happens,
            # but still...
            return {"name": None, "class": None, "handle": None}
        if (wmname is None) and (wmclass is None):
            try:
                windowvar = windowvar.query_tree().parent
                wmname = windowvar.get_wm_name()
                wmclass = windowvar.get_wm_class()
                wmhandle = str(windowvar)[20:30]
            except:
                # This is to keep things running smoothly. It almost never
                # happens, but still...
                return {"name": None, "class": None, "handle": None}
        if wmclass is None:
            return {"name": wmname, "class": wmclass, "handle": wmhandle}
        else:
            return {"name": wmname, "class": wmclass[0], "handle": wmhandle}


class PyXHookKeyEvent:
    """
        This is the class that is returned with each key event.f
        It simply creates the variables below in the class.

        - window = The handle of the window.
        - window_name = The name of the window.
        - window_proc_name = The backend process for the window.
        - key = The key pressed, shifted to the correct caps value.
        - ascii = An ascii representation of the key. It returns 0 if the ascii
        value is not between 31 and 256.
        - key_id = This is just False for now. Under windows, it is the Virtual
        Key Code, but that's a windows-only thing.
        - scan_code = Please don't use this. It differs for pretty much every
        type of keyboard. X11 abstracts this information anyway.
        - message_name = KDOWN, KUP.
    """

    def __init__(self, window, window_name, window_proc_name, key, ascii,
                 key_id, scan_code, message_name, mx, my, time):
        self.Window = window
        self.WindowName = window_name
        self.WindowProcName = window_proc_name
        self.Key = key
        self.Ascii = ascii
        self.KeyID = key_id
        self.ScanCode = scan_code
        self.MessageName = message_name
        self.MouseX = mx
        self.MouseY = my
        self.Time = time

    def __str__(self):
        return "Window Handle: " + str(self.Window) + "\nWindow Name: " + \
            str(self.WindowName) + "\nWindow's Process Name: " + \
            str(self.WindowProcName) + "\nKey Pressed: " + str(self.Key) + \
            "\nAscii Value: " + str(self.Ascii) + "\nKeyID: " + \
            str(self.KeyID) + "\nScanCode: " + str(self.ScanCode) + \
            "\nMessageName: " + str(self.MessageName) + \
            "\nMouseX: " + str(self.MouseX) + \
            "\nMouseY: " + str(self.MouseY) + \
            "\nTime: " + str(self.Time) + "\n"


class PyXHookMouseEvent:
    """
        This is the class that is returned with each key event.f
        It simply creates the variables below in the class.

        Window = The handle of the window.
        WindowName = The name of the window.
        WindowProcName = The backend process for the window.
        Position = 2-tuple (x,y) coordinates of the mouse click
        MessageName = "MLEFT|MRIGHT|MMIDDLE",
                        "mouse left|right|middle up".
    """

    def __init__(self, window, window_name, window_proc_name, position,
                 message_name, time):
        self.Window = window
        self.WindowName = window_name
        self.WindowProcName = window_proc_name
        self.Position = position
        self.MessageName = message_name
        self.Time = time

    def __str__(self):
        return "Window Handle: " + str(self.Window) + "\nWindow Name: " + \
            str(self.WindowName) + "\nWindow's Process Name: " \
            + str(self.WindowProcName) + "\nPosition: " + \
            str(self.Position) + "\nMessageName: " + str(self.MessageName) + \
            "\nTime: " + str(self.Time) + "\n"

#########################################################################
# ########################END CLASS DEF################################ #
#########################################################################

if __name__ == '__main__':
    hm = HookManager()
    hm.HookKeyboard()
    hm.HookMouse()
    hm.KeyDown = hm.printevent
    hm.KeyUp = hm.printevent
    hm.MouseAllButtonsDown = hm.printevent
    hm.MouseAllButtonsUp = hm.printevent
    hm.start()
    time.sleep(10)
    hm.cancel()
