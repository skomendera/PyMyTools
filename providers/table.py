import pymysql
from providers import schema, server


def find_schema(connection, table_name):

    with connection.cursor(pymysql.cursors.DictCursor) as cursor:

        system_schema_string = ','.join(['%s'] * len(schema.system_schemas))

        cursor.execute("select table_schema from information_schema.tables where table_name = '%s' and table_schema "
                       "not in (%s)" % (table_name, system_schema_string), tuple(schema.system_schemas))

        return cursor.fetchall()


def exists_in_schema(connection, table_name, table_schema):

    query = "select 1 from information_schema.tables where table_schema = '%s' and table_name = '%s'"\
          % (table_schema, table_name)

    query_result = server.execute_raw_dict(connection, query)

    return len(query_result) > 0


def get_show_create(connection, table_name, table_schema):

    return_value = {}

    query = 'show create table %s.%s' % (table_schema, table_name)

    query_result = server.execute_raw_dict(connection, query, True)

    if 'Create Table' in query_result:

        return_value['type'] = 'table'
        return_value['definition'] = query_result['Create Table']

    else:

        return_value['type'] = 'view'
        return_value['definition'] = query_result['Create View']

    return return_value


def get_size(connection, table_name, table_schema):

    query = 'select table_rows, avg_row_length, round(data_length/1024/1024/1024, 3) as data_gb, ' \
            'round(index_length/1024/1024/1024, 3) as index_gb from information_schema.tables ' \
            "where table_schema = '%s' and table_name = '%s'" % (table_schema, table_name)

    query_result = server.execute_raw_dict(connection, query, True)

    query_result['total_gb'] = query_result['data_gb'] + query_result['index_gb']

    return query_result


def get_index_stats(connection, table_name, table_schema):

    query = 'select non_unique, index_name, seq_in_index, column_name, cardinality ' \
            "from information_schema.statistics where table_schema = '%s' and table_name = '%s'" \
            % (table_schema, table_name)

    return server.execute_raw_dict(connection, query)


def get_indexes(connection, table_name, table_schema):

    query = 'select index_name, column_name from information_schema.statistics ' \
            "where table_schema = '%s' and table_name = '%s' order by seq_in_index" % (table_schema, table_name)

    query_result = server.execute_raw_dict(connection, query)

    return_value = {}

    for line in query_result:

        if line['index_name'] not in return_value:

            return_value[line['index_name']] = []

        return_value[line['index_name']].append(line['column_name'])

    return return_value


def get_redundant_indexes(index_info_dict):

    return_value = {}
    index_info_serialized = {}

    for (k, v) in index_info_dict.items():

        index_info_serialized[k] = ','.join(v)

    for (k1, v1) in index_info_serialized.items():

        for (k2, v2) in index_info_serialized.items():

            if k1 != k2 and v2.startswith(v1):

                if k1 not in return_value:

                    return_value[k1] = []

                return_value[k1].append(k2)

    return return_value


def get_unbound_textual_indexes(connection, table_name, table_schema):

    # we're only looking for unbound char and varchar keys, texts and blobs must have a prefix by definition
    # this query may look stupid but it's not using a join in order to avoid server-wide FRM scan

    query = 'select s.index_name from information_schema.statistics s ' \
            "where s.table_schema = '%(schema)s' and s.table_name = '%(table)s' and s.sub_part is null " \
            'and s.column_name in (select c.column_name from information_schema.columns c ' \
            "where c.table_schema = '%(schema)s' and c.table_name = '%(table)s' " \
            "and c.data_type in ('char', 'varchar'))" % {'table': table_name, 'schema': table_schema}

    return server.execute_raw_dict(connection, query)


def analyze(connection, table_name, table_schema):

    query = 'analyze table %s.%s' % (table_schema, table_name)

    return server.execute_raw_dict(connection, query)


def get_custom_sample_pages(connection, table_name, table_schema):

    sample_pages = None

    query = "select create_options from information_schema.tables where table_schema = '%s' and table_name = '%s'" % \
            (table_schema, table_name)

    query_result = server.execute_raw_dict(connection, query, True)

    for option in query_result['create_options'].split():

        if option.startswith('stats_sample_pages'):

            sample_pages = option.split('=').pop()

    return sample_pages


def set_sample_size(connection, table_name, table_schema, sample_size):

    query = 'alter table %s.%s stats_sample_pages = %s' % (table_schema, table_name, sample_size)

    server.execute_raw_dict(connection, query)
