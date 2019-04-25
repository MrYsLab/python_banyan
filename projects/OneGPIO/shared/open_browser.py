"""
 Copyright (c) 2019 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import sys
import webbrowser
import time


def open_browser():

    valid_html_files = ['arduino', 'esp8266', 'rpi']
    path = '../arduino_uno/arduino.html'

    if len(sys.argv) == 2:
        if sys.argv[1] in valid_html_files:
            if sys.argv[1] == 'arduino':
                path = '../arduino_uno/arduino.html'
            elif sys.argv[1] == 'esp8266':
                path = '../esp_8266/esp8266.html'
            elif sys.argv[1] == 'rpi':
                path = '../raspberry_pi/rpi.html'

    webbrowser.open(path, new=2)
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    open_browser()
