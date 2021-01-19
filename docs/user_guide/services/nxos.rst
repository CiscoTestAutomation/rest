NXOS
====

The following services are supported by the REST connector for NXOS.


get
---

API to send GET command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``headers``, "Headers to send with the GET command", "None"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
    url = '/api/mo/sys/bgp/inst/dom-default/af-ipv4-mvpn.json'
    output = device.rest.get(url)

post
----

API to send POST command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``payload``, "Payload to send to the device", "Mandatory"
    ``headers``, "Headers to send with the GET command", "None"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

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

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``headers``, "Headers to send with the GET command", "None"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
    url = '/api/mo/sys/bgp/inst/dom-default/af-ipv4-mvpn.json'
    output = device.rest.delete(url)

patch
-----

API to send PATCH command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``payload``, "Payload to send to the device", "Mandatory"
    ``headers``, "Headers to send with the GET command", "None"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
    payload = """{
        "intf-items": {
          "phys-items": {
            "PhysIf-list": [
              {
                "adminSt": "down",
                "id": "eth1/2",
                "userCfgdFlags": "admin_layer,admin_state"
              }
            ]
          }
        }
      }
    """
    url = '/api/mo/sys/bgp/inst/dom-default/af-ipv4-mvpn.json'
    output = device.rest.patch(url)

put
---

API to send PUT command to the device.

.. csv-table::
    :header: Argument, Description, Default
    :widths: 30, 50, 20

    ``dn``, "Unique distinguished name describes the place in the tree", "Mandatory"
    ``payload``, "Payload to send to the device", "Mandatory"
    ``headers``, "Headers to send with the GET command", "None"
    ``timeout``, "Maximum time it can take to disconnect to the device.", "30 seconds"
    ``expected_return_code``, "Return code that is expected.", "None (Any good result)"

.. code-block:: python

    # Assuming the device is already connected
    payload = """{
        "intf-items": {
          "phys-items": {
            "PhysIf-list": [
              {
                "adminSt": "down",
                "id": "eth1/2",
                "userCfgdFlags": "admin_layer,admin_state"
              }
            ]
          }
        }
      }
    """
    url = '/api/mo/sys/bgp/inst/dom-default/af-ipv4-mvpn.json'
    output = device.rest.put(url)

.. sectionauthor:: Jean-Benoit Aubin <jeaubin@cisco.com>

