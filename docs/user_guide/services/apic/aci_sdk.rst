APIC SDK
=========

The following services are supported by the SDK (Cobra) connector for APIC.


query
-----

Mimics same-name function from MoDirectory class (cobra.mit.access)

.. list-table:: QUERY arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - queryObject (obj)
      - A query object
      - Mandatory

For more information please visit the `Cisco APIC Python API <https://cobra.readthedocs.io/en/stable/api-ref/access.html?highlight=query#cobra.mit.access.MoDirectory.query>`_

commit
------

Mimics same-name function from MoDirectory class (cobra.mit.access)

.. list-table:: COMMIT arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - configObject (obj)
      - The configuration request to commit
      - Mandatory

For more information please visit the `Cisco APIC Python API <https://cobra.readthedocs.io/en/stable/api-ref/access.html?highlight=commit#cobra.mit.access.MoDirectory.commit>`_

lookupByDn
----------

Mimics same-name function from MoDirectory class (cobra.mit.access)

.. list-table:: LOOKUPBYDN arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - dnStrOrDn (obj|str)
      - DN of the object to lookup
      - Mandatory
    * - queryParams (dict)
      - Dictionary containing additional filters
      - Optional

For more information please visit the `Cisco APIC Python API <https://cobra.readthedocs.io/en/stable/api-ref/access.html?highlight=lookupByDn#cobra.mit.access.MoDirectory.lookupByDn>`_

lookupByClass
-------------

Mimics same-name function from MoDirectory class (cobra.mit.access)

.. list-table:: LOOKUPBYCLASS arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - classNames (str|list)
      - Class name or list of classes
      - Mandatory
    * - parentDn (obj|str)
      - DN of the parent object
      - None
    * - kwargs (dict)
      - Dictionary containing additional filters
      - Optional

For more information please visit the `Cisco APIC Python API <https://cobra.readthedocs.io/en/stable/api-ref/access.html?highlight=lookupByClass#cobra.mit.access.MoDirectory.lookupByClass>`_

exists
------

Mimics same-name function from MoDirectory class (cobra.mit.access)

.. list-table:: EXISTS arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - dnStrOrDn (obj|str)
      - DN of the object to check
      - Mandatory

get_model
---------

Automatically import the required library and return the model class

.. list-table:: GET_MODEL arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - model (str)
      - Unique identifier of the module and class (eg. fv.Tenant)
      - Mandatory

.. code-block:: python

    # Assuming the device is already connected
    tenant_class = device.cobra.get_model(model='fv.Tenant')

create
------

Automatically import the required library and instantiate the model object

.. list-table:: CREATE arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - model (str)
      - Unique identifier of the module and class (eg. "fv.Tenant")
      - Mandatory
    * - parent_mo_or_dn (obj|str)
      - The parent MO or DN
      - Mandatory
    * - extra_parms (dict)
      - Dictionary containing additional attributes for the object
      - Optional

.. code-block:: python

    # Assuming the device is already connected
    tenant = device.cobra.create(model='fv.Tenant',
                                 parent_mo_or_dn='uni',
                                 name='test')

config_and_commit
-----------------

Add MO to ConfigRequest and push it to device

.. list-table:: CONFIG_AND_COMMIT arguments
    :widths: 30 50 20
    :header-rows: 1

    * - Argument
      - Description
      - Default
    * - mo (obj)
      - Object to be committed
      - Mandatory
    * - expected_status_code (int)
      - Expected result
      - 200

.. code-block:: python

    # Assuming the device is already connected
    # and tenant object is created (create function)
    tenant = device.cobra.config_and_commit(mo=tenant)


Additional info on the Cobra SDK can be found on the `Cisco APIC Python API <https://cobra.readthedocs.io/en/stable/index.html>`_


.. sectionauthor:: Romel Tolos <rtolos@cisco.com>
