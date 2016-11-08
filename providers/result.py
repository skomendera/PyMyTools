from collections import OrderedDict
from providers import value, terminal


def result_format(database_result, fmt):

    format_function = 'result_format_%s' % fmt

    if format_function not in globals():

        raise Exception('Unsupported format "%s"' % fmt)

    return globals()[format_function](database_result)


def result_format_tabular(database_result):

    if len(database_result) == 0:

        return ''

    column_width = OrderedDict()
    text_output = []

    for k in database_result[0].keys():

        column_width[k] = len(k)+1

    for line in database_result:

        for (k, v) in line.items():

            if len(str(v)) > column_width[k]:

                column_width[k] = len(str(v))+1

    output_line = '+'

    for (k, v) in column_width.items():

        output_line += '-' * v + '+'

    text_output.append(output_line)

    output_line = '|'

    for (k, v) in column_width.items():

        output_line += '{:>{width}}|'.format(k, width=column_width[k])

    text_output.append(output_line)

    output_line = '+'

    for (k, v) in column_width.items():
        output_line += '-' * v + '+'

    text_output.append(output_line)

    for line in database_result:

        output_line = '|'

        for k in column_width.keys():

            output_line += '{:>{width}}|'.format(str(line[k]) if line[k] is not None else '', width=column_width[k])

        text_output.append(output_line)

    output_line = '+'

    for (k, v) in column_width.items():
        output_line += '-' * v + '+'

    text_output.append(output_line)

    return '\n'.join(text_output)


def result_format_vertical(database_result):

    if len(database_result) == 0:

        return ''

    text_output = []

    max_label_length = 0

    for k in database_result[0].keys():

        if len(k) > max_label_length:

            max_label_length = len(k)

    row_num = 1

    for line in database_result:

        line_header = '{:*^{width}}'.format(' %s. row ' % row_num, width=64)

        text_output.append(line_header)

        for (k, v) in line.items():

            line_column = terminal.get_key_value_adjusted(k, v, max_label_length)

            text_output.append(line_column)

        row_num += 1

    return '\n'.join(text_output)


def result_format_keyvalue(database_result):

    if len(database_result) == 0:

        return ''

    text_output = []

    for line in database_result:

        kv_list = list(line.values())

        text_output.append('%s=%s' % (kv_list[0], str(kv_list[1])))

    return '\n'.join(text_output)


def convert_to_dict(database_result):

    if len(database_result) == 0:

        return {}

    dict_output = {}

    for line in database_result:

        kv_list = list(line.values())

        dict_output[kv_list[0]] = int(kv_list[1]) if value.represents_int(kv_list[1]) else kv_list[1]

    return dict_output
