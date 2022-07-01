"""
banyan_base_multi.py

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

# Use argparse and signal if you wish to implement the argparse
# code located at the bottom of this file
# import argparse
# import signal

import csv
import sys
import time
import itertools
import msgpack
import msgpack_numpy as m
import zmq
import os



# noinspection PyMethodMayBeStatic
class BanyanBaseMulti(object):
    """

    This is the base class for Python Banyan components that wish to connect to multiple back planes.
    It requires the user to create a .csv descriptor file to describe the back planes and their
    addresses/ports and subscription topics.

    The .csv file has the following format. This line must be the first line in the file:

    backplane_name,ip_address,subscriber_port,subscriber_topic,publisher_port

    backplane_name: a unique identifier string for backplane - for informational purposes only

    ip_address: IP address of the computer that the backplane is running on

    subscriber_port: port number assigned to the backplane's subscriber port

    subscriber_topic: this is an optional list of subscription topics

    publisher_port: port number assigned to the backplane's publisher port



    There should be an entry in this file for each backplane that the component needs to connect to.

    This class encapsulates zeromq and message pack functionality. Its methods should be overridden by the user
    in the derived class to meet the needs of the component.

    To import into  the derived class use:

           from python_banyan.banyan_base_multi import BanyanBaseMulti

    """

    def __init__(self, back_plane_csv_file=None, process_name='None',
                 loop_time=.1, numpy=False, connect_time=0.3):
        """
        The __init__ method sets up all the ZeroMQ "plumbing"

        :param back_plane_csv_file: full path to .csv file with backplane descriptors

        :param process_name: identifier for your component printed at startup on the console

        :param loop_time: receive loop sleep time

        :param numpy: Set true if you wish to include numpy matrices in your messages

        :param connect_time: a short delay to allow the component to connect to the Backplane

        :return:
        """

        # socket type - used for calls to find_socket
        self.SUB_SOCK = 0
        self.PUB_SOCK = 1

        if back_plane_csv_file is None:
            raise ValueError('You must specify a valid .csv backplane descriptor file')

        # file specified, make sure it exists
        if not os.path.isfile(back_plane_csv_file):
            raise ValueError("Can't find backplane configuration file")

        if process_name == 'None':
            print('Warning: No Process Name Was Specified')

        self.numpy = numpy

        self.connect_time = connect_time

        # if using numpy apply the msgpack_numpy monkey patch
        if numpy:
            m.patch()

        self.loop_time = loop_time

        # get a zeromq context
        self.my_context = zmq.Context()

        # a list of dictionaries describing connections to the back planes
        self.backplane_table = []

        print("\nUsing Backplane Descriptor File: ", back_plane_csv_file)

        with open(back_plane_csv_file) as csvfile:
            reader = csv.DictReader(csvfile)
            print('\n************************************************************\n')
            for row in reader:
                # make sure backplane name is unique
                if any(d['backplane_name'] == row['backplane_name'] for d in self.backplane_table):
                    raise RuntimeError('Duplicate Back Plane Name - check your .csv file')

                print(process_name + ' using ' + row['backplane_name'] + ' Black plane at IP Address: ' +
                      row['ip_address'])

                # setup a publisher and subscriber for each backplane
                subscriber = None
                if row['subscriber_port']:
                    subscriber = self.my_context.socket(zmq.SUB)
                    connect_string = "tcp://" + row['ip_address'] + ':' + row['subscriber_port']
                    subscriber.connect(connect_string)

                publisher = None
                if row['publisher_port']:
                    publisher = self.my_context.socket(zmq.PUB)
                    connect_string = "tcp://" + row['ip_address'] + ':' + row['publisher_port']
                    publisher.connect(connect_string)

                # get topics and subscribe to them
                # test that topic string has a leading and trailing []
                if row['subscriber_port']:
                    print('    Subscriber Port = ' + row['subscriber_port'])
                    topic_list = row['subscriber_topic']
                    if '[' not in topic_list:
                        raise RuntimeError('Topic field must begin with "[" and end with "]" ')
                    if ']' not in topic_list:
                        raise RuntimeError('Topic field must begin with "[" and end with "]" ')

                    # make sure that the topic string does not contain a space character
                    if ' ' in topic_list:
                        raise RuntimeError('Topics may not contain a space character')

                    topic_list = topic_list[1:-1].split(',')

                    # subscribe to topics in list
                    for t in topic_list:
                        if sys.version_info[0] < 3:
                            t = t.encode()
                        print('        Subscribed to topic: ' + t)
                        self.set_subscriber_topic(t, subscriber)
                else:
                    print('    Subscriber Port = None Specified')

                if row['publisher_port']:
                    print('    Publisher  Port = ' + row['publisher_port'])
                else:
                    print('    Publisher  Port = None Specified')

                # update backplane table with new entry
                self.backplane_table.append(
                    {'backplane_name': row['backplane_name'], 'subscriber': subscriber,
                     'publisher': publisher})

            # wait for the last Backplane TCP connection
            time.sleep(self.connect_time)

            print()
            print('Loop Time = ' + str(loop_time) + ' seconds\n')
            print('************************************************************')

    def find_socket(self, backplane, socket_type):
        """
        Find a publisher or subscriber in the backplane table and return a ZMQ socket reference

        :param backplane: backplane name entry in table

        :param socket_type: publisher or subscriber

        :return: socket reference or None
        """
        valid_socket_types = [self.PUB_SOCK, self.SUB_SOCK]

        if socket_type in valid_socket_types:
            try:
                entry = next(item for item in self.backplane_table if item.get("backplane_name") == backplane)
                if socket_type == self.PUB_SOCK:
                    rval = entry['publisher']
                else:
                    rval = entry['subscriber']
                return rval

            except StopIteration:
                raise StopIteration(backplane + ' not found in table.')
        else:
            raise ValueError(socket_type + ' is an illegal socket_type')

    def set_subscriber_topic(self, topic, subscriber_socket):
        """
        This method sets a subscriber topic.

        You can subscribe to multiple topics by calling this method for
        each topic.

        :param topic: A topic string

        :param subscriber_socket: subscriber socket

        :return:
        """

        # make sure topic is a string
        if not type(topic) is str:
            raise TypeError('Subscriber topic must be python_banyan string')

        # does the subscriber socket exist?
        if subscriber_socket:
            subscriber_socket.setsockopt(zmq.SUBSCRIBE, topic.encode())
        else:
            raise ValueError('set_subscriber_topic: socket is None')

    def unsubscribe_topic(self, topic, subscriber_socket):
        """
        This method un-subscribes from a topic.

        :param topic: A topic string

        :param subscriber_socket: subscriber socket

        :return:
        """

        # make sure topic is a string
        if not type(topic) is str:
            raise TypeError('Subscriber topic must be python_banyan string')

        # make sure that a socket reference has been passed in
        if subscriber_socket:
            subscriber_socket.unsubscribe(topic.encode())
        else:
            raise ValueError('set_subscriber_topic: socket is None')

    def publish_payload(self, payload, publisher_socket, topic=''):
        """
        This method will publish a python_banyan payload and its associated topic

        :param payload:  Protocol message to be published

        :param publisher_socket: Publisher socket - handle to socket or "BROADCAST" to send to
                                 all connected publisher sockets

        :param topic: A string value for message topic

        :return:
        """

        # make sure topic is a string
        if not type(topic) is str:
            raise TypeError('Publish topic must be python_banyan string', 'topic')

        # create python_banyan message pack payload
        if self.numpy:
            message = msgpack.packb(payload, default=m.encode)
        else:
            message = msgpack.packb(payload)

        pub_envelope = topic.encode()
        if publisher_socket == "BROADCAST":
            for element in self.backplane_table:
                if element['publisher']:
                    element['publisher'].send_multipart([pub_envelope, message])
        else:

            if publisher_socket:
                publisher_socket.send_multipart([pub_envelope, message])
            else:
                raise ValueError('Invalid publisher socket')

    def receive_loop(self):
        """
        This is the receive loop for zmq messages.

        This method may be overwritten to meet the needs
        of the application before handling received messages.

        :return:
        """
        for element in itertools.cycle(self.backplane_table):
            if element['subscriber']:
                try:
                    data = element['subscriber'].recv_multipart(zmq.NOBLOCK)
                    if self.numpy:
                        payload = msgpack.unpackb(data[1], object_hook=m.decode)
                        self.incoming_message_processing(data[0].decode(), payload)
                    else:
                        self.incoming_message_processing(data[0].decode(), umsgpack.unpackb(data[1]))
                except zmq.error.Again:
                    try:
                        time.sleep(self.loop_time)
                    except KeyboardInterrupt:
                        self.clean_up()
                        sys.exit(0)
                except AttributeError:
                    raise

    def incoming_message_processing(self, topic, payload):
        """
        Override this method with a custom python_banyan message processor for subscribed messages

        :param topic: Message Topic string

        :param payload: Message Data

        :return:
        """
        print('this method should be overwritten in the child class', topic, payload)

    def clean_up(self):
        """
        Clean up before exiting - override if additional cleanup is necessary

        :return:
        """
        for element in self.backplane_table:
            if element['publisher']:
                element['publisher'].close()
            if element['subscriber']:
                element['subscriber'].close()
        self.my_context.term()

# When creating a derived component, replicate the code below and replace banyan_base_multi with a  name of your choice

# def banyan_base_multi():
#     # allow user to bypass the IP address auto-discovery. This is necessary if the component resides on a computer
#     # other than the computing running the backplane.
#
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-b", dest="back_plane_csv_file", default="None",
#                         help="Backplane .csv descriptor file name")
#
#     # allow the user to specify a name for the component and have it shown on the console banner.
#     # modify the default process name to one you wish to see on the banner.
#     # change the default in the derived class to set the name
#     parser.add_argument("-n", dest="process_name", default="YOUR PROCESS NAME", help="Set process name in banner")
#
#     parser.add_argument("-t", dest="loop_time", default=".1", help="Event Loop Timer in seconds")
#
#     args = parser.parse_args()
#     kw_options = {}
#
#     if args.back_plane_csv_file != 'None':
#         kw_options['back_plane_csv_file'] = args.back_plane_csv_file
#
#     kw_options['process_name'] = args.process_name
#
#     kw_options['loop_time'] = float(args.loop_time)
#
#     # replace with the name of your class
#     app = BanyanBaseMulti(**kw_options)
#
#     # optionally start the receive loop here or start it in your __init__
#     app.receive_loop()
#
#
# signal handler function called when Control-C occurs
# noinspection PyShadowingNames,PyUnusedLocal,PyUnusedLocal
# def signal_handler(sig, frame):
#     print('Exiting Through Signal Handler')
#     raise KeyboardInterrupt
#
#
# # listen for SIGINT
# signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)
#
#
# if __name__ == '__main__':
#     # replace with name of function you defined above
#     banyan_base_multi()
