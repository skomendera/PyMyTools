from __future__ import print_function
import argparse
import getpass
import pymysql
import time
import sys

from datetime import datetime

pmt_version = '0.1'


class PyMyToolsArgParser:
    parser = None
    args = None

    def __init__(self, tool_name, endpoint_type='instance'):
        self.parser = argparse.ArgumentParser(description=tool_name)

        host_socket_group = self.parser.add_mutually_exclusive_group(required=True)

        if endpoint_type == 'instance':
            host_socket_group.add_argument('--host', help='Host address', default=None, type=str)

        elif endpoint_type == 'cluster':
            host_socket_group.add_argument('--host', help='Cluster DNS endpoint', default=None, type=str)

        else:
            raise Exception('Unsupported endpoint type: %s' % endpoint_type)

        host_socket_group.add_argument('--socket', help='Socket', default=None, type=str)

        self.parser.add_argument('--port', help='Port (default: 3306)', default=3306, type=int)
        self.parser.add_argument('--user', help='User', default=None, type=str, required=True)
        self.parser.add_argument('--password', help='Password (default: prompt)', default=None, type=str)
        self.parser.add_argument('--run-at', help='Run at the specified time (UTC), format: YYYY-MM-DDTHH:MM:SS '
                                                  '(example: 2016-10-31T12:25:00)', default=None)

    def parse_args(self):

        self.parser.add_argument('--version', help='Show version number and exit', action='store_true', default=False)

        self.args = vars(self.parser.parse_args())

    def handle_version(self):

        if self.args['version'] is True:

            print('PyMyTools version %s' % pmt_version)
            sys.exit(0)

    def handle_connection_parameters(self):
        self.args['password'] = getpass.getpass() if self.args['password'] is None else self.args['password']


class PyMyToolsConnection:
    connection = None

    connection_type = None

    db_host = None
    db_port = None
    db_socket = None
    db_user = None
    db_password = None

    def __init__(self, arg_parser):

        self.connection_type = 'socket' if arg_parser.args['host'] is None else 'tcp'

        self.db_host = arg_parser.args['host']
        self.db_port = arg_parser.args['port']
        self.db_socket = arg_parser.args['socket']
        self.db_user = arg_parser.args['user']
        self.db_password = arg_parser.args['password']

    def disconnect(self):

        self.connection.close()

    def connect(self, exit_on_error=True):

        try:

            if self.connection_type == 'tcp':

                self.connection = pymysql.connect(host=self.db_host,
                                                  port=self.db_port,
                                                  user=self.db_user,
                                                  password=self.db_password,
                                                  autocommit=True,
                                                  connect_timeout=2)

            elif self.connection_type == 'socket':

                self.connection = pymysql.connect(unix_socket=self.db_socket,
                                                  user=self.db_user,
                                                  password=self.db_password,
                                                  autocommit=True,
                                                  connect_timeout=2)

        except pymysql.Error as e:

            print('Could not connect to server: %s' % e)

            if exit_on_error:
                sys.exit(1)

        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:

            cursor.execute("set session sql_mode = 'no_engine_substitution', time_zone = '+0:00'")


class PyMyToolsDelay:

    start_time = None

    def __init__(self, arg_parser):

        if arg_parser.args['run_at'] is not None:

            try:

                self.start_time = datetime.strptime(arg_parser.args['run_at'], "%Y-%m-%dT%H:%M:%S")

                if self.start_time <= datetime.utcnow():
                    print('!!! Start time is in the past, check your parameters')
                    sys.exit(1)

            except ValueError:

                print('!!! Incorrect time format, must be YYYY-MM-DDTHH:MM:SS (example: 2016-10-31T12:25:00)')
                sys.exit(1)

    def delay(self):

        if self.start_time is not None:

            print('Sleeping until %s UTC (T+%s)' % (self.start_time, self.start_time - datetime.utcnow()))

            while self.start_time > datetime.utcnow():
                time.sleep(1)
