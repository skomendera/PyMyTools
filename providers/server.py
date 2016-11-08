from collections import OrderedDict
from pymysql.cursors import DictCursorMixin, Cursor
import pymysql


class OrderedDictCursor(DictCursorMixin, Cursor):
    dict_type = OrderedDict


def get_aurora_id(connection):

    with connection.cursor() as cursor:

        try:

            cursor.execute('select @@aurora_server_id')

            return cursor.fetchone()[0]

        except pymysql.err.InternalError as e:

            return '<unknown>'


def get_global_variable(connection, variable_name):

    with connection.cursor() as cursor:

        cursor.execute('select @@%s as v' % variable_name)

        return cursor.fetchone()[0]


def set_global_variable(connection, variable_name, variable_value):

    with connection.cursor() as cursor:

        sql = "set global %s = '%s'" % (variable_name, variable_value)

        try:

            cursor.execute(sql)
            return {'status': True, 'result': sql}

        except pymysql.err.InternalError as e:

            return {'status': False, 'result': 'Command failed (%s): %s' % (sql, e[1])}


def execute_raw_dict(connection, query, fetch_one=False):

    with connection.cursor(OrderedDictCursor) as cursor:

        cursor.execute(query)

        if fetch_one:

            return cursor.fetchone()

        else:

            return cursor.fetchall()


def get_trx_purge_info(connection):

    text_output = []

    with connection.cursor(OrderedDictCursor) as cursor:

        cursor.execute('show engine innodb status')

        tmp_result = cursor.fetchone()

        tmp_result = tmp_result['Status'].split('\n')

        for line in tmp_result:

            if line.startswith(('Trx id counter', 'Purge done for', 'History list length')):

                text_output.append(line)

    return '\n'.join(text_output)


def get_trx_id_counter_from_purge_info(purge_info):

    for line in purge_info.split('\n'):

        if line.startswith('Trx id counter'):

            return int(line.split(' ').pop())


def get_uptime(connection):

    with connection.cursor(pymysql.cursors.DictCursor) as cursor:

        cursor.execute("SHOW GLOBAL STATUS LIKE 'Uptime'")
        server_uptime = cursor.fetchone()
        return server_uptime['Value']


def get_cluster_topology(connection):

    with connection.cursor(pymysql.cursors.DictCursor) as cursor:

        cursor.execute('select * from information_schema.replica_host_status')

        return cursor.fetchall()
