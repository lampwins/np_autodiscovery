import django_filters
import netaddr
from django.db.models import Q

from dcim.models import DeviceRole, Platform, Site

from np_autodiscovery.constants import REQUEST_STATUS_CHOICES
from np_autodiscovery.models import DiscoveryRequest


class DiscoveryRequestFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=REQUEST_STATUS_CHOICES,
        null_value=None
    )
    prefix = django_filters.CharFilter(
        method='filter_prefix',
        label='Prefix',
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform (ID)',
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Platform (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    device_role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
        label='Device role (ID)',
    )
    device_role = django_filters.ModelMultipleChoiceFilter(
        field_name='device_role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Device role (slug)',
    )

    class Meta:
        model = DiscoveryRequest
        fields = [
            'id', 'prefix', 'update_existing', 'status',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(prefix__icontains=value)
        )
        return queryset.filter(qs_filter)

    def filter_prefix(self, queryset, name, value):
        if not value.strip():
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(prefix=query)
        except ValidationError:
            return queryset.none()
