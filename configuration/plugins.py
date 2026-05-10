# Add your plugins and plugin settings here.
# Of course uncomment this file out.

# To learn how to build images with your required plugins
# See https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins

PLUGINS = [
    'netbox_topology_views',
    'netbox_diode_plugin',
]

PLUGINS_CONFIG = {
    'netbox_topology_views': {
        'allow_coordinates_saving': True,
        'always_save_coordinates': True,
    },
    "netbox_diode_plugin": {
        # Diode gRPC target for communication with Diode server
        "diode_target_override": "grpc://10.0.1.63:8080/diode",
        # NetBox username associated with changes applied via plugin
        "diode_username": "diode",
        # netbox-to-diode client secret
        "netbox_to_diode_client_secret": "bSEW2pcisC11IiQpbaI96Qs8CunziLDgCIttD3Zgs=",
    },
}
