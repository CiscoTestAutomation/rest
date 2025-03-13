"""
Utility functions available to all tests
"""
import os
from logging import getLogger
import json
from ipaddress import IPv6Address

from pyats.topology import loader

log = getLogger(__name__)

HERE = os.path.dirname(__file__)

def generate_mock_server_url(testbed_device: object,
                             connection_name: str) -> str:
    """
    Common function to generate a mock server base URL based on testbed
    attributes (protocol, host, post)

    :param testbed_device: Testbed device object
    :param connection_name: Test connection being tested
    """
    # Test for IPv6, set the mocker URL accordingly
    protocol = testbed_device.connections[connection_name].protocol
    port = testbed_device.connections[connection_name].port

    try:
        destination_host = testbed_device.connections[connection_name].host
    except AttributeError:
        destination_host = testbed_device.connections[connection_name].ip
        if isinstance(destination_host, IPv6Address):
            destination_host = f"[{IPv6Address(destination_host).exploded}]"

    mock_url = f"{protocol}://{destination_host}:{port}/"
    return mock_url

def get_testbed(testbed_file="testbed.yaml"):
    """
    Load and return the testbed for unittests

    :param testbed_file: Filename of the testbed to return
    """
    return loader.load(os.path.join(HERE, testbed_file))

def return_all_request_data_from_mocker(request, context):
    """
    Use this function as the "text" parameter in requests_mock to return
    the headers and message-body received from a request back to the client.

    Useful to verify that an encoded message-body matches the expected
    (e.g. that a dict was actually encoded in XML or that an Authorization
    header matches the expected value)

    Example usage:

     kwargs['mock'].get(url, text=return_all_request_data_from_mocker)
    """
    response_body = {
        "headers": dict(request.headers),
        "body": request.text
    }
    context.status_code = 200
    return json.dumps(response_body)
