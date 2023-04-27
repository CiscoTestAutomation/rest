--------------------------------------------------------------------------------
                                      Fix
--------------------------------------------------------------------------------

* All connectors (except xpresso)
    * Change implementation of ip/host address to remove default .exploded
      method. If an ipaddress object is passed, .exploded will still be used,
      otherwise use the raw IP data. This enables dynamic testbed creation
      using string values for IP addresses.
