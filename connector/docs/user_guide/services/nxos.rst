NXOS
====

The following services are supported by the REST connector for NXOS.


get
---

API to send GET command to the device.

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
    output = device.rest.get(url)

post
----

API to send POST command to the device.

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
    device.rest.post(url, payload)

delete
------

API to send DELETE command to the device.

.. csv-table:: DELETE arguments
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``expected_status_code``, "Expected result", "200"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"

.. code-block:: python

    # Assuming the device is already connected
    url = '/api/mo/sys/bgp/inst/dom-default/af-ipv4-mvpn.json'
    output = device.rest.delete(url)


.. sectionauthor:: Jean-Benoit Aubin <jeaubin@cisco.com>

