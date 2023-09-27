September 2023
==========

September 26 - Rest v23.9 
------------------------



+-------------------------------+-------------------------------+
| Module                        | Versions                      |
+===============================+===============================+
| ``rest.connector ``           | 23.9                          |
+-------------------------------+-------------------------------+

Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    pip install --upgrade rest.connector




Changelogs
^^^^^^^^^^
--------------------------------------------------------------------------------
                                      Fix                                       
--------------------------------------------------------------------------------

* rest
    * Updated IOSXE Implimentation
        * Changed "connect" method
            * Send a GET request to a common "well-known" IOS-XE YANG model (path /Cisco-IOS-XE-nativenative/version)
            * Debug output to include the received data from the device
            * Content-Type header is not used (default_content_type parameter)


