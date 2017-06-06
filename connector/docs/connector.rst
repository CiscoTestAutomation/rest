Connector
=========

Introduction
------------

``Rest`` is a pyATS connection class implementation that allows scripts to
connect to a device using REST via topology/YAML format.

To specify ``Rest`` connection implementation, add the following to your YAML
file:

.. code-block:: yaml

    # Example
    # -------
    #
    #   pyATS testbed yaml example for defining a REST connection

    testbed:
        name: myTestbed

    devices:
        PE1:
            connections:
                # Console
                a:
                    # specify the rest connector class
                    ip: 1.2.3.4
                    port: 10001
                    protocol: telnet
                # Rest connector class
                rest:
                    class: rest.connector.Rest
                    ip: 1.2.3.4

With the above, the testbed loader can then load this YAML into object form.

.. code-block:: python

    # Example
    # -------
    #
    #   loading & using REST testbed yaml file in pyATS

    # import the topology module
    from ats import topology

    # load the above testbed file containing REST device
    testbed = topology.loader.load('/path/to/rest/testbed.yaml')

    # get device by name
    device = testbed.devices['PE1']

    # connect to it 
    device.connect(via='rest')

    # get information of a particular DN
    url = '/api/mo/sys/bgp/inst/dom-default/af-ipv4-mvpn.json'
    output = x.rest.get(url)

    # etc..

Connect
-------

Api to connect to the device.

.. csv-table:: connect arguments
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"

.. code-block:: python

    # Example
    # -------
    #
    #   loading & using REST testbed yaml file in pyATS

    # import the topology module
    from ats import topology

    # load the above testbed file containing REST device
    testbed = topology.loader.load('/path/to/rest/testbed.yaml')

    # get device by name
    device = testbed.devices['PE1']

    # connect to it 
    device.connect(via='rest')

Disconnect
----------

Api to disconnect to the device.

.. csv-table:: disconnect arguments
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"

.. code-block:: python

    # Example
    # -------
    #
    #   loading & using REST testbed yaml file in pyATS

    # import the topology module
    from ats import topology

    # load the above testbed file containing REST device
    testbed = topology.loader.load('/path/to/rest/testbed.yaml')

    # get device by name
    device = testbed.devices['PE1']

    # connect to it 
    device.connect(via='rest')

    # disconnect to it 
    device.disconnect()

Get
---

Api to send GET command to the device.

.. csv-table:: GET arguments
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``rsp_subtree``, "Specifies child object level included in the response", "full"
    ``rsp_foreign_subtree``, "", "ephemeral"
    ``batch_size``, "Size of output to receive per batch", "1000"
    ``batch_id``, "# in the sequence of the batch to receive", "1"
    ``expected_status_code``, "Expected result", "200"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"

.. code-block:: python

    # Assuming the device is already connected
    url = '/api/mo/sys/bgp/inst/dom-default/af-ipv4-mvpn.json'
    output = x.get(url)

Post
----

Api to send POST command to the device.

.. csv-table:: POST arguments
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``payload``, "Payload to send to the device", "Mandatory"
    ``expected_status_code``, "Expected result", "200"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"

.. code-block:: python

    # Assuming the device is already connected
    payload = """
    {
      "bgpInst": {
        "attributes": {
          "isolate": "disabled",
          "adminSt": "enabled",
          "fabricSoo": "unknown:unknown:0:0",
          "ctrl": "fastExtFallover",
          "medDampIntvl": "0",
          "affGrpActv": "0",
          "disPolBatch": "disabled",
          "flushRoutes": "disabled"
        },
        "children": [
          {
            "bgpDom": {
              "attributes": {
                 "name": "default",
                 "pfxPeerTimeout": "30",
                 "pfxPeerWaitTime": "90",
                 "clusterId": "",
                 "maxAsLimit": "0",
                 "reConnIntvl": "60",
                 "rtrId": "0.0.0.0"
              },
              "children": [
                {
                  "bgpRtCtrl": {
                    "attributes": {
                      "logNeighborChanges": "disabled",
                      "enforceFirstAs": "enabled",
                      "fibAccelerate": "disabled",
                      "supprRt": "enabled"
                    }
                  }
                },
                {
                  "bgpPathCtrl": {
                    "attributes": {
                      "alwaysCompMed": "disabled",
                      "asPathMultipathRelax": "disabled",
                      "compNbrId": "disabled",
                      "compRtrId": "disabled",
                      "costCommunityIgnore": "disabled",
                      "medConfed": "disabled",
                      "medMissingAsWorst": "disabled",
                      "medNonDeter": "disabled"
                    }
                  }
                }
              ]
            }
          }
        ]
      }
    }
    """

    url = 'api/mo/sys/bgp/inst.json'
    device.post(url, payload)

Delete
------

Api to send DELETE command to the device.

.. csv-table:: DELETE arguments
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``expected_status_code``, "Expected result", "200"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"

.. code-block:: python

    # Assuming the device is already connected
    url = '/api/mo/sys/bgp/inst/dom-default/af-ipv4-mvpn.json'
    output = device.delete(url)

.. sectionauthor:: Jean-Benoit Aubin <jeaubin@cisco.com>
