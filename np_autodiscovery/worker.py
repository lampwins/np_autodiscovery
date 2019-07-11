import jnpr
import napalm
import netaddr
import socket
from contextlib import closing
from django_rq import job
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from napalm.base.exceptions import (
    ConnectAuthError, ConnectionClosedException, ConnectionException, ConnectTimeoutError, ModuleImportError
)

from dcim.models import Device, DeviceType, Manufacturer

from np_autodiscovery.constants import *
from np_autodiscovery.models import DiscoveryResult


def _get_or_create_device_type(model, manufacturer, vendor):
    device_type = DeviceType.objects.filter(model__iexact=model).first()
    if not device_type:
        # Create a new device type

        # Create a new manufacture if one does not already exist
        if not manufacturer:
            manufacturer = Manufacturer.objects.filter(name__iexact=vendor).first()
            if not manufacturer:
                manufacturer = Manufacturer.objects.create(name=vendor)

        device_type = DeviceType.objects.create(model=model, manufacturer=manufacturer)

    return device_type


@job('default')
def discovery_job(discovery_request):
    """
    Given a DiscoveryRequest object, scan the prefix for devices and take the specified action
    """
    discovery_request.status = REQUEST_STATUS_RUNNING
    discovery_request.save()

    # Validate the configured driver
    try:
        driver = napalm.get_network_driver(discovery_request.platform.napalm_driver)
    except ModuleImportError:
        # No driver is defined on the platform or the driver is invalid
        discovery_request.status = REQUEST_STATUS_FAILED
        discovery_request.save()
        raise ImproperlyConfigured(
            'Platform {} does not have a napalm driver defined or has an invalid driver defined'.format(
                discovery_request.platform
            )
        )

    # Iterate over the prefix
    for address in discovery_request.prefix.iter_hosts():
        discovery_result = DiscoveryResult.objects.create(
            address=address,
            discovery_request=discovery_request
        )

        ip_address = str(address)
        optional_args = settings.NAPALM_ARGS.copy()
        if discovery_request.platform.napalm_args is not None:
            optional_args.update(discovery_request.platform.napalm_args)
        d = driver(
            hostname=ip_address,
            username=settings.NAPALM_USERNAME,
            password=settings.NAPALM_PASSWORD,
            timeout=settings.NAPALM_TIMEOUT,
            optional_args=optional_args
        )

        # Try to connect to the address
        try:
            # Simple open port check first if the port attribute is accessible
            if hasattr(d, 'port'):
                with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                    sock.settimeout(4)
                    if sock.connect_ex((ip_address, int(d.port))):
                        raise ConnectionException("Port {} not open".format(d.port))

            # Now open the actual connection
            d.open()
        except ConnectAuthError:
            # Login failed
            discovery_result.status = RESULT_STATUS_FAILED_LOGIN
        except jnpr.junos.exception.ConnectError:
            # Connection error
            discovery_result.status = RESULT_STATUS_FAILED_CONNECTION_ERROR
        except (ConnectionException, ConnectTimeoutError, jnpr.junos.exception.ConnectTimeoutError):
            # Unreachable
            discovery_result.status = RESULT_STATUS_UNREACHABLE
        except (ConnectionClosedException, jnpr.junos.exception.ConnectRefusedError):
            # Connection closed
            discovery_result.status = RESULT_STATUS_FAILED_CONNECTION_CLOSED
        except Exception as e:
            # Some other failure
            discovery_result.status = RESULT_STATUS_FAILED
        else:

            # Connection open, now try to get facts
            try:
                device_facts = d.get_facts()
                device_environmental = d.get_environment()
                device_interfaces = d.get_interfaces()
            except Exception:
                # Parse error
                discovery_result.status = RESULT_STATUS_FAILED_PARSING
            else:
                # Everything went well, so now we do something with the results
                d.close()

                device = Device.objects.filter(name=device_facts['hostname'], site=discovery_request.site).first()
                if device:
                    if discovery_request.update_existing:
                        # update
                        discovery_result.status = RESULT_STATUS_COMPLETED_UPDATED_DEVICE

                        device_type = _get_or_create_device_type(
                            device_facts['model'],
                            discovery_request.platform.manufacturer,
                            device_facts['vendor']
                        )

                        device.device_type = device_type
                        device.serial = device_facts['serial_number']
                        device.platform = discovery_request.platform
                        device.device_role = discovery_request.device_role
                        device.save()
                    else:
                        # no update
                        discovery_result.status = RESULT_STATUS_COMPLETED_NO_UPDATED_DEVICE
                else:
                    # new device
                    discovery_result.status = RESULT_STATUS_COMPLETED_NEW_DEVICE

                    device_type = _get_or_create_device_type(
                        device_facts['model'],
                        discovery_request.platform.manufacturer,
                        device_facts['vendor']
                    )

                    device = Device.objects.create(
                        name=device_facts['hostname'],
                        device_type=device_type,
                        serial=device_facts['serial_number'],
                        site=discovery_request.site,
                        platform=discovery_request.platform,
                        device_role=discovery_request.device_role
                    )

                discovery_result.device = device

        discovery_result.save()

    discovery_request.status = REQUEST_STATUS_COMPLETE
    discovery_request.save()
    return True
