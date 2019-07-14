#!/usr/bin/env python3

"""
 Copyright (c) 2018-2019 Alan Yorinks - All Rights Reserved.


 Python Banyan is free software; you can redistribute it and/or
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

import signal
import sys

from python_banyan.banyan_base import BanyanBase


class BLK(BanyanBase):
    """
    This is the banyan launcher killer
    """

    def __init__(self):
        super(BLK, self).__init__(process_name='Launcher Killer')

        self.publish_payload({'exit': 'exit'}, 'killall')

        sys.exit(0)


def blk():
    BLK()


# signal handler function called when Control-C occurs
# noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
def signal_handler(sig, frame):
    print('Exiting Through Signal Handler')
    raise KeyboardInterrupt


# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    # replace with name of function you defined above
    blk()
