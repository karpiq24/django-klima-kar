from django.views.generic import ListView

from apps.warehouse.models import Ware


class WareListView(ListView):
    model = Ware
