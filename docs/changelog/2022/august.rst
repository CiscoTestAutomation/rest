August 2022
==========

August 26 - Rest v22.8 
------------------------



+-------------------------------+-------------------------------+
| Module                        | Versions                      |
+===============================+===============================+
| ``rest.connector ``           | 22.8                          |
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

* nexus dashboard (nd)
    * Added content_type parameter to post and put api
    * Prevented an error from being raised if response does not contain a json,


