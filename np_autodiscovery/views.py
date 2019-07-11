from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from utilities.views import ObjectDeleteView, ObjectEditView, ObjectListView

from np_autodiscovery import filters, forms, tables
from np_autodiscovery.models import DiscoveryRequest


#
# DiscoveryRequests
#

class DiscoveryRequestListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'np_autodiscovery.view_discoveryrequest'
    queryset = DiscoveryRequest.objects.all()
    filter = filters.DiscoveryRequestFilter
    filter_form = forms.DiscoveryRequestFilterForm
    table = tables.DiscoveryRequestTable
    template_name = 'np_autodiscovery/discoveryrequest_list.html'


class DiscoveryRequestView(PermissionRequiredMixin, View):
    permission_required = 'np_autodiscovery.view_discoveryrequest'

    def get(self, request, pk):

        discoveryrequest = get_object_or_404(DiscoveryRequest, pk=pk)

        return render(request, 'np_autodiscovery/discoveryrequest.html', {
            'discoveryrequest': discoveryrequest,
        })


class DiscoveryRequestCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'np_autodiscovery.add_discoveryrequest'
    model = DiscoveryRequest
    model_form = forms.DiscoveryRequestForm
    template_name = 'np_autodiscovery/discoveryrequest_edit.html'
    default_return_url = 'np_autodiscovery:discoveryrequest_list'


class DiscoveryRequestDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'np_autodiscovery.delete_discoveryrequest'
    model = DiscoveryRequest
    default_return_url = 'np_autodiscovery:discoveryrequest_list'