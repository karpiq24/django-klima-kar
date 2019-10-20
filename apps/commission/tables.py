import django_tables2 as tables

from apps.commission.models import Vehicle, Component, Commission, CommissionItem


class VehicleTable(tables.Table):
    brand = tables.Column(
        attrs={'th': {'width': '24%'}})
    model = tables.Column(
        attrs={'th': {'width': '23%'}})
    registration_plate = tables.Column(
        attrs={'th': {'width': '23%'}})
    vin = tables.Column(
        attrs={'th': {'width': '23%'}})
    actions = tables.TemplateColumn(
        attrs={'th': {'width': '7%'}},
        verbose_name="Akcje",
        template_name='commission/vehicle/table_actions.html',
        orderable=False,
        exclude_from_export=True)

    class Meta:
        model = Vehicle
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['brand', 'model', 'registration_plate', 'vin', 'actions']
        order_by = 'brand'
        empty_text = 'Brak pojazdów'


class ComponentTable(tables.Table):
    component_type = tables.Column(
        attrs={'th': {'width': '24%'}})
    model = tables.Column(
        attrs={'th': {'width': '23%'}})
    serial_number = tables.Column(
        attrs={'th': {'width': '23%'}})
    catalog_number = tables.Column(
        attrs={'th': {'width': '23%'}})
    actions = tables.TemplateColumn(
        attrs={'th': {'width': '7%'}},
        verbose_name="Akcje",
        template_name='commission/component/table_actions.html',
        orderable=False,
        exclude_from_export=True)

    class Meta:
        model = Component
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['component_type', 'model', 'serial_number', 'catalog_number', 'actions']
        order_by = 'component_type'
        empty_text = 'Brak podzespołów'


class CommissionTable(tables.Table):
    pk = tables.Column(
        attrs={'th': {'width': '10%'}},
        empty_values=(),
        verbose_name="Numer zlecenia")
    vc_name = tables.Column(
        attrs={'th': {'width': '24%'}},
        empty_values=(),
        verbose_name="Pojazd/podzespół")
    contractor = tables.Column(
        attrs={'th': {'width': '24%'}})
    start_date = tables.Column(
        attrs={'th': {'width': '15%'}},
        verbose_name="Data wystawienia")
    value_netto = tables.Column(
        attrs={'th': {'width': '20%'}},
        verbose_name="Łączna wartość netto")
    actions = tables.TemplateColumn(
        attrs={'th': {'width': '7%'}},
        verbose_name="Akcje",
        template_name='commission/commission/table_actions.html',
        orderable=False,
        exclude_from_export=True)

    def render_value_netto(self, value):
        return "{0:.2f} zł".format(value).replace('.', ',')

    class Meta:
        model = Commission
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['pk', 'vc_name', 'contractor', 'start_date', 'value_netto']
        order_by = '-pk'
        empty_text = 'Brak zleceń'


class CommissionItemTable(tables.Table):
    name = tables.Column(
        attrs={'th': {'width': '20%'}})
    description = tables.Column(
        attrs={'th': {'width': '20%'}})
    ware = tables.Column(
        attrs={'th': {'width': '10%'}})
    quantity = tables.Column(
        attrs={'th': {'width': '10%'}})
    price_netto = tables.Column(
        attrs={'th': {'width': '20%'}})
    price_brutto = tables.Column(
        attrs={'th': {'width': '20%'}})

    def render_price_netto(self, value):
        return "{0:.2f} zł".format(value).replace('.', ',')

    def render_price_brutto(self, value):
        return "{0:.2f} zł".format(value).replace('.', ',')

    class Meta:
        model = CommissionItem
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['name', 'description', 'ware', 'quantity', 'price_netto', 'price_brutto']
        empty_text = 'Brak pozycji'
