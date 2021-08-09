""" Utilities shared by all plugin libraries. """
from pkg_resources import get_distribution, DistributionNotFound
import re
import requests
import subprocess

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


def get_token(connection):
    token = None
    if connection.connection_info.get('credentials'):
        try:
            token = str(
                connection.connection_info['credentials']['rest']['token'])
        except Exception:
            pass

    return token


def get_apic_sdk_version(ip):
    """
    :param ip: IP or hostname of the APIC controller
    :return: version of the APIC software as noted in the /cisco page
    """
    version = None
    url = f'https://{ip}/cobra'

    response = requests.get(url, verify=False)

    if response.status_code == requests.codes.ok:
        match = re.search(r'<title>.*\s([\d.]+)\s.*</title>', response.text)
        if match:
            version = match.groups()[0]

    return version


def get_installed_lib_versions(packages=('acicobra', 'acimodel')):
    """
    :param packages: (tuple) a list of packages to be checked
    :return: dictionary with packages as keys and versions as values
    """
    if not isinstance(packages, tuple) and not isinstance(packages, list):
        packages = [packages]
    versions = {}
    for package in packages:
        try:
            versions[package] = get_distribution(package).version
        except DistributionNotFound:
            versions[package] = None

    return versions


def get_file_links(ip, packages=('acicobra', 'acimodel')):
    """
    :param ip: IP or hostname of the APIC controller
    :param packages: (tuple) a list of packages to be downloaded
    :return: dictionary containing package names as keys and full path to files
    """
    if not isinstance(packages, list):
        packages = [packages]
    url = f'https://{ip}/cobra/_downloads'
    links_dict = {}

    r = requests.get(url, verify=False)
    files = re.findall(r'<a href=([\w\d.-]+.whl)>', r.text)

    for package in packages:
        for file in files:
            if package in file:
                links_dict[package] = f'{url}/{file}'

    return links_dict


def pip_install_from_link(ip, link=''):
    """
    :param ip: IP or hostname of the APIC controller
    :param link: link to file (https://{ip}/cobra/_downloads/{file_name})
    :return: True if install succeeded, False otherwise
    """
    params = ['pip', 'install', f'--trusted-host={ip}', link]

    r = subprocess.run(params)
    if r.returncode:
        return False
    return True


def verify_apic_version(ip):
    apic_version = get_apic_sdk_version(ip=ip)
    installed = get_installed_lib_versions(packages=['acicobra', 'acimodel'])

    if apic_version and any(map(lambda x: x != apic_version, installed)):
        links_dict = get_file_links(ip=ip, packages=[k for k, v in
                                                     installed.items()
                                                     if v != apic_version])
        for package in links_dict:
            if not pip_install_from_link(ip=ip, link=links_dict[package]):
                raise RuntimeError('There seems to be a problem with the '
                                   f'{package} automated installation.\n'
                                   'Please install packages manually from APIC')
