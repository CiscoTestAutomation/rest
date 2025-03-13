import json

TEST_PAYLOAD_DICT = {
    "Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile": [
        {
            "profile-name": "default-ap-profile",
            "description": "default ap profile",
            "hyperlocation": {
                "pak-rssi-threshold-detection": -50
            },
            "halo-ble-entries": {
                "halo-ble-entry": [
                    {
                        "beacon-id": 0
                    },
                    {
                        "beacon-id": 1
                    },
                    {
                        "beacon-id": 2
                    },
                    {
                        "beacon-id": 3
                    },
                    {
                        "beacon-id": 4
                    }
                ]
            }
        }
    ]
}

TEST_PAYLOAD_JSON = json.dumps(TEST_PAYLOAD_DICT)

TEST_PAYLOAD_XML = """<Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile>
  <description>default ap profile</description>
  <halo-ble-entries>
    <halo-ble-entry>
      <beacon-id>0</beacon-id>
    </halo-ble-entry>
    <halo-ble-entry>
      <beacon-id>1</beacon-id>
    </halo-ble-entry>
    <halo-ble-entry>
      <beacon-id>2</beacon-id>
    </halo-ble-entry>
    <halo-ble-entry>
      <beacon-id>3</beacon-id>
    </halo-ble-entry>
    <halo-ble-entry>
      <beacon-id>4</beacon-id>
    </halo-ble-entry>
  </halo-ble-entries>
  <hyperlocation>
    <pak-rssi-threshold-detection>-50</pak-rssi-threshold-detection>
  </hyperlocation>
  <profile-name>default-ap-profile</profile-name>
</Cisco-IOS-XE-wireless-site-cfg:ap-cfg-profile>"""