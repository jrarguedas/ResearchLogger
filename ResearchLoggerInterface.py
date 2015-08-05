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

from Tkinter import *
import tkSimpleDialog
from constants import EXTENSION, WINDOWTITLE, BASE_PATH
import os.path
import codecs
import sys
import time
import os
import string
import argparse


class TranslationWindow(Frame):
    """
        This is the window which has the translation source text and target
        text. It initializes the keylogging activity.

        The onset is the time when the test start. For us, the onset is the
        time when the researcher chooses a file that the subjects should
        translate. The file selection can be done in two different ways:
            - By double clicking on the chosen file.
            - By selecting the file with one click and then pressing enter.
        We start the keylogging activity before showing the file
        chooser window so that the time when the file is chosen is logged.

        The logging activity finishes when the translation window is closed.
        This is logged by our program and then it stops logging data. There is
        only one way to close a translation window and that is by clicking once
        in the X button on the right upper corner of the screen.
    """

    def __init__(self, parent, path):
        Frame.__init__(self, parent)
        self.parent = parent
        self.path = path
        # Gets the subject name.
        self.username = self.getUsername()
        # Gets the source text.
        self.filename = self.getFilename()
        # Starts the User Interface.
        # For the experiments with translation memories, we don't need a
        # graphical interface.
        self.initUI()
        # Updates the source tex.
        self.setFilename(self.filename)

    def getUsername(self):
        """
            Gets the subject ID.
        """
        # Hides the main window. (This is necessary to ask for the subject id)
        self.parent.withdraw()
        # Asks for the subject id.
        username = None
        exists = False
        username = tkSimpleDialog.askstring("Enter Subject ID", "Please "
                                            "insert you subject id here.")
        # Always in lowercase to avoid conflicts between Linux and Windows.
        if username is not None:
            username = string.lower(username)
            exists = self.check_log_existance(username)
        if username is None or username == '' or exists is True:
            print "Error. Username cannot be empty."
            sys.exit(1)
        # Shows the main window that had been hidden.
        self.parent.deiconify()
        return username

    def check_log_existance(self, username):
        """
            Checks whether a log file exists. If it does, it returns True.
            Otherwise, it returns
            False.

            A log file is of the form "logs-"+username.
        """
        logdir = "logs-" + username
        return logdir in os.listdir(os.getcwd())

    def getFilename(self):
        """
            Selects a file using tkFileDialog.
        """
        import tkFileDialog
        # Dialog window to select a file.
        ftypes = [('All files', '*')]
        dlg = tkFileDialog.Open(self, filetypes=ftypes)
        filename = dlg.show()
        return filename

    def initUI(self):
        """
            Initiates the User Interface.
        """
        self.parent.title(WINDOWTITLE)

        # Overrides the default behavious of the close button.
        self.parent.protocol("WM_DELETE_WINDOW", self.onExit)

        # Menu Bar.
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        # Source Text.
        self.sourcetext = Text(self.parent, width=110, height=16,
                               font="Verdana 12", wrap="word", bd=0,
                               bg="white smoke", state=DISABLED)
        self.sourcetext.pack(fill=BOTH, expand=1, padx=10, pady=5)
        self.sourcetext.tag_configure('title', font=('Verdana', 12),
                                      underline=1, justify='center')
        self.sourcetext.tag_configure('text', font=('Verdana', 12))

        # Target Text Box.
        self.targettext = Text(self.parent, width=110, height=10,
                               state='normal', font="Verdana 12")
        self.targettext.pack(fill=BOTH, expand=1, padx=10, pady=5)

    def setFilename(self, filename):
        """
            Tries to open a file that contains the source code.
        """
        # The textbox needs to be able to be modified.
        self.sourcetext.config(state=NORMAL)

        try:
            # Tries to open the file.
            f = open(filename, 'r')
        except IOError as ioe:
            # The file couldn't be opened because it doesn't exist!
            msg = "Error de I/O al abrir el archivo que contiene el texto "
            msg += "fuente. Error {0}: {1}."
            print msg.format(ioe.errno, ioe.strerror)
            self.onExit()
            sys.exit(1)  # Abnormal termination.
        except:
            msg = "Error fatal al abrir el archivo que contiene el texto "
            msg += "fuente:"
            print msg, sys.exc_info()[0]
            sys.exit(1)  # Abnormal termination.
        else:
            # Cleans the textbox.
            self.sourcetext.delete(0.0, END)
            # Inserts the the title of the source text.
            title = f.readline()
            self.sourcetext.insert(END, title, 'title')
            # Inserts the body of the source text.
            txt = f.read()
            self.sourcetext.insert(END, txt, 'text')
            # Closes the file.
            f.close()
            # Now the text has been loaded but it shouldn't be modified by the
            # user.
            self.sourcetext.config(state=DISABLED)

    def saveDefault(self, fname, tstmp):
        """
            Saves the translation on a default dir.
        """
        msg = "Guardando el archivo en el directorio por defecto."
        print msg
        filename = BASE_PATH + '/' + self.username + '_' + fname + '_' + tstmp + EXTENSION
        self.f = codecs.open(filename, mode='w+', encoding="utf-8")

    def onSave(self):
        """
            Saves the content of the targettext field into a file named
            user_text.txt.
        """
        # Tries to get the name that will be created.
        # Creation of this file may fail in case nothing has been translated,
        # So we do nothing since there's nothing to be saved.

        # Timestamp to make sure that we save different versions of a
        # translation done by the same subject.
        tstmp = str(int(time.time()))
        fname = self.filename.split("/")[-1]
        fname = fname.split('.')[0]
        filename = self.path + self.username + '_' + fname + '_' + tstmp + EXTENSION
        print "Guardando archivo:", filename
        # Gets the target text.
        ttext = self.targettext.get(0.0, END)
        # Creates the file where the target text will be saved.
        try:
            directory = filename.split('/')
            directory.pop()
            directory = "/".join(directory)
            directory += '/'
            if not os.path.isdir(directory):
                os.mkdir(directory)
            self.f = codecs.open(filename, mode='w+', encoding="utf-8")
        except IOError:
            # Tries to create a file that already exists.
            msg = "Error fatal al guardar el texto meta:"
            print msg, sys.exc_info()[0]
            self.onExit(False)
            self.saveDefault(fname, tstmp)
            sys.exit(1)  # Abnormal termination.
        except OSError:
            msg = "Imposible crear el directorio especificado.\n"
            print msg
            self.saveDefault(fname, tstmp)
        try:
            # Save the translated text in a file.
            self.f.write(ttext)
        except UnicodeEncodeError, reason:
            print ttext
            print reason
            sys.exit(1)
        self.f.close()

    def onExit(self, saves=True):
        """
            Saves the target text before exiting the translation interface.
        """
        assert(isinstance(saves, bool))
        if saves:
            self.onSave()
        self.parent.destroy()


def parse():
    """
        Returns the command line option for the log directory.
    """
    parser = argparse.ArgumentParser(description='Options for Keylogger.')
    parser.add_argument('-d', default=BASE_PATH,
                        help='Directory to save the log files.')
    args = parser.parse_args()
    dir = args.d
    # Dir need to end with '/'
    if not dir.endswith('/'):
        dir += '/'
    return dir


def main():
    # Parses command line options.
    path = parse()
    # Creates the main window.
    root = Tk()
    # Prepares the translation window.
    ex = TranslationWindow(root, path)
    RWidth = root.winfo_screenwidth()
    RHeight = root.winfo_screenheight()
    root.minsize(1000, 450)
    root.maxsize(1200, 650)
    root.geometry((("%dx%d") % (RWidth, RHeight)) + '+20+20')
    # Begins our program.
    root.mainloop()


if __name__ == '__main__':
    main()
