"""
Collection of response hooks available for requests Session instances
across all implementations.
"""
from logging import getLogger

from requests import Response
from requests.exceptions import RequestException

log = getLogger(__name__)

def default_response_hook(response: Response, *args, **kwargs) -> Response:
    """
    Default response hook. Raise for status, catch any desired exceptions,
    then raise a meaningful exception for the caller.

    :param response: Requests response object for the last call
    :param args: Additional arguments to pass to the hook
    :param kwargs: Additional keyword arguments passed to the hook
    :return: Response object, assuming no exceptions re-raised
    """
    try:
        response.raise_for_status()
    except RequestException as e:
        log.critical("An error occurred while making request:\n%s\n",
                     e,
                     exc_info=True)
        raise RequestException(e) from e
    return response
