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
        fields = ['component_type', 'model',
                  'serial_number', 'catalog_number', 'actions']
        order_by = 'component_type'
        empty_text = 'Brak podzespołów'


class CommissionTable(tables.Table):
    pk = tables.Column(
        attrs={'th': {'width': '10%'}},
        empty_values=(),
        verbose_name="Numer zlecenia")
    vc_name = tables.Column(
        attrs={'th': {'width': '19%'}},
        empty_values=(),
        verbose_name="Pojazd/podzespół")
    contractor = tables.Column(
        attrs={'th': {'width': '17%'}})
    phone = tables.TemplateColumn(
        attrs={'th': {'width': '10%'}},
        empty_values=(),
        accessor='contractor',
        template_name='commission/commission/phone_table_field.html',
        verbose_name="Telefon")
    start_date = tables.Column(
        attrs={'th': {'width': '12%'}},
        verbose_name="Data przyjęcia")
    end_date = tables.Column(
        attrs={'th': {'width': '12%'}},
        verbose_name="Data zamknięcia")
    value = tables.Column(
        attrs={'th': {'width': '13%'}},
        empty_values=(),
        verbose_name="Cena")
    actions = tables.TemplateColumn(
        attrs={'th': {'width': '7%'}},
        verbose_name="Akcje",
        template_name='commission/commission/table_actions.html',
        orderable=False,
        exclude_from_export=True)

    def render_value(self, value):
        return "{0:.2f} zł".format(value or 0).replace('.', ',')

    def order_value(self, queryset, is_descending):
        queryset = queryset.order_by_total(is_descending)
        return (queryset, True)

    def order_phone(self, queryset, is_descending):
        queryset = queryset.order_by(
            ('-' if is_descending else '') + 'contractor__phone_1',
            ('-' if is_descending else '') + 'contractor__phone_2')
        return (queryset, True)

    class Meta:
        model = Commission
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['pk', 'vc_name', 'contractor',
                  'phone', 'start_date', 'end_date', 'value']
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
    price = tables.Column(
        attrs={'th': {'width': '20%'}})

    def render_price(self, value):
        return "{0:.2f} zł".format(value).replace('.', ',')

    class Meta:
        model = CommissionItem
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['name', 'description', 'ware', 'quantity', 'price']
        empty_text = 'Brak pozycji'
