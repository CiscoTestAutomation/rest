DCNM
====

The following services are supported by the REST connector for DCNM.


get
---

API to send GET command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``api_url``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``headers``, "Headers to send with the GET command", "None"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected, and the fabric name is single_leaf_demo
    url = '/rest/top-down/fabrics/single_leaf_demo/vrfs'
    output = device.rest.get(url)

post
----

API to send POST command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``api_url``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``payload``, "Payload to send to the device", "Mandatory"
    ``headers``, "Headers to send with the GET command", "None"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
    payload = """
    {
       "fabric": "single_leaf_demo",
       "networkName": "MyNetwork_10000",
       "serialNumber": "FDO22230J8W",
       "vlan": "1000",
       "dot1QVlan": 1,
       "untagged": False,
       "detachSwitchPorts": "Ethernet1/5",
       "switchPorts": "",
       "deployment": False
    }
    """
    # Assuming single_leaf_demo fabric is already created
    url = '/rest/top-down/fabrics/single_leaf_demo/networks/MyNetwork_10000/attachments/'
    device.rest.post(url, payload)

delete
------

API to send DELETE command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``api_url``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``headers``, "Headers to send with the GET command", "None"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
    url = '/rest/top-down/fabrics/single_leaf_demo/networks/MyNetwork_10000'
    output = device.rest.delete(url)

patch
-----

API to send PATCH command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``api_url``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``payload``, "Payload to send to the device", "Mandatory"
    ``headers``, "Headers to send with the GET command", "None"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
    payload = """
    {
       "fabric": "single_leaf_demo",
       "networkName": "MyNetwork_10000",
       "serialNumber": "FDO22230J8W",
       "vlan": "1000",
       "dot1QVlan": 1,
       "untagged": False,
       "detachSwitchPorts": "Ethernet1/6",
       "switchPorts": "",
       "deployment": False
    }
    """
    # Assuming single_leaf_demo fabric is already created
    url = '/rest/top-down/fabrics/single_leaf_demo/networks/MyNetwork_10000'
    output = device.rest.patch(url)

put
---

API to send PUT command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``api_url``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``payload``, "Payload to send to the device", "Mandatory"
    ``headers``, "Headers to send with the GET command", "None"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
   payload = """
    {
       "fabric": "single_leaf_demo",
       "networkName": "MyNetwork_10000",
       "serialNumber": "FDO22230J8W",
       "vlan": "1000",
       "dot1QVlan": 1,
       "untagged": False,
       "detachSwitchPorts": "Ethernet1/7",
       "switchPorts": "",
       "deployment": False
    }
    """
    # Assuming single_leaf_demo fabric is already created
    url = '/rest/top-down/fabrics/single_leaf_demo/networks/MyNetwork_10000'
    output = device.rest.put(url)

.. sectionauthor:: Sukanya Kalluri <sukkallu@cisco.com>

