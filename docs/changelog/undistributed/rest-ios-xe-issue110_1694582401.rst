--------------------------------------------------------------------------------
                                Fix
--------------------------------------------------------------------------------
* rest
     * Updated IOSXE Implimentation
        * Changed "connect" method:
          * Send a GET request to a common "well-known" IOS-XE YANG model (path: /Cisco-IOS-XE-native:native/version)
          * Debug output to include the received data from the device
          * Content-Type header is not used (default_content_type parameter)