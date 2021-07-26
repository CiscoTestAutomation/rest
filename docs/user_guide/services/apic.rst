APIC
====

The following services are supported by the REST connector for APIC.


get
---

API to send GET command to the device.

.. list-table:: GET arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - dn
      - Unique distinguished name describes the object and its place in the tree
      - Mandatory
    * - query_target {self|children|subtree}
      - | 'self': (default) MO itself
        | 'children': just the MO's child objects
        | 'subtree': MO and its child objects
      - self
    * - rsp_subtree {no|children|full}
      - | Specifies child object level included in the response
        | 'no': (default) the response does not include any children
        | 'children': return only the child objects
        | 'full': includes the full tree structure
      - no
    * - rsp_prop_include {all|naming-only|config-only}
      - | 'all': all properties of the objects
        | 'naming-only': only the naming properties
        | 'config-only': only configurable properties
      - all
    * - rsp_subtree_include (string)
      - specify additional contained objects or options to be included
      - None
    * - rsp_subtree_class (string)
      - specify classes
      - None
    * - query_target_filter (string)
      - filter expression
      - None
    * - target_subtree_class (string)
      - specify class
      - None
    * - expected_status_code (int)
      - Expected result
      - None
    * - timeout
      - Maximum time it can take to disconnect to the device
      - 30 seconds

.. code-block:: python

    # Assuming the device is already connected
    url = 'api/node/class/fvTenant.json'
    output = device.get(url, query_target='self', rsp_subtree='no',
                        query_target_filter='', rsp_prop_include='all')

post
----

API to send POST command to the device.

.. list-table:: POST arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - dn
      - Unique distinguished name describes the object and its place in the tree
      - Mandatory
    * - payload (dict)
      - Information to send via the post command
      - Mandatory
    * - xml_payload (bool)
      - Set to True if payload is in XML format
      - False
    * - expected_status_code (int)
      - Expected result
      - 200
    * - timeout (int)
      - Maximum time it can take to disconnect to the device
      - 30 seconds

.. code-block:: python

    # Assuming the device is already connected
    payload = """
    {
      "fvTenant": {
        "attributes": {
          "dn": "uni/tn-test",
          "name": "test",
          "rn": "tn-test",
          "status": "created"
        },
        "children": []
    }
    """

    url = 'api/node/mo/uni/tn-test.json'
    device.rest.post(url, payload)

delete
------

API to send DELETE command to the device.

.. list-table:: DELETE arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - dn (string)
      - Unique distinguished name describes the object and its place in the tree
      - Mandatory
    * - expected_status_code (int)
      - Expected result
      - 200
    * - timeout (int)
      - Maximum time it can take to disconnect to the device
      - 30 seconds

.. code-block:: python

    # Assuming the device is already connected
    url = 'api/v1/schema/583c7c482501002501061985'
    output = device.delete(url)


.. sectionauthor:: Takashi Higashimura <tahigash@cisco.com>
