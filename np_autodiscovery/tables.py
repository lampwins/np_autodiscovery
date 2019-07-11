import django_tables2 as tables

from utilities.tables import BaseTable, BooleanColumn

from np_autodiscovery.models import DiscoveryRequest


STATUS_LABEL = """
<span class="label label-{{ record.get_status_class }}">{{ record.get_status_display }}</span>
"""


class DiscoveryRequestTable(BaseTable):
    prefix = tables.LinkColumn()
    update_existing = BooleanColumn()
    status = tables.TemplateColumn(template_code=STATUS_LABEL, verbose_name='Status')

    class Meta(BaseTable.Meta):
        model = DiscoveryRequest
        fields = ['prefix', 'created', 'update_existing', 'platform', 'status', 'site', 'device_role']
