viptela/vManage
===============

The following services are supported by the REST connector for viptela/vManage.


connect
-------

API to connect to the device.

The vManage REST implementation supports specifying the port to connect to 
and allows to specify the username and password in the testbed YAML file.

.. code-block:: yaml

    # Example
    # -------
    #
    #   pyATS testbed yaml example for defining a REST connection

    testbed:
        name: myTestbed

    devices:
        vmanage:
            os: viptela
            type: vmanage
            custom:
                abstraction:
                    order: [os]
            connections:
                rest:
                    class: rest.connector.Rest
                    ip : "2.3.4.5"
                    port: 8443
                    verify: False
                    credentials:
                        rest:
                            username: admin
                            password: admin


If no port is specified, the default of `8443` is used. If verify is provided
and is False, it wont verify the SSL certificate.

.. csv-table:: GET arguments
    :header: Argument, Description, Default

    ``timeout``, Maximum time it can take to connect to the device. (optional), 30


get
---

API to send GET command to the device.

.. list-table:: GET arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - mount_point
      - API url string
      - | string
        | Required
    * - headers
      - Additional headers dictionary
      - | dict
        | Optional
    * - timeout
      - Maximum time it can take to disconnect to the device
      - | default 30 seconds
        | Optional


.. code-block:: python

    # Assuming the device is already connected
    mount_point = 'dataservice/device'
    output = device.get(mount_point=mount_point)

post
----

API to send POST command to the device.

.. list-table:: POST arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - mount_point
      - API url string
      - | string
        | Required
    * - payload
      - payload dictionary
      - | dict
        | Required
    * - headers
      - Additional headers dictionary
      - | dict
        | Optional
    * - timeout
      - Maximum time it can take to disconnect to the device
      - | default 30 seconds
        | Optional

.. code-block:: python

    # Assuming the device is already connected
    mount_point = "dataservice/template/feature/"
    payload = {"templateName":"cli-add-stp",
               "templateDescription":"cli-add-stp",
               "templateType":"cli-template",
               "deviceType":["vedge-ISR-4451-X"],
               "templateMinVersion":"15.0.0",
               "templateDefinition":{"config":{"vipObjectType":"object",
                                               "vipType":"constant",
                                               "vipValue":"spanning-tree mode rapid-pvst"}},
               "factoryDefault":false}

    device.rest.post(mount_point=mount_point,
                     payload=payload)


put
---

API to send PUT command to the device.

.. list-table:: PUT arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - mount_point
      - API url string
      - | string
        | Required
    * - payload
      - payload dictionary
      - | dict
        | Required
    * - headers
      - Additional headers dictionary
      - | dict
        | Optional
    * - timeout
      - Maximum time it can take to disconnect to the device
      - | default 30 seconds
        | Optional

.. code-block:: python

    # Assuming the device is already connected
    mount_point = "dataservice/template/feature/3e322401-c965-4394-b539-216e57020404"
    payload = {"templateName":"cli-add-stp",
               "templateDescription":"cli-add-stp",
               "templateType":"cli-template",
               "deviceType":["vedge-ISR-4451-X"],
               "templateMinVersion":"15.0.0",
               "templateDefinition":{"config":{"vipObjectType":"object",
                                               "vipType":"constant",
                                               "vipValue":"spanning-tree mode rapid-pvst"}},
                "factoryDefault":false}

    device.rest.put(mount_point=mount_point,
                    payload=payload)

delete
------

API to send DELETE command to the device.

.. list-table:: DELETE arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - mount_point
      - API url string
      - | string
        | Required
    * - headers
      - Additional headers dictionary
      - | dict
        | Optional
    * - timeout
      - Maximum time it can take to disconnect to the device
      - | default 30 seconds
        | Optional

.. code-block:: python

    # Assuming the device is already connected
    mount_point = "dataservice/device/unreachable/"
    device.rest.delete(mount_point=mount_point)


.. sectionauthor:: Vanda Wang <vanwang@cisco.com>
