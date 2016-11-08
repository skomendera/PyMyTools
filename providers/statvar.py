import time
from collections import defaultdict
from providers import terminal

statvars_custom_formats_dict = {
    'Bytes_sent': 'bytes',
    'Bytes_received': 'bytes',
    'Innodb_buffer_pool_bytes_data': 'bytes',
    'Innodb_buffer_pool_bytes_dirty': 'bytes',
    'Innodb_data_read': 'bytes',
    'Innodb_data_written': 'bytes',
    'Qcache_free_memory': 'bytes',
    'Innodb_row_lock_time': 'milliseconds',
    'AuroraDb_ddl_stmt_duration': 'microseconds',
    'AuroraDb_select_stmt_duration': 'microseconds',
    'AuroraDb_insert_stmt_duration': 'microseconds',
    'AuroraDb_update_stmt_duration': 'microseconds',
    'AuroraDb_delete_stmt_duration': 'microseconds'
}


statvars_formats = {
    'count': [
        {'factor': 1000000, 'abbreviation': 'M'},
        {'factor': 1000, 'abbreviation': 'K'},
        {'factor': 1, 'abbreviation': ''}
    ],
    'bytes': [
        {'factor': 1024 * 1024 * 1024, 'abbreviation': 'G'},
        {'factor': 1024 * 1024, 'abbreviation': 'M'},
        {'factor': 1024, 'abbreviation': 'K'},
        {'factor': 1, 'abbreviation': 'B'}
    ],
    'milliseconds': [
        {'factor': 1000, 'abbreviation': 's'},
        {'factor': 1, 'abbreviation': 'ms'}
    ],
    'microseconds': [
        {'factor': 1000000, 'abbreviation': 's'},
        {'factor': 1000, 'abbreviation': 'ms'},
        {'factor': 1, 'divisor': 1000, 'abbreviation': 'ms'}
    ]
}

statvars_custom_formats = defaultdict(lambda: 'count', statvars_custom_formats_dict)


def statvalue_format(var_name, var_value, raw):

    var_value = float(var_value)

    if raw:

        return round(var_value, 3)

    for f in statvars_formats[statvars_custom_formats[var_name]]:

        if var_value >= f['factor']:

            if 'divsor' in f:

                return '%s %s' % (round(var_value / float(f['divisor']), 2), f['abbreviation'])

            else:

                return '%s %s' % (round(var_value / float(f['factor']), 2), f['abbreviation'])

    return '%s %s' % (round(var_value, 3), f['abbreviation'])


def db_result_to_dict(database_result):

    return_value = {}

    for tmp_field in database_result:

        return_value[tmp_field['Variable_name']] = tmp_field['Value']

    return return_value


def db_result_to_ordered_list(database_result, requested_variables_list):

    result_dict = db_result_to_dict(database_result)

    result_is_valid = validate_result_fields(database_result, requested_variables_list)

    if result_is_valid is not True:

        raise Exception('Key %s not found in database result, check your variable list' % result_is_valid)

    return [result_dict[v] for v in requested_variables_list]


def validate_result_fields(database_result, requested_variables_list):

    result_dict = db_result_to_dict(database_result)

    for var in requested_variables_list:

        if var not in result_dict:

            return var

    return True


def format_header(variables_list, csv):

    tmp_variables = list(variables_list)

    if csv:

        return 'Timestamp UTC,' + ','.join(tmp_variables)

    else:

        return_value = ''

        for var in tmp_variables:

            return_value += ' %s|' % var

        return '      Timestamp UTC|' + return_value


def format_result_row_vertical(variables_list, result_row_ordered):

    return_row = []

    max_label_length = 0

    for v in variables_list:

        if len(v) > max_label_length:

            max_label_length = len(v)

    for i in range(0, len(result_row_ordered)):

        formatted_value = statvalue_format(variables_list[i], result_row_ordered[i], False)

        return_row.append(terminal.get_key_value_adjusted(variables_list[i], formatted_value, max_label_length))

    return '\n'.join(return_row)


def format_result_row_horizontal(variables_list, result_row_ordered, csv):

    return_row = [time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()) + str('' if csv else '|')]

    join_string = ',' if csv else ''

    for i in range(0, len(result_row_ordered)):

        formatted_value = statvalue_format(variables_list[i], result_row_ordered[i], csv)

        if csv:

            return_row.append(str(formatted_value))

        else:

            return_row.append('{:>{width}}|'.format(formatted_value, width=len(variables_list[i]) + 1))

    return join_string.join(return_row)


def calculate_deltas(former_row, latter_row, time_delta):

    return_row = []
    time_delta = float(time_delta)

    for i in range(0, len(former_row)):

        return_row.append((int(latter_row[i]) - int(former_row[i])) / time_delta)

    return return_row


def get_zerofilled_row(variables_list):

    return [0 for i in variables_list]


def get_field_from_db_result(field_name, database_result):

    result_dict = db_result_to_dict(database_result)

    return result_dict[field_name]


def format_information_line(str):

    return '%s %s' % ('*' * 3,  str)


class StatvarResultList:

    max_results = 100

    def __init__(self):

        self._result_list = []

    def add(self, item):

        if len(self._result_list) == self.max_results:
            self._result_list.pop()

        self._result_list.insert(0, item)

    def get(self):

        return self._result_list
