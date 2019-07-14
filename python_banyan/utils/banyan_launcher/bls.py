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
import copy
import csv
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


# noinspection PyTypeChecker
class BLS(BanyanBase):
    """
    This is the banyan launcher server. It reads a user .csv
    processor descriptor file. This file describes all processes
    to be launched locally as well as remotely.

    Format for the file is described as:
    command_string,spawn,topic,append_bp_address,auto_restart

    Where:
        command string is the command to issue
        spawn = yes or no. If yes the command is spawned in its own window
        topic = local if the process should be run on this computer.
                For clients, it is the topic they will be listening for
                to get their launch instructions
        append_bp_address = yes or no. If yes a -b command line option with
                            the IP address of this computer is appended to the
                            command string.
        auto_restart = yes or no. If yes, if the process dies it will be restarted.

    """

    def __init__(self, subscriber_port='43125', publisher_port='43124',
                 descriptor_file='launch.csv', ):
        """
        Initialize the launch server
        :param subscriber_port: backplane subscriber port
        :param publisher_port:  backplane publisher port
        :param descriptor_file: .csv process descriptor file
        """

        # get the path to the home directory
        home = expanduser("~")

        # start the logging process
        # the log file will be found in the user's home directory

        logging.basicConfig(filename=home + '/banyan_launcher.log', filemode='w',
                            level=logging.ERROR)

        # a popen process object
        self.proc = None

        # create a launch_id counter
        self.launch_id = 1

        # maintain a database of information pertaining to each launch item
        # this will be an array of dictionaries, with each row describing a single launch process
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
        # launch_id - id so that remote can differentiate multiple instances of a component

        self.empty_launch_entry = {'append_bp_address': 'no', 'auto_restart': 'no',
                                   'command_string': None, 'process': None, 'process_id': None,
                                   'spawn': 'no', 'topic': None, 'reply_topic': None,
                                   'launch_id': None
                                   }

        # create an instance of an empty launch_db entry
        new_entry = copy.deepcopy(self.empty_launch_entry)

        # backplane status string
        bp_string = ""

        # checking running processes.
        # if the backplane is already running, just note that and move on.
        for pid in psutil.pids():
            p = psutil.Process(pid)
            if p.name() == "backplane":
                new_entry['process_id'] = p
                bp_string = "Backplane already running.          PID = " + str(p.pid)
                self.backplane_exists = True
            else:
                continue

        # if backplane is not already running, start a new instance
        if not new_entry['process_id']:
            self.proc = Popen(['backplane'],
                              stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE)
            new_entry['process'] = self.proc
            new_entry['process_id'] = self.proc.pid

        # prepare an entry for the launch_db table
        new_entry['command_string'] = 'backplane'
        new_entry['wait'] = '0'

        # add the backplane entry to the launch database
        self.launch_db.append(new_entry)

        # call the parent class to attach this banyan component to the backplane
        super(BLS, self).__init__(subscriber_port=subscriber_port,
                                  publisher_port=publisher_port, process_name='Banyan Launch Server',
                                  loop_time=.1)

        # read in the descriptor file
        with open(descriptor_file) as csvfile:
            reader = csv.DictReader(csvfile)
            # add a field for pid
            for row in reader:
                # get an empty entry for launch_db
                new_entry = copy.deepcopy(self.empty_launch_entry)
                # add all fields to an empty launch database entry
                # add additional fields not specified in the csv file
                new_entry['topic'] = row['topic']
                new_entry['auto_restart'] = row['auto_restart']
                new_entry['append_bp_address'] = row['append_bp_address']
                new_entry['command_string'] = row['command_string']
                new_entry['spawn'] = row['spawn']
                new_entry['wait'] = row['wait']

                # if the topic is not 'local' then create a reply topic
                # and check if the command needs to have a -b option appended
                if not row['topic'] == 'local':
                    new_entry['reply_topic'] = 'ACK' + new_entry['topic']
                    # print(new_entry['reply_topic'])
                    self.set_subscriber_topic(new_entry['reply_topic'])
                    if new_entry['append_bp_address'] == 'yes':
                        new_entry['command_string'] = new_entry['command_string'] + ' -b ' + self.back_plane_ip_address
                    new_entry['launch_id'] = self.launch_id
                    self.launch_id += 1

                # add the populated record to launch_db
                self.launch_db.append(new_entry)

        # display pid of backplane either just invoked or already running
        if not bp_string:
            print('backplane                           PID = {}'.format(str(self.proc.pid)))
        else:
            print(bp_string)

        # launch local processes or send launch messages to remotes
        for idx, record in enumerate(self.launch_db):
            # skip over the backplane entry
            if not record['command_string'] == 'backplane':
                #
                if record['topic'] == 'local':
                    self.spawn_local(idx)
                else:
                    self.publish_payload(record, record['topic'])
            try:
                if int(record['wait']) > 0:
                    time.sleep(int(record['wait']))
            except TypeError:
                print(record)
                raise

        # start the background scheduler to periodically run check_processes and confirm methods
        self.scheduler = BackgroundScheduler()
        self.job = self.scheduler.add_job(self.check_local_processes, 'interval', seconds=.5)
        self.job2 = self.scheduler.add_job(self.confirm_remote, 'interval', seconds=5)

        # subscribe to the killall topic to exit when received
        self.set_subscriber_topic('killall')

        # start the schedule running
        self.scheduler.start()

        try:
            # initial launching is complete, so just wait to receive incoming messages.
            self.receive_loop()
        except (KeyboardInterrupt, SystemExit):
            self.clean_up()

    def spawn_local(self, idx):
        """
        This method launches processes that are needed to run on this computer
        :param idx: An index into launch_db
        """

        # get the launch entry in launch_db
        db_entry = self.launch_db[idx]

        # skip over the entry for the backplane
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
                self.clean_up()

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
        print(topic)
        if topic == 'killall':
            self.clean_up()

        # update the launch_db record for the remote process so that we do not send additional launch commands
        for idx, record in enumerate(self.launch_db):
            # if no launch id has already been assigned, update the record and print a message
            # if not record['launch_id']:
            # is this an acknowledgement from the remote launch?
            if record['launch_id']:
                if record['launch_id'] == payload['launch_id']:
                    self.launch_db[idx]['process_id'] = payload['process_id']
                    print('{}: {:25} PID = {}'.format(topic, record['command_string'], str(payload['process_id'])))
                    break

    def confirm_remote(self):
        """
        This method checks to see if the remote sides acknowledged starting their processes.
        If not, resend them
        :return:
        """

        for idx, record in enumerate(self.launch_db):
            if not record['process_id']:
                if record['topic'] != 'local':
                    self.publish_payload(record, record['topic'])

    def clean_up(self):
        """
        Graceful shutdown - all newly opened windows and associated processes
        are killed
        :return:
        """
        self.scheduler.pause()

        for idx, record in enumerate(self.launch_db):
            if record['process']:

                print('{:35} PID = {} KILLED'.format(record['command_string'], str(record['process'].pid)))
                try:
                    proc = psutil.Process(record['process'].pid)
                    for c in proc.children(recursive=True):
                        c.kill()
                    proc.kill()
                    record['process'] = None
                    record['process_id'] = None
                    # this is necessary for killing the command windows in Windows
                    if proc.name() == record['command_string']:
                        proc.kill()
                except psutil.NoSuchProcess:
                    pass

        super(BLS, self).clean_up()
        sys.exit(0)


def bls():
    # allow user to bypass the IP address auto-discovery. This is necessary if the component resides on a computer
    # other than the computing running the backplane.

    parser = argparse.ArgumentParser()

    parser.add_argument("-f", dest="descriptor_file", default='launch.csv',
                        help="csv descriptor file")
    parser.add_argument("-p", dest="publisher_port", default='43124',
                        help="Publisher IP port")
    parser.add_argument("-s", dest="subscriber_port", default='43125',
                        help="Subscriber IP port")

    args = parser.parse_args()

    kw_options = {
        'publisher_port': args.publisher_port,
        'subscriber_port': args.subscriber_port,
        'descriptor_file': args.descriptor_file, }

    # replace with the name of your class
    BLS(**kw_options)


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
    bls()
