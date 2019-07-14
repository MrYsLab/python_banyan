"""
backplane.py


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
import signal
import socket
import sys
import time
import argparse
import zmq
import zmq.utils.win32


# noinspection PyMethodMayBeStatic,PyBroadException
class BackPlane:
    """
    This class instantiates a ZeroMQ forwarder that acts as the python_banyan software backplane.
    All other components use a common TCP address to connect to the backplane and have their messages forwarded.

    See http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/devices/forwarder.html for info on forwarder
    """

    def __init__(self, subscriber_port='43125', publisher_port='43124', backplane_name='',
                 loop_time=.001):
        """
        This is the initializer for the Python Banyan BackPlane class. The class must be instantiated
        before starting any other Python Banyan components

        :param subscriber_port: subscriber IP port number

        :param publisher_port: publisher IP port number

        :param backplane_name: name to appear on the console for this backplane

        :param loop_time: event loop idle timer
        """

        # get ip address of this machine

        # create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # use the google dns to figure out the machine's address and use that address for the backplane.
        # this precludes the necessity of having a network configuration file.
        # noinspection PyPep8
        try:
            s.connect(('8.8.8.8', 1))
            self.bp_ip_address = s.getsockname()[0]
        except:
            self.bp_ip_address = '127.0.0.1'
        finally:
            s.close()

        print('\n******************************************')
        if backplane_name == "":
            print('Backplane IP address: ' + self.bp_ip_address)
        else:
            print(backplane_name + ' Backplane IP address: ' + self.bp_ip_address)
        print('Subscriber Port = ' + subscriber_port)
        print('Publisher  Port = ' + publisher_port)
        print('Loop Time = ' + str(loop_time) + ' seconds')
        print('******************************************')

        self.loop_time = loop_time
        # create a zmq instance for the backplane
        self.bp = zmq.Context()

        # establish bp as python_banyan ZMQ FORWARDER Device

        # setup up socket that all components will connect and publish to
        self.publish_to_bp = self.bp.socket(zmq.SUB)
        bind_string = 'tcp://' + self.bp_ip_address + ':' + publisher_port
        self.publish_to_bp.bind(bind_string)

        # Don't filter any incoming messages, just pass them through
        try:
            # for python 3
            self.publish_to_bp.setsockopt_string(zmq.SUBSCRIBE, '')
        except TypeError:
            # for python 2
            self.publish_to_bp.setsockopt(zmq.SUBSCRIBE, '')

        # setup socket that all subscribers will connect to
        self.subscribe_to_bp = self.bp.socket(zmq.PUB)
        bind_string = 'tcp://' + self.bp_ip_address + ':' + subscriber_port
        self.subscribe_to_bp.bind(bind_string)

        # instantiate the forwarder device
        try:
            with zmq.utils.win32.allow_interrupt(self.clean_up):
                zmq.device(zmq.FORWARDER, self.publish_to_bp, self.subscribe_to_bp)
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit()

    def run_back_plane(self):
        """
        This method runs the backplane in a do nothing forever loop to keep the back plane alive.
        :return:
        """
        while True:
            try:
                time.sleep(self.loop_time)
            except KeyboardInterrupt:
                sys.exit(0)

    def clean_up(self):
        """
        Close the zmq publish and subscribe sockets and release the zmq context
        :return:
        """
        self.publish_to_bp.close()
        self.subscribe_to_bp.close()
        self.bp.term()


def bp():
    """
    Instantiate the backplane and run it.
    Attach a signal handler for the process to listen for user pressing Control C

    usage: backplane [-h] [-n BACKPLANE_NAME] [-p PUBLISHER_PORT] [-s SUBSCRIBER_PORT] [-t LOOP_TIME]

    optional arguments:

      -h, --help          show this help message and exit

      -n BACKPLANE_NAME   Name of this backplane

      -p PUBLISHER_PORT   Publisher IP port

      -s SUBSCRIBER_PORT  Subscriber IP port

      -t LOOP_TIME        Event Loop Timer in seconds

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", dest="backplane_name", default="", help="Name of this backplane")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")
    parser.add_argument("-t", dest="loop_time", default=".001", help="Event Loop Timer in seconds")

    args = parser.parse_args()
    kw_options = {'publisher_port': args.publisher_port, 'subscriber_port': args.subscriber_port,
                  'backplane_name': args.backplane_name, 'loop_time': float(args.loop_time)}
    # replace with the name of your class
    backplane = BackPlane(**kw_options)
    backplane.run_back_plane()


# signal handler function called when Control-C occurs
# noinspection PyShadowingNames,PyUnusedLocal
def signal_handler(sig, frame):
    print('Exiting Through Signal Handler')
    raise KeyboardInterrupt


# listen for SIGINT
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    bp()
