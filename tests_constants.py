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

# Una cantidad razonable de segundos para esperar respuestas
TIMEOUT = 3
# Directorio donde se encuentra PyKeyLogger
PATH = "/home/roxy/Tesis/PyKeylogger/"
LOGPATH = "logs/detailed_log/logfile.txt"
# Separador de la fecha.
DSEPARATOR = '-'
# Separador de la hora.
TSEPARATOR = ':'
# Separador del log.
SEPARATOR = '|'
# Teclas para abrir el menu.
MENU_KEYS = '[KeyName:Control_L][KeyName:Control_R][KeyName:F12]'
# Teclas para cerrar el detalle de acciones del menu.
EXIT_KEYS = '[KeyName:Alt_L]a'
# Hubo un enter.
RETURN = '[KeyName:Return]'
# Segundos para esperar entre paso y paso.
SECONDS = 1

# Tiempos necesarios para simular la entrada por un humano
TIMES = [0.01, 0.05, 0.09]

# Mapeo entre strings y keysyms (solo de caracteres especiales).
SPECIALKEYSYMS = {
    ' ': "space",
    '\t': "Tab",
    '\n': "Return",
    '\r': "Return",
    '\e': "Escape",
    '!': "exclam",
    '#': "numbersign",
    '%': "percent",
    '$': "dollar",
    '&': "ampersand",
    '"': "quotedbl",
    '\'': "apostrophe",
    '(': "parenleft",
    ')': "parenright",
    '*': "asterisk",
    '=': "equal",
    '+': "plus",
    ',': "comma",
    '-': "minus",
    '.': "period",
    '/': "slash",
    ':': "colon",
    ';': "semicolon",
    '<': "less",
    '>': "greater",
    '?': "question",
    '@': "at",
    '[': "bracketleft",
    ']': "bracketright",
    '\\': "backslash",
    '^': "asciicircum",
    '_': "underscore",
    '`': "grave",
    '{': "braceleft",
    '|': "bar",
    '}': "braceright",
    '~': "asciitilde"
    }
