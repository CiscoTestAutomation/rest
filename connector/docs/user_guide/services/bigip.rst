BigIP
=====

The following services are supported by the REST connector for F5 (BigIP).


connect
-------

API to connect to the device.

The BigIP REST implementation supports specifying the port to connect to
and allows to specify the username and password in the testbed YAML file.
Under the hood its using token authentication to communicate with BigIP.

.. code-block:: yaml

    # Example
    # -------
    #
    #   pyATS testbed yaml example for defining a REST connection

    testbed:
        name: myTestbed

    devices:
    bigip01.lab.local:
        alias: 'bigip01'
        type: 'bigip'
        os: 'bigip'
        custom:
        abstraction:
            order: [os]
        connections:
        rest:
            class: rest.connector.Rest
            ip: 1.2.3.4
            port: 443
            protocol: http
            credentials:
            rest:
                username: admin
                password: admin


If no port is specified, the default of `443` is used.
If verify is provided and is True, it will verify the SSL certificate.
If protocol is not provided, the default is `http`.


.. code-block:: python

    device = testbed.devices['bigip01']
    device.connect(alias='rest', via='rest')
    device.rest.connected


disconnect
----------

Will delete the current API Token in use.


get
---

API to GET from the device.

.. csv-table:: GET arguments
    :header: Argument, Description, Default

    ``api_url``,  API url string (required),
    ``timeout``, timeout in seconds (optional), 30

.. code-block:: python

    url = '/mgmt/tm/ltm/node'
    nodes = device.rest.get(url)


POST
---

API to POST data to the device.

.. csv-table:: POST arguments
    :header: Argument, Description, Default

    ``api_url``,  API url string (required),
    ``payload``,  Payload to be sent (required),
    ``timeout``, timeout in seconds (optional), 30

.. code-block:: python

    url = '/mgmt/tm/ltm/node/'
    data = {"name":"wa12","partition":"Common","address":"119.119.192.193"}
    node = device.rest.post(url, data)

    url = '/mgmt/tm/ltm/node/'
    data = {"name":"wa13","partition":"Common","address":"119.119.192.195"}
    node = device.rest.post(url, data)

    url = '/mgmt/tm/ltm/pool/'
    data = {"name":"wa12","partition":"Common","members":"wa12:80"}
    pool = device.rest.post(url, data)


PATCH
---

API to PATCH data on the device.

.. csv-table:: PATCH arguments
    :header: Argument, Description, Default

    ``api_url``,  API url string (required),
    ``payload``,  Payload to be sent (required),
    ``timeout``, timeout in seconds (optional), 30

.. code-block:: python

    url = '/mgmt/tm/ltm/node/~Common~wa12'
    data = {"session":"user-disabled"}
    node = device.rest.patch(url, data)


PUT
---

API to PUT data on the device.

.. csv-table:: PUT arguments
    :header: Argument, Description, Default

    ``api_url``,  API url string (required),
    ``payload``,  Payload to be sent (required),
    ``timeout``, timeout in seconds (optional), 30

.. code-block:: python

    url = '/mgmt/tm/ltm/pool/wa12'
    data = {"members":"wa13:80"}
    pool = device.rest.put(url, data)


DELETE
---

API to DELETE data on the device.

.. csv-table:: DELETE arguments
    :header: Argument, Description, Default

    ``api_url``,  API url string (required),
    ``timeout``, timeout in seconds (optional), 30

.. code-block:: python

    url = '/mgmt/tm/ltm/node/wa12'
    node = device.rest.delete(url)

    url = '/mgmt/tm/ltm/pool/wa12'
    pool = device.rest.delete(url)

    url = '/mgmt/tm/ltm/node/wa13'
    node = device.rest.delete(url)

.. sectionauthor:: Mirza Waqas Ahmed <m.w.ahmed@gmail.com>

