from collections import OrderedDict
from pymysql.cursors import DictCursorMixin, Cursor


class OrderedDictCursor(DictCursorMixin, Cursor):
    dict_type = OrderedDict

system_schemas = ['information_schema', 'performance_schema', 'mysql']


def get_list(connection, exclude_system=False):

    schemas = []

    with connection.cursor(OrderedDictCursor) as cursor:

        cursor.execute('show schemas')

        tmp_result = cursor.fetchall()

        for s in tmp_result:

            if exclude_system and s['Database'] in system_schemas:

                pass

            else:

                schemas.append(s['Database'])

    return schemas
