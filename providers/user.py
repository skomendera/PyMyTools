def is_super(connection):

    with connection.cursor() as cursor:

        cursor.execute('show grants for current_user()')

        query_result = cursor.fetchone()

        return 'SUPER' in query_result
