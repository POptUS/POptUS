import os
import platform


def get_username():
    """
    :return: Username of the account that calls this function
    """
    os_name = platform.system().lower()
    if os_name in ['linux', 'darwin']:
        if 'LOGNAME' not in os.environ:
            raise ValueError('Could not get user name on *nix system')
        return os.environ['LOGNAME']
    elif os_name == 'windows':
        if 'USERNAME' not in os.environ:
            raise ValueError('Could not get user name on Windows system')
        return os.environ['USERNAME']

    raise ValueError(f"Unknown operating system {os_name}")
