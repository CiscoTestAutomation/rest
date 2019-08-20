""" Utilities shared by all plugin libraries. """

try:
    from pyats.utils.secret_strings import to_plaintext
except ImportError:
    def to_plaintext(string):
        return(str(string))

def get_username_password(connection):
    username = password = None
    if connection.connection_info.get('credentials'):
        try:
            username = str(
                connection.connection_info['credentials']['rest']['username'])
            password = to_plaintext(
                connection.connection_info['credentials']['rest']['password'])
        except Exception:
            pass

    if not username:
        username = connection.connection_info.get('username', \
            connection.device.tacacs.username \
            if connection.device.tacacs.username \
            else 'admin')

    if not password:
        password = connection.connection_info.get('password', \
            connection.device.passwords.tacacs \
            if connection.device.passwords.tacacs \
            else 'admin')

    return (username, password)
