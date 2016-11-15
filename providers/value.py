def represents_int(value):

    try:

        int(value)
        return True

    except ValueError:

        return False


def bytes_to_gib(byte_value, round_digits=2):

    return round(byte_value / 1024 / 1024 / float(1024), round_digits)


def count_to_millions(count_value, round_digits=3):

    return round(count_value / float(1000000), round_digits)
