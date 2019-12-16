import datetime

from django.test import TestCase

from apps.warehouse.models import Ware, Supplier, Invoice, InvoiceItem


class WareModelTest(TestCase):
    def setUp(self):
        self.ware = Ware.objects.create(
            index='K 1111A',
            name='Cabin filter')

    def test_object_name(self):
        self.assertEquals(self.ware.index, str(self.ware))

    def test_last_price(self):
        self.assertEquals(self.ware.last_price, None)

    def test_index_slug(self):
        self.assertEquals(self.ware.index_slug, 'k1111a')

    def test_stock_default(self):
        self.assertEquals(self.ware.stock, 0)


class SupplierModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name='The Supplier')

    def test_object_name(self):
        self.assertEquals(self.supplier.name, str(self.supplier))

    def test_all_invoices_value(self):
        self.assertEquals(self.supplier.all_invoices_value, None)


class InvoiceModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name='The Supplier')
        self.invoice = Invoice.objects.create(
            date=datetime.date.today(),
            number='F123/2019',
            supplier=self.supplier)

    def test_object_name(self):
        expected_name = '{}: {}'.format(str(self.invoice.supplier), self.invoice.number)
        self.assertEquals(expected_name, str(self.invoice))

    def test_total_value(self):
        self.assertEquals(self.invoice.total_value, None)
