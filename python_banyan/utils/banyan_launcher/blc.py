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

import argparse
import logging
import signal
import subprocess
import sys
import time
from os.path import expanduser
from subprocess import Popen

import psutil
from apscheduler.schedulers.background import BackgroundScheduler
from python_banyan.banyan_base import BanyanBase


class BLC(BanyanBase):
    """
    This is the banyan launcher client. It receives launch instructions
    from the server and then locally launches and manages those processes.
    """

    def __init__(self, subscriber_port='43125', publisher_port='43124',
                 back_plane_ip_address=None, topic=None):
        """
        :param back_plane_ip_address: address of backplane. This is a required
                                      parameter
        :param subscriber_port: backplane subscriber port
        :param publisher_port:  backplane publisher port
        :param topic: subscriber topic containing launch instructions. This is
                      a required parameter
        """

        # To use this class the backplane address is a required parameter
        if not any((back_plane_ip_address, topic)):
            print('You must specify both the backplane ip address and topic.')
            sys.exit(0)

        # start the logging process

        # get the home directory path
        home = expanduser("~")

        # set up the log file
        logging.basicConfig(filename=home + '/banyan_launcher.log', filemode='w',
                            level=logging.ERROR)

        # a popen process object
        self.proc = None

        # maintain a database of information pertaining to each launch item
        # this will be an array of dictionaries, with each row describing a single launched process
        self.launch_db = []

        # the keys defined for a given row are as follows:
        #
        # auto_restart - restart process if it dies
        # append_bp_address - the backplane ip address appended to
        #                     the command_string with -b option
        # command_string - the command used to launch the process
        # process - the value returned from popen after launching process
        # process_id - pid of launched process
        # spawn - spawn process in its own window
        # topic - used to publish to remote launcher
        # reply_topic - reply topic from remote launcher

        # call the parent class to attach this banyan component to the backplane
        super(BLC, self).__init__(back_plane_ip_address=back_plane_ip_address,
                                  subscriber_port=subscriber_port,
                                  publisher_port=publisher_port,
                                  process_name='Banyan Launch Client',
                                  loop_time=.1)

        print('Listening for ' + topic + ' messages.')

        # subscribe to the launch topic specified in the init parameter
        self.set_subscriber_topic(topic)

        # subscribe to the killall topic to exit this program via message
        self.set_subscriber_topic('killall')

        # start the background scheduler to periodically run check_processes and confirm
        self.scheduler = BackgroundScheduler()
        self.job = self.scheduler.add_job(self.check_local_processes, 'interval', seconds=.5)

        self.scheduler.start()

        try:
            # initial launching is complete, so just wait to receive incoming messages.
            self.receive_loop()
        except (KeyboardInterrupt, SystemExit):
            self.clean_up()

    def spawn_local(self, idx):
        """
        This method launches processes that are needed to run on this computer.
        :param idx: An index into launch_db
        """

        # get the launch entry in launch_db
        db_entry = self.launch_db[idx]

        # skip over the entry for the backplane.
        # there shouldn't be one for the client, but the code is
        # kept consist with the server.
        # launch the process either in its own window or just launch it.
        # differentiate between windows and other os's.
        if not db_entry['command_string'] == 'backplane':
            if sys.platform.startswith('win32'):
                if db_entry['spawn'] == 'yes':
                    self.proc = Popen(db_entry['command_string'],
                                      creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    command_list = db_entry['command_string']
                    self.proc = Popen(command_list, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                if db_entry['spawn'] == 'yes':
                    self.proc = Popen(['xterm', '-e', db_entry['command_string']],
                                      stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
                else:
                    command_list = db_entry['command_string'].split(' ')
                    self.proc = Popen(command_list)

            # update the entry with the launch information
            db_entry['process'] = self.proc
            db_entry['process_id'] = self.proc.pid
            print('{:35} PID = {}'.format(db_entry['command_string'], str(self.proc.pid)))

            # allow a little time for the process to startup
            try:
                time.sleep(0.5)
            except (KeyboardInterrupt, SystemExit):
                # self.scheduler.shutdown()
                self.clean_up()
                sys.exit(0)
    """
    def check_local_processes(self):

        # This method is called by the scheduler periodically.
        # Check to make sure if a local process previously started is still running.
        # If a process is not dead, print that to the console and if the process
        # has the restart flag set, then restart it.
        
        for x, record in enumerate(self.launch_db):

            # ignore backplane
            if not record['command_string'] == 'backplane':
                # get a list of all pids running
                pids = psutil.pids()

                status = None
                # check to see if the process in the launch_db is in this list
                if record['process'].pid in pids:
                    proc = psutil.Process(record['process'].pid)

                    # get the status for this process
                    status = proc.status()

                # if it is not in the list, declare it a zombie to force the print
                if not record['process'].pid in pids:
                    status = psutil.STATUS_ZOMBIE

                if status == psutil.STATUS_ZOMBIE:
                    log_string = '{:35} PID = {} DIED'.format(record['command_string'], str(record['process'].pid))
                    print(log_string)

                    # log_string = record['command_string'] + " PID = " + str(record['process'].pid + 'DIED')
                    logger = logging.getLogger()
                    logger.error(log_string)

                    # reset its state and process, and process ID
                    record['process'] = None
                    record['process_id'] = None

                    # do we need to restart it?
                    if record['auto_restart'] == 'yes':
                        self.spawn_local(x)
    """
    def check_local_processes(self):
        """
        This method is called by the scheduler periodically.
        Check to make sure if a local process previously started is still running.
        If a process is dead, print that to the console and if the process
        has the restart flag set, then restart it.

        Affect the launch_db entry so that only one message is printed and the if
        the process to be restarted, it is restarted once.
        """

        if sys.platform.startswith('win32'):
            for x, record in enumerate(self.launch_db):

                # ignore backplane
                if not record['command_string'] == 'backplane':
                    # get a list of all pids running
                    pids = psutil.pids()

                    # status = None
                    # check to see if the process in the launch_db is in this list
                    if record['process'].pid in pids:
                        proc = psutil.Process(record['process'].pid)

                        # get the status for this process
                        status = proc.status()

                    elif not record['process'].pid in pids:
                        status = psutil.STATUS_ZOMBIE

                    else:
                        status = None

                    # print(status)
                    if status == psutil.STATUS_ZOMBIE:
                        log_string = '{:35} PID = {} DIED'.format(record['command_string'], str(record['process'].pid))
                        print(log_string)

                        # log_string = record['command_string'] + " PID = " + str(record['process'].pid + 'DIED')
                        logger = logging.getLogger()
                        logger.error(log_string)

                        # reset its state and process, and process ID
                        record['process'] = None
                        record['process_id'] = None

                        # do we need to restart it?
                        if record['auto_restart'] == 'yes':
                            self.spawn_local(x)
        else:
            for x, record in enumerate(self.launch_db):
                if not record['command_string'] == 'backplane':
                    if record['process_id']:
                        pids = psutil.pids()
                        # print(record)
                        # check to see if the process in the launch_db is in this list
                        # status = None

                        try:
                            if record['process'].pid in pids:
                                proc = psutil.Process(record['process'].pid)
                                status = proc.status()
                                # print('command: ' + record['command_string'] + 'status: ' + status)

                                if status == psutil.STATUS_SLEEPING:
                                    continue

                                if not status:
                                    status = psutil.STATUS_ZOMBIE

                                if status == psutil.STATUS_ZOMBIE:

                                    log_string = '{:35} PID = {} DIED'.format(record['command_string'],
                                                                              str(record['process'].pid))
                                    print(log_string)

                                    logger = logging.getLogger()
                                    logger.error(log_string)

                                    # reset its process, and process ID
                                    record['process'] = None
                                    record['process_id'] = None

                                    # do we need to restart it?
                                    if record['auto_restart'] == 'yes':
                                        self.spawn_local(x)
                        except AttributeError:
                            pass

    def incoming_message_processing(self, topic, payload):
        """
        Messages are sent here from the receive_loop

        :param topic: Message Topic string
        :param payload: Message Data
        :return:
        """
        # make sure this is not a duplicate launch request

        if topic == 'killall':
            # self.scheduler.shutdown()
            self.clean_up()
            # sys.exit(0)

        else:
            # check to see if the process was already launched and ignore
            # if it was
            for idx, record in enumerate(self.launch_db):
                if record['launch_id'] == payload['launch_id']:
                    return
            # print(topic, payload)
            # idx = len(self.launch_db)
            self.launch_db.append(payload)
            self.spawn_local(len(self.launch_db) - 1)

            record = self.launch_db[-1]

            # pid = str(record['process_id'])
            # send acknowledgement to server
            ack = {'command_string': record['command_string'],
                   'process_id': record['process_id'],
                   'launch_id': record['launch_id']}
            topic = record['reply_topic']
            self.publish_payload(ack, topic)

    def clean_up(self):
        """
        Graceful shutdown - all newly opened windows and associated processes
        are killed
        :return:
        """
        # self.scheduler.shutdown()
        # self.publish_payload({'kill': True}, 'killall')
        # time.sleep(.5)
        self.scheduler.pause()
        for idx, record in enumerate(self.launch_db):
            if record['process']:
                print('{:35} PID = {} KILLED'.format(record['command_string'], str(record['process'].pid)))
                proc = psutil.Process(record['process'].pid)
                proc.kill()
                record['process'] = None
                record['process_id'] = None
        sys.exit(0)


def blc():
    # allow user to bypass the IP address auto-discovery. This is necessary if the component resides on a computer
    # other than the computing running the backplane.

    parser = argparse.ArgumentParser()

    parser.add_argument("-b", dest="back_plane_ip_address", default="None",
                        help="None or IP address used by Back Plane",
                        required=True)
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-t", dest="topic", default='None',
                        help="Command Receiver Topic", required=True)
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")

    args = parser.parse_args()

    kw_options = {
        'back_plane_ip_address': args.back_plane_ip_address,
        'publisher_port': args.publisher_port,
        'subscriber_port': args.subscriber_port,
        'topic': args.topic
    }

    # replace with the name of your class
    BLC(**kw_options)


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
    blc()
