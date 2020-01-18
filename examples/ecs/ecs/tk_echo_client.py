#!/usr/bin/env python3

"""
tk_echo_client.py

Copyright (c) 2016 - 2019 Alan Yorinks All right reserved.

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
from __future__ import unicode_literals

import time

# python 2/3 compatibility
try:
    from tkinter import *
    from tkinter import font
    from tkinter import ttk
except ImportError:
    from Tkinter import *
    import tkFont as font
    import ttk

import sys
import umsgpack
import zmq
from python_banyan.banyan_base import BanyanBase


# noinspection PyMethodMayBeStatic,PyUnresolvedReferences,PyUnusedLocal
class TkEchoClient(BanyanBase):
    """
    A graphical echo client.
    """

    def __init__(self, topics=['reply'], number_of_messages=10,
                 back_plane_ip_address=None, subscriber_port='43125',
                 publisher_port='43124', process_name='Banyan Echo Client'):
        """

        :param topics: A list of topics to subscribe to
        :param number_of_messages: Default number of echo messages to send
        :param back_plane_ip_address:
        :param subscriber_port:
        :param publisher_port:
        :param process_name:
        """

        # establish some banyan variables
        self.back_plane_ip_address = back_plane_ip_address
        self.subscriber_port = subscriber_port
        self.publisher_port = publisher_port

        # subscribe to the topic
        if topics is None:
            raise ValueError('No Topic List Was Specified.')

        # initialize the banyan base class
        super(TkEchoClient, self).__init__(back_plane_ip_address=back_plane_ip_address,
                                           subscriber_port=subscriber_port,
                                           publisher_port=publisher_port,
                                           process_name=process_name)

        # subscribe to all topics specified
        for x in topics:
            self.set_subscriber_topic(str(x))

        # setup root window
        self.root = Tk()
        # create content window into which everything else is placed

        self.root.title(process_name)
        self.content = ttk.Frame(self.root, borderwidth=5,
                                 relief="sunken", padding=12)

        # use a grid layout
        self.content.grid(column=0, row=0, sticky=(N, S, E, W))

        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        # setup some display variables

        # messages to be sent
        self.messages_to_be_sent = StringVar()
        self.messages_to_be_sent.set('10')

        # messages sent count
        self.messages_sent = StringVar()
        self.message_sent_count = 0
        self.messages_sent.set(str(self.message_sent_count))

        # set up font variant
        self.larger_font = font.Font(size=12)

        # add the widgets
        ttk.Label(self.content, font=self.larger_font, text="Messages To Be Sent").grid(column=3, row=1, sticky=W)
        ttk.Label(self.content, font=self.larger_font, text="Messages Sent").grid(column=3, row=2, sticky=W)

        style = ttk.Style()
        style.configure("BW.TLabel", foreground="black", background="white")

        ttk.Label(self.content, font=self.larger_font,
                  textvariable=self.messages_sent,
                  width=5,
                  anchor=E, justify=RIGHT, style="BW.TLabel").grid(column=2, row=2, sticky=W)

        self.to_send_entry = ttk.Entry(self.content, width=5,
                                       font=self.larger_font,
                                       textvariable=self.messages_to_be_sent,
                                       justify='right')
        self.to_send_entry.grid(column=2, row=1, sticky=(W, E))

        s = ttk.Style()
        s.configure('my.TButton', font=self.larger_font)

        self.send_button = ttk.Button(self.content, text="Send Messages",
                                      command=self.send, style='my.TButton')
        self.send_button.grid(column=4, row=3, sticky=W)

        for child in self.content.winfo_children():
            child.grid_configure(padx=20, pady=5)

        self.to_send_entry.focus()
        self.root.bind('<Return>', self.send)

        self.number_of_messages = number_of_messages

        # sequence number of messages
        self.message_number = self.number_of_messages

        # send the first message - make sure that the server is already started
        # self.publish_payload({'message_number': self.message_number}, 'echo')
        self.message_number -= 1
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.root.after(1, self.get_message)

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()

    def get_message(self):
        """
        This method is called from the tkevent loop "after" call. It will poll for new zeromq messages
        :return:
        """
        try:
            data = self.subscriber.recv_multipart(zmq.NOBLOCK)
            self.incoming_message_processing(data[0].decode(), umsgpack.unpackb(data[1]))
            self.root.after(1, self.get_message)

        except zmq.error.Again:
            try:
                time.sleep(.0001)
                self.root.after(1, self.get_message)

            except KeyboardInterrupt:
                self.root.destroy()
                self.publisher.close()
                self.subscriber.close()
                self.my_context.term()
                sys.exit(0)
        except KeyboardInterrupt:
            self.root.destroy()
            self.publisher.close()
            self.subscriber.close()
            self.my_context.term()
            sys.exit(0)

    def incoming_message_processing(self, topic, payload):
        # When a message is received and its number is zero, finish up.
        if self.message_number == 0:
            self.messages_sent.set(str(self.number_of_messages))

        # bump the message number and send the message out
        else:
            self.message_number -= 1
            self.message_sent_count += 1
            self.messages_sent.set(str(self.message_sent_count))

            # account for python2 vs python3 differences
            if sys.version_info[0] < 3:
                self.publish_payload({'message_number': self.message_number}, 'echo'.encode())
            else:
                self.publish_payload({'message_number': self.message_number}, 'echo')


    def send(self, *args):
        msgs = self.to_send_entry.get()
        # reset the sent count variables to zero
        self.message_sent_count = 0
        self.messages_sent.set(str(self.message_sent_count))

        # set current message number to the number of messages to be sent
        self.message_number = int(msgs)

        # update the number of messages to be sent
        self.number_of_messages = int(msgs)

        # account for python2 vs python3 differences
        if sys.version_info[0] < 3:
            self.publish_payload({'message_number': self.message_number}, 'echo'.encode())
        else:
            self.publish_payload({'message_number': self.message_number}, 'echo')

    def on_closing(self):
        """
        Destroy the window
        :return:
        """
        self.clean_up()
        self.root.destroy()


def gui_client():
    TkEchoClient()


if __name__ == '__main__':
    gui_client()
