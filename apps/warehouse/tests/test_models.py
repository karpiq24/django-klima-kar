from django.test import TestCase

from datetime import date, timedelta

from apps.warehouse.models import Ware, Supplier, Invoice, InvoiceItem, WarePriceChange


class WareModelTest(TestCase):
    def setUp(self):
        self.ware = Ware.objects.create(index="K 1111A", name="Cabin filter")

    def test_object_name(self):
        self.assertEquals(self.ware.index, str(self.ware))

    def test_last_price(self):
        self.assertEquals(self.ware.last_price, None)

    def test_index_slug(self):
        self.assertEquals(self.ware.index_slug, "k1111a")

    def test_stock_default(self):
        self.assertEquals(self.ware.stock, 0)


class SupplierModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name="The Supplier")

    def test_object_name(self):
        self.assertEquals(self.supplier.name, str(self.supplier))

    def test_all_invoices_value(self):
        self.assertEquals(self.supplier.all_invoices_value, 0)


class InvoiceModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name="The Supplier")
        self.ware = Ware.objects.create(index="K 1111A", name="Cabin filter")
        self.invoice = Invoice.objects.create(
            date=date.today() - timedelta(days=1),
            number="F123/2019",
            supplier=self.supplier,
        )
        InvoiceItem.objects.create(
            invoice=self.invoice, ware=self.ware, quantity=2, price=20
        )
        self.invoice2 = Invoice.objects.create(
            date=date.today(), number="F124/2019", supplier=self.supplier
        )
        InvoiceItem.objects.create(
            invoice=self.invoice2, ware=self.ware, quantity=1, price=5
        )
        self.invoice2.check_ware_price_changes()

    def test_object_name(self):
        expected_name = "{}: {}".format(str(self.invoice.supplier), self.invoice.number)
        self.assertEquals(expected_name, str(self.invoice))

    def test_total_value(self):
        self.assertEquals(self.invoice.total_value, 40)
        self.assertEquals(self.invoice2.total_value, 5)

    def test_supplier_all_invoices_value(self):
        self.assertEquals(self.supplier.all_invoices_value, 45)

    def test_last_price(self):
        self.assertEquals(self.ware.last_price, 5)

    def test_ware_price_change(self):
        change = WarePriceChange.objects.first()
        self.assertIsNotNone(change)
        self.assertEquals(change.ware, self.ware)
        self.assertEquals(change.last_price, 20)
        self.assertEquals(change.new_price, 5)
        self.assertEquals(change.is_discount, True)
        self.assertEquals(change.percent_change(absolute=False), -75)
        self.assertEquals(change.percent_change(absolute=True), 75)
