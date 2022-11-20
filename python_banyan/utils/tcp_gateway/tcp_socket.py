"""
 Copyright (c) 2020 Alan Yorinks All rights reserved.

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

import asyncio
import sys


# noinspection PyStatementEffect,PyUnresolvedReferences,PyUnresolvedReferences
class TcpSocket:
    """
    This class encapsulates management of a tcp/ip connection that communicates
    with a TCP server
    """

    def __init__(self, ip_address, ip_port, loop):
        self.ip_address = ip_address
        self.ip_port = ip_port
        self.loop = loop
        self.reader = None
        self.writer = None

    async def start(self):
        """
        This method opens an IP connection on the IP device

        :return: None
        """
        connected = None
        print("Waiting to connect to the server ...")
        while not connected:
            try:
                self.reader, self.writer = await asyncio.open_connection(
                    self.ip_address, self.ip_port)
                print(f'Successfully connected to: {self.ip_address}:{self.ip_port}')
                connected = True
            except OSError:
                continue

    async def write(self, data):
        """
        This method writes sends data to the IP device
        :param data:

        :return: None
        """

        output_list = []

        # create an array of integers from the data to be sent
        for x in data:
            output_list.append(x)

        # now convert the integer list to a bytearray
        to_wifi = bytearray(output_list)
        self.writer.write(to_wifi)
        await self.writer.drain()

    async def read(self, num_bytes=1):
        """
        This method reads one byte of data from IP device

        :return: Next byte
        """
        buffer = await self.reader.read(num_bytes)
        return buffer
