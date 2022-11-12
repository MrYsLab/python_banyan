# zmq_banyan_local_station_simulator.py

# requires Banyan 'backplane'

"""
Python-Banyan Providence:

Copyright (c) 2018-2019 Alan Yorinks All right reserved.

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


import time

from python_banyan.banyan_base import BanyanBase


class Bpub(BanyanBase):
    

    def __init__(self):
        
        # initialize the base class
        super(Bpub, self).__init__(process_name='Bpub')

        # send a message
        self.publish_payload({'from_banyan': 'hello_world'}, 'figura')
        self.count = 0
        
        while True:
            
            # send command to turn Led_0 ON
            self.publish_payload({'Led_0': self.count}, 'figura')
            self.count += 1
            time.sleep(0.01)
            #print('published ON')
            
            # send command to turn Led_0 OFF
            self.publish_payload({'Led_0': self.count}, 'figura')
            self.count += 1

            time.sleep(0.01)            
            #print('published OFF')
            
        # exit
        self.clean_up()
        
        
b = Bpub()
