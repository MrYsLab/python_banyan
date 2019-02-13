"""
 Copyright (c) 2016-2019 Alan Yorinks All right reserved.

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

import sys
import time
from python_banyan.banyan_base import BanyanBase


class BanyanPub(BanyanBase):
    """
    This class publishes 100000 "test" topic messages as fast as it can.
    It then prints the current time and exits.
    """

    def __init__(self):
        super(BanyanPub, self).__init__(process_name='Banyan publisher')

        print('Publishing 100000 messages.')
        time.sleep(.3)

        for x in range(0, 100000):
            payload = {'msg': x}
            self.publish_payload(payload, 'test')

        localtime = time.asctime(time.localtime(time.time()))

        print('Task completed at: ', localtime)

        super(BanyanPub, self).clean_up()
        sys.exit(0)

# instantiate this class
BanyanPub()



