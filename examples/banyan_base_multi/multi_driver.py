"""
multi_driver.py

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

import argparse
import signal
import sys


from python_banyan.banyan_base_multi import BanyanBaseMulti


class MultiDriver(BanyanBaseMulti):
    """
    This class sends messages to 2 backplanes and monitors the reply packets
    """

    def __init__(self, back_plane_csv_file=None,
                 number_of_messages=10, process_name='MultiDriver', loop_time=0.01):
        """

        :param back_plane_csv_file: Backplane, pub port, sub port, and sub topic descriptor file
        :param number_of_messages: Number of messages to send
        :param process_name:
        :param loop_time:
        """

        super(MultiDriver, self).__init__(back_plane_csv_file=back_plane_csv_file,
                                          process_name=process_name, loop_time=loop_time)

        # sequence number of messages
        self.message_number_a = number_of_messages
        self.message_number_b = number_of_messages

        self.number_of_messages = number_of_messages

        # find the sockets in the table for the 2 backplanes
        self.socket_a = self.find_socket("BP1", self.PUB_SOCK)
        self.socket_b = self.find_socket("BP2", self.PUB_SOCK)

        # send the first message for each backplane
        self.publish_payload({'message_number': self.message_number_a, 'id': 'a'},
                             self.socket_a, 'trigger')
        self.publish_payload({'message_number': self.message_number_b, 'id': 'b'},
                             self.socket_b, 'trigger')

        # a flag to determine when both channels are done
        self.both_done = 0

        # start receiving messages
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def incoming_message_processing(self, topic, payload):

        # channel a handler
        if payload['id'] == 'a':
            if self.message_number_a == 0:
                # we are done
                print(str(self.number_of_messages) + ' messages sent and received. ')
                self.both_done += 1

            # bump the message number and send the message out
            else:
                self.message_number_a -= 1
                self.publish_payload({'message_number': self.message_number_a, 'id': 'a'}, self.socket_a, 'trigger')
        # channel b handler
        elif payload['id'] == 'b':

            if payload['message_number'] == 0:
                print(str(self.number_of_messages) + ' messages sent and received. ')
                self.both_done += 1

            # bump the message number and send the message out
            else:
                self.message_number_b -= 1
                self.publish_payload({'message_number': self.message_number_b, 'id': 'b'}, self.socket_b, 'trigger')
        # test to see if we are done
        if self.both_done == 2:
            input("Both channels completed. Press Enter to exit.")
            self.clean_up()
            sys.exit(0)


def multi_driver():
    # allow user to bypass the IP address auto-discovery. This is necessary if the component resides on a computer
    # other than the computing running the backplane.

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", dest="back_plane_csv_file", default="multi_driver_spec.csv",
                        help="Backplane CSV Formatted Descriptor File")

    # allow the user to specify a name for the component and have it shown on the console banner.
    # modify the default process name to one you wish to see on the banner.
    # change the default in the derived class to set the name
    parser.add_argument("-m", dest="number_of_messages", default="10", help="Number of messages to publish")
    parser.add_argument("-n", dest="process_name", default="MultiDriver", help="Set process name in banner")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")
    parser.add_argument("-t", dest="loop_time", default=".1", help="Event Loop Timer in seconds")

    args = parser.parse_args()

    kw_options = {'back_plane_csv_file': args.back_plane_csv_file, 'number_of_messages': int(args.number_of_messages),

                  'process_name': args.process_name,
                  'loop_time': float(args.loop_time)}

    MultiDriver(**kw_options)


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
    multi_driver()
