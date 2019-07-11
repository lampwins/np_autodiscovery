from django.apps import AppConfig


class NPAutoDiscoveryConfig(AppConfig):
    name = 'np_autodiscovery'
    verbose_name = 'Auto Discovery'
    netbox_min_version = '2.6.0'
    netbox_max_version = '2.7.0'
    required_configuration_settings = []
    default_configuration_settings = {}
    nav_links = [
        {
            'primary': {
                'name': 'Discovery Requests',
                'view': 'discoveryrequest_list',
                'permission': 'view_discoveryrequest'
            },
            'add': {
                'view': 'discoveryrequest_add',
                'permission': 'add_discoveryrequest'
            },
            #'import': {
            #    'view': 'hello_world',
            #}
        }
    ]
