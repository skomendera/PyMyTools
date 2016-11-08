import os


def get_terminal_columns():

    terminal_rows, terminal_columns = os.popen('stty size', 'r').read().split()
    return int(terminal_columns)


def get_terminal_rows():

    terminal_rows, terminal_columns = os.popen('stty size', 'r').read().split()
    return int(terminal_rows)


def get_header_l1(lines_list, width=None):

    text_output = []

    if width is None:

        width = get_terminal_columns()

    text_output.append('')
    text_output.append('%s%s%s' % ('+', '-' * (width-2), '+'))

    for line in lines_list:

        text_output.append('| {:<{width}}|'.format(line, width=width-3))

    text_output.append('%s%s%s' % ('+', '-' * (width - 2), '+'))
    text_output.append('')

    return '\n'.join(text_output)


def get_header_l2(lines_list, width=None):

    text_output = []

    if width is None:

        width = 0

        for line in lines_list:

            if len(line) > width:

                width = len(line)

        width += 5

    text_output.append('')
    text_output.append('#')
    text_output.append('##')

    for line in lines_list:

        text_output.append('### ' + line)

    text_output.append('-' * width)
    text_output.append('')

    return '\n'.join(text_output)


def get_key_value_adjusted(key, value, key_width):

    return '{:>{width}}'.format(key, width=key_width) + ': ' + str(value)


def format_seconds(seconds):

    output = []

    seconds = int(seconds)

    if seconds > 86400:

        output.append('%s days' % round(seconds / 86400))
        seconds %= 86400

    if seconds > 3600:

        output.append('%s hours' % round(seconds / 3600))
        seconds %= 3600

    if seconds > 60:

        output.append('%s minutes' % round(seconds / 60))
        seconds %= 60

    if seconds > 0:

        output.append('%s seconds' % seconds)

    return ' '.join(output)
