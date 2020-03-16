from haystack import indexes

from apps.warehouse.models import Ware, Invoice, Supplier
from apps.invoicing.models import Contractor, SaleInvoice
from apps.commission.models import Vehicle, Component, Commission


class SearchIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    boost = 1
    model = None
    haystack_use_for_indexing = False

    def get_model(self):
        return self.model

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    def prepare(self, obj):
        data = super().prepare(obj)
        data["boost"] = self.boost
        return data


class SupplierIndex(SearchIndex):
    haystack_use_for_indexing = True
    model = Supplier
    boost = 5


class WareIndex(SearchIndex):
    haystack_use_for_indexing = True
    model = Ware
    boost = 5


class PurchaseInvoiceIndex(SearchIndex):
    haystack_use_for_indexing = True
    model = Invoice


class ContractorIndex(SearchIndex):
    haystack_use_for_indexing = True
    model = Contractor
    boost = 5


class SaleInvoiceIndex(SearchIndex):
    haystack_use_for_indexing = True
    model = SaleInvoice


class VehicleIndex(SearchIndex):
    haystack_use_for_indexing = True
    model = Vehicle
    boost = 5


class ComponentIndex(SearchIndex):
    haystack_use_for_indexing = True
    model = Component
    boost = 5


class CommissionIndex(SearchIndex):
    haystack_use_for_indexing = True
    model = Commission
