January 2021
============

January 27
----------

+-------------------------------+-------------------------------+
| Module                        | Versions                      |
+===============================+===============================+
| ``rest.connector ``           | 21.1                          |
+-------------------------------+-------------------------------+

Upgrade Instructions
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    pip install --upgrade rest.connector


Features:
^^^^^^^^^
* Moved APIC implementation from NXOS/ACI to APIC

* IOSXE
    * Added sshtunnel support
    * Added protocol key in testbed yaml. Default to https
* NXOS
    * Added sshtunnel support
    * Added protocol key in testbed yaml. Default to https
* VIRL
    * Added sshtunnel support
    * Added protocol key in testbed yaml. Default to http
* DCNM
    * Added sshtunnel support
    * Added protocol key in testbed yaml. Default to https
* NSO
    * Added sshtunnel support
    * Added protocol key in testbed yaml. Default to http
* Viptela
    * Added sshtunnel support
    * Added protocol key in testbed yaml. Default to https
* BIG-IP
    * Added sshtunnel support
    * Added protocol key in testbed yaml. Default to https
