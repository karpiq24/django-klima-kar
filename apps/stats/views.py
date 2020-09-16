import requests

from datetime import date, timedelta, datetime
from decimal import Decimal

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser

from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Sum, Avg, Count, F, FloatField
from django.template.defaultfilters import date as _date

from KlimaKar.mixins import StaffOnlyMixin
from KlimaKar.templatetags.slugify import slugify
from apps.settings.models import InvoiceDownloadSettings
from apps.warehouse.models import Invoice, Ware, WarePriceChange, Supplier
from apps.invoicing.models import SaleInvoice, Contractor, RefrigerantWeights
from apps.commission.models import Commission
from apps.stats.models import ReceiptPTU, Round
from apps.stats.mixins import ChartDataMixin, BigChartHistoryMixin
from apps.stats.dictionaries import COLORS


class DashboardView(TemplateView):
    template_name = "stats/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["stats"] = {
            "purchase": {
                "group": "purchase",
                "metrics": self._get_purchase_metrics(),
                "charts": self._get_purchase_charts(),
            },
            "sale": {
                "group": "sale",
                "metrics": self._get_sale_metrics(),
                "charts": self._get_sale_charts(),
            },
        }
        return context

    def _get_purchase_charts(self):
        charts = []
        if self.request.user.is_staff:
            charts.append(
                {
                    "title": "Historia faktur zakupowych",
                    "url": reverse("stats:purchase_invoices_history"),
                    "big": True,
                    "select_date": {"extra": True},
                    "custom_select": [
                        ("Sum", "Suma"),
                        ("Avg", "Średnia"),
                        ("Count", "Ilość"),
                    ],
                }
            )
            charts.append(
                {
                    "title": "Historia zakupów u dostawców",
                    "select_date": True,
                    "custom_select": [
                        ("Sum", "Suma"),
                        ("Avg", "Średnia"),
                        ("Count", "Ilość"),
                    ],
                    "url": reverse("stats:supplier_purchase_history"),
                }
            )
        charts.append(
            {
                "title": "Historia zakupów towarów",
                "select_date": True,
                "custom_select": [("Count", "Ilość"), ("Sum", "Suma")],
                "url": reverse("stats:ware_purchase_history"),
            }
        )
        return charts

    def _get_purchase_metrics(self):
        metrics = []
        metrics.append(
            {
                "icon": "fa-tags",
                "color": "#E21E00",
                "title": "Liczba dodanych towarów",
                "class": "ware_count",
            }
        )
        metrics.append(
            {
                "icon": "fa-truck",
                "color": "#C1456E",
                "title": "Liczba dodanych dostawców",
                "class": "supplier_count",
            }
        )
        metrics.append(
            {
                "icon": "fa-file-alt",
                "color": "#8355C5",
                "title": "Liczba dodanych faktur",
                "class": "invoice_count",
            }
        )
        if self.request.user.is_staff:
            metrics.append(
                {
                    "icon": "fa-file-alt",
                    "color": "#8355C5",
                    "title": "Kwota netto dodanych faktur",
                    "class": "invoice_sum",
                }
            )
        return metrics

    def _get_sale_charts(self):
        charts = []
        if self.request.user.is_staff:
            charts.append(
                {
                    "title": "Historia faktur sprzedażowych",
                    "url": reverse("stats:sale_invoices_history"),
                    "big": True,
                    "select_date": {"extra": True},
                    "custom_select": [
                        ("SumNetto", "Suma netto"),
                        ("SumBrutto", "Suma brutto"),
                        ("AvgNetto", "Średnia netto"),
                        ("AvgBrutto", "Średnia brutto"),
                        ("Count", "Ilość"),
                    ],
                }
            )
            charts.append(
                {
                    "title": "Historia zleceń",
                    "url": reverse("stats:commission_history"),
                    "big": True,
                    "select_date": {"extra": True},
                    "custom_select": [
                        ("Sum", "Suma"),
                        ("Avg", "Średnia"),
                        ("Count", "Ilość"),
                    ],
                }
            )
        charts.append(
            {
                "title": "Historia sprzedaży czynników",
                "url": reverse("stats:refrigerant_history"),
                "big": True,
                "select_date": {"extra": True},
                "custom_select": [
                    ("r134a", "R134a"),
                    ("r1234yf", "R1234yf"),
                    ("r12", "R12"),
                    ("r404", "R404"),
                ],
            }
        )
        return charts

    def _get_sale_metrics(self):
        metrics = []
        metrics.append(
            {
                "icon": "fa-book",
                "color": "#89D23A",
                "title": "Liczba dodanych faktur",
                "class": "sale_invoice_count",
            }
        )
        if self.request.user.is_staff:
            metrics.append(
                {
                    "icon": "fa-book",
                    "color": "#89D23A",
                    "title": "Kwota netto dodanych faktur",
                    "class": "sale_invoice_sum",
                }
            )
            metrics.append(
                {
                    "icon": "fa-book",
                    "color": "#89D23A",
                    "title": "Kwota brutto dodanych faktur",
                    "class": "sale_invoice_sum_brutto",
                }
            )
            metrics.append(
                {
                    "icon": "fa-percentage",
                    "color": "#E21E00",
                    "title": "Podatek VAT",
                    "class": "vat_sum",
                }
            )
            metrics.append(
                {
                    "icon": "fa-percentage",
                    "color": "#E21E00",
                    "title": "Podatek VAT od firm",
                    "class": "company_vat_sum",
                }
            )
            metrics.append(
                {
                    "icon": "fa-percentage",
                    "color": "#E21E00",
                    "title": "Podatek VAT od osób fizycznych",
                    "class": "person_vat_sum",
                }
            )
            metrics.append(
                {
                    "icon": "fa-hand-holding-usd",
                    "color": "#E21E00",
                    "title": "Kwota PTU",
                    "class": "ptu_sum",
                }
            )

        metrics.append(
            {
                "icon": "fa-tasks",
                "color": "#427BD2",
                "title": "Liczba zakończonych zleceń",
                "class": "commission_count",
            }
        )
        if self.request.user.is_staff:
            metrics.append(
                {
                    "icon": "fa-tasks",
                    "color": "#427BD2",
                    "title": "Kwota zakończonych zleceń",
                    "class": "commission_sum",
                }
            )

        metrics.append(
            {
                "icon": "fa-users",
                "color": "#00A0DF",
                "title": "Liczba dodanych kontrahentów",
                "class": "contractor_count",
            }
        )
        metrics.append(
            {
                "icon": "fa-flask",
                "color": "#F8640B",
                "title": "Sprzedaż czynnika R134a",
                "class": "r134a_sum",
            }
        )
        metrics.append(
            {
                "icon": "fa-flask",
                "color": "#F8640B",
                "title": "Sprzedaż czynnika R1234yf",
                "class": "r1234yf_sum",
            }
        )
        metrics.append(
            {
                "icon": "fa-flask",
                "color": "#F8640B",
                "title": "Sprzedaż czynnika R12",
                "class": "r12_sum",
            }
        )
        metrics.append(
            {
                "icon": "fa-flask",
                "color": "#F8640B",
                "title": "Sprzedaż czynnika R404",
                "class": "r404_sum",
            }
        )
        return metrics


class SupplierPurchaseHistory(StaffOnlyMixin, ChartDataMixin, View):
    max_positions = 8

    def get(self, *args, **kwargs):
        self.date_option = self.request.GET.get("date_select", "week")
        self.metric = self.request.GET.get("custom_select", "Sum")

        self.invoices = self.get_invoices()
        self.response_data = self.get_response_data_template(
            chart_type="doughnut", values_appendix=" zł"
        )
        self.invoices = self.invoices.values("supplier")
        self.invoices = self._annotate(self.invoices)
        self.invoices = self.invoices.values_list("supplier__name", "total").order_by(
            "-total"
        )
        if self.invoices.count() > self.max_positions:
            index = self.max_positions - 1
        else:
            index = self.invoices.count()

        labels = list(self.invoices[0:index].values_list("supplier__name", flat=True))
        values = list(self.invoices[0:index].values_list("total", flat=True))

        if self.invoices.count() > self.max_positions:
            labels.append("Pozostali dostawcy")
            if self.metric == "Avg":
                values.append(
                    self.invoices[self.max_positions - 1 :]
                    .values("total")
                    .aggregate(avg=Round(Avg("total")))["avg"]
                )
            else:
                values.append(
                    self.invoices[self.max_positions - 1 :]
                    .values("total")
                    .aggregate(Sum("total"))["total__sum"]
                )

        self.response_data["data"]["labels"] = labels
        self.response_data["data"]["datasets"].append(
            self.get_dataset(values, COLORS[: len(values)])
        )

        return JsonResponse(self.response_data)

    def get_invoices(self):
        invoices = Invoice.objects.all()
        if self.date_option == "week":
            date = datetime.today() - relativedelta(days=6)
        elif self.date_option == "month":
            date = datetime.today() - relativedelta(months=1)
        elif self.date_option == "year":
            date = (datetime.today() - relativedelta(years=1, months=-1)).replace(day=1)
        else:
            date = None
        if date:
            invoices = invoices.filter(date__gte=date)
        return invoices

    def _annotate(self, qs):
        if self.metric == "Sum":
            return self.invoices.annotate(
                total=Sum(F("invoiceitem__price") * F("invoiceitem__quantity"))
            )
        if self.metric == "Avg":
            return self.invoices.annotate(
                total=Round(F("invoiceitem__price") * F("invoiceitem__quantity"))
            )
        elif self.metric == "Count":
            self.response_data["custom"]["values_appendix"] = ""
            return self.invoices.annotate(total=Count("id"))


class WarePurchaseHistory(ChartDataMixin, View):
    max_positions = 8

    def get(self, *args, **kwargs):
        date_option = self.request.GET.get("date_select", "week")
        metric = self.request.GET.get("custom_select", "Count")
        now = datetime.today()
        if date_option == "week":
            date = now - relativedelta(days=6)
        elif date_option == "month":
            date = now - relativedelta(months=1)
        elif date_option == "year":
            date = (now - relativedelta(years=1, months=-1)).replace(day=1)
        else:
            date = None

        response_data = self.get_response_data_template(
            chart_type="doughnut", values_appendix=" zł"
        )
        wares = Ware.objects.exclude(invoiceitem=None)
        if date:
            wares = wares.filter(invoiceitem__invoice__date__gte=date)

        if metric == "Sum":
            wares = wares.annotate(
                total=Sum(
                    F("invoiceitem__quantity") * F("invoiceitem__price"),
                    output_field=FloatField(),
                )
            )
        elif metric == "Count":
            wares = wares.annotate(total=Sum("invoiceitem__quantity"))
            response_data["custom"]["values_appendix"] = ""
        wares = wares.values_list("index", "total").order_by("-total")

        if wares.count() > self.max_positions:
            wares = wares[: self.max_positions]

        response_data["data"]["labels"] = list(wares.values_list("index", flat=True))
        values = list(wares.values_list("total", flat=True))
        response_data["data"]["datasets"].append(
            self.get_dataset(values, COLORS[: len(values)])
        )

        return JsonResponse(response_data)


class PurchaseInvoicesHistory(StaffOnlyMixin, BigChartHistoryMixin):
    model = Invoice
    date_field = "date"
    price_field = "invoiceitem__price"
    quantity_field = "invoiceitem__quantity"

    def _filter_objects(self, **kwargs):
        supplier = kwargs.get("supplier")
        if supplier:
            self.objects = self.objects.filter(supplier__pk=supplier)

    def _get_default_date_option(self, **kwargs):
        supplier = kwargs.get("supplier")
        if supplier:
            return "year"
        return "week"


class SaleInvoicesHistory(StaffOnlyMixin, BigChartHistoryMixin):
    model = SaleInvoice
    date_field = "issue_date"
    price_field = "saleinvoiceitem__price_"
    quantity_field = "saleinvoiceitem__quantity"

    def _annotate(self, qs):
        if self.metric == "SumBrutto":
            self.metric = "Sum"
            self.price_field = "{}brutto".format(self.price_field)
        if self.metric == "SumNetto":
            self.metric = "Sum"
            self.price_field = "{}netto".format(self.price_field)
        if self.metric == "AvgBrutto":
            self.metric = "Avg"
            self.price_field = "{}brutto".format(self.price_field)
        if self.metric == "AvgNetto":
            self.metric = "Avg"
            self.price_field = "{}netto".format(self.price_field)
        return super()._annotate(qs)

    def _filter_objects(self, **kwargs):
        self.objects = self.objects.exclude(
            invoice_type__in=[
                SaleInvoice.TYPE_PRO_FORMA,
                SaleInvoice.TYPE_CORRECTIVE,
                SaleInvoice.TYPE_WDT_PRO_FORMA,
            ]
        )


class CommissionHistory(StaffOnlyMixin, BigChartHistoryMixin):
    model = Commission
    date_field = "end_date"
    price_field = "commissionitem__price"
    quantity_field = "commissionitem__quantity"

    def _filter_objects(self, **kwargs):
        self.objects = self.objects.filter(status=Commission.DONE).exclude(
            end_date=None
        )


class RefrigerantWeightsHistory(BigChartHistoryMixin):
    model = SaleInvoice
    date_field = "issue_date"
    values_appendix = " g"

    def _annotate(self, qs):
        return qs.annotate(total=Sum("refrigerantweights__" + self.metric))


class WarePurchaseCost(ChartDataMixin, View):
    min_count = 3

    def get(self, *args, **kwargs):
        ware_pk = self.kwargs.get("pk")
        response_data = self.get_response_data_template(values_appendix=" zł")
        invoices = Invoice.objects.filter(invoiceitem__ware__pk=ware_pk).order_by(
            "date"
        )
        if invoices.count() < self.min_count:
            return JsonResponse({}, status=404)
        response_data["data"]["labels"] = list(invoices.values_list("date", flat=True))
        values = list(invoices.values_list("invoiceitem__price", flat=True))
        response_data["data"]["datasets"].append(self.get_dataset(values, COLORS[0]))

        response_data["options"]["legend"]["display"] = False
        return JsonResponse(response_data)


class WarePriceChanges(View):
    def get(self, *args, **kwargs):
        date_from = date_parser.parse(self.request.GET.get("date_from")).date()
        date_to = date_parser.parse(self.request.GET.get("date_to")).date()
        changes = WarePriceChange.objects.filter(
            created_date__date__gte=date_from, created_date__date__lte=date_to
        ).order_by("-created_date")
        response = {"changes": []}
        for change in changes:
            response["changes"].append(self.get_change_dict(change))
        return JsonResponse(response)

    def get_change_dict(self, change):
        return {
            "invoice": {
                "url": reverse(
                    "warehouse:invoice_detail",
                    kwargs={"pk": change.invoice.pk, "slug": slugify(change.invoice),},
                ),
                "number": change.invoice.number,
            },
            "ware": {
                "url": reverse(
                    "warehouse:ware_detail",
                    kwargs={"pk": change.ware.pk, "slug": slugify(change.ware)},
                ),
                "index": change.ware.index,
            },
            "supplier": {
                "url": reverse(
                    "warehouse:supplier_detail",
                    kwargs={
                        "pk": change.invoice.supplier.pk,
                        "slug": slugify(change.invoice.supplier),
                    },
                ),
                "name": change.invoice.supplier.name,
            },
            "is_discount": change.is_discount,
            "last_price": "{0:.2f} zł".format(change.last_price).replace(".", ","),
            "new_price": "{0:.2f} zł".format(change.new_price).replace(".", ","),
            "created_date": _date(change.created_date, "d E Y"),
        }


class DuePayments(StaffOnlyMixin, View):
    def get(self, *args, **kwargs):
        invoices = (
            SaleInvoice.objects.exclude(
                invoice_type__in=[
                    SaleInvoice.TYPE_PRO_FORMA,
                    SaleInvoice.TYPE_WDT_PRO_FORMA,
                ]
            )
            .filter(payed=False)
            .order_by("payment_date")
        )
        response = {"invoices": []}
        for invoice in invoices:
            if not invoice.payment_date:
                invoice.payed = True
                invoice.save()
                continue
            response["invoices"].append(self.get_invoice_dict(invoice))
        return JsonResponse(response)

    def get_invoice_dict(self, invoice):
        return {
            "url": reverse(
                "invoicing:sale_invoice_detail",
                kwargs={"pk": invoice.pk, "slug": slugify(invoice)},
            ),
            "number": invoice.number,
            "brutto_price": "{0:.2f} zł".format(invoice.total_value_brutto).replace(
                ".", ","
            ),
            "payment_date": _date(invoice.payment_date, "d E Y"),
            "is_exceeded": invoice.payment_date < date.today(),
            "contractor": {
                "url": reverse(
                    "invoicing:contractor_detail",
                    kwargs={
                        "pk": invoice.contractor.pk,
                        "slug": slugify(invoice.contractor),
                    },
                ),
                "name": invoice.contractor.name,
            },
            "payed_url": reverse(
                "invoicing:sale_invoice_set_payed", kwargs={"pk": invoice.pk}
            ),
        }


class Metrics(View):
    wares = None
    suppliers = None
    purchase_invoices = None
    sale_invoices = None
    contractors = None
    commissions = None
    weights = None
    ptus = None

    def get(self, *args, **kwargs):
        group = self.request.GET.get("group")
        self.date_from = date_parser.parse(self.request.GET.get("date_from")).date()
        self.date_to = date_parser.parse(self.request.GET.get("date_to")).date()

        if group == "purchase":
            response = self._get_purchase_metrics()
        elif group == "sale":
            response = self._get_sale_metrics()
        else:
            return {}
        return JsonResponse(response)

    def _get_purchase_metrics(self):
        response = {
            "ware_count": self.get_wares().count(),
            "supplier_count": self.get_suppliers().count(),
            "invoice_count": self.get_purchase_invoices().count(),
        }
        if self.request.user.is_staff:
            response.update(self._get_purchase_secret_metrics())
        return response

    def _get_purchase_secret_metrics(self):
        return {
            "invoice_sum": "{0:.2f} zł".format(
                self.get_purchase_invoices().total()
            ).replace(".", ",")
        }

    def _get_sale_metrics(self):
        response = {
            "contractor_count": self.get_contractors().count(),
            "sale_invoice_count": self.get_sale_invoices().count(),
            "commission_count": self.get_commissions().count(),
        }
        r134a = 0
        r1234yf = 0
        r12 = 0
        r404 = 0
        if self.get_weights():
            r134a = self.get_weights().aggregate(Sum("r134a"))["r134a__sum"]
            r1234yf = self.get_weights().aggregate(Sum("r1234yf"))["r1234yf__sum"]
            r12 = self.get_weights().aggregate(Sum("r12"))["r12__sum"]
            r404 = self.get_weights().aggregate(Sum("r404"))["r404__sum"]
        response["r134a_sum"] = "{} g".format(r134a)
        response["r1234yf_sum"] = "{} g".format(r1234yf)
        response["r12_sum"] = "{} g".format(r12)
        response["r404_sum"] = "{} g".format(r404)

        if self.request.user.is_staff:
            response.update(self._get_sale_secret_metrics())
        return response

    def _get_sale_secret_metrics(self):
        invoices_sum_netto = 0
        invoices_sum_brutto = 0
        tax_sum = 0
        person_tax_sum = 0
        if self.get_sale_invoices():
            invoices_sum_netto = self._get_sale_netto(self.get_sale_invoices())
            invoices_sum_brutto = self._get_sale_brutto(self.get_sale_invoices())
            tax_sum = invoices_sum_brutto - invoices_sum_netto
        person_invoices = self.get_sale_invoices().filter(contractor__nip=None)
        if person_invoices:
            person_netto = self._get_sale_netto(person_invoices)
            person_brutto = self._get_sale_brutto(person_invoices)
            person_tax_sum = person_brutto - person_netto
        response = {}
        response["sale_invoice_sum"] = "{0:.2f} zł".format(invoices_sum_netto).replace(
            ".", ","
        )
        response["sale_invoice_sum_brutto"] = "{0:.2f} zł".format(
            invoices_sum_brutto
        ).replace(".", ",")
        response["vat_sum"] = "{0:.2f} zł".format(tax_sum).replace(".", ",")
        response["person_vat_sum"] = "{0:.2f} zł".format(person_tax_sum).replace(
            ".", ","
        )
        response["company_vat_sum"] = "{0:.2f} zł".format(
            tax_sum - person_tax_sum
        ).replace(".", ",")

        ptu_sum = 0
        if self.get_ptus():
            ptu_sum = self.get_ptus().aggregate(Sum("value"))["value__sum"]
        response["ptu_sum"] = "{0:.2f} zł".format(ptu_sum).replace(".", ",")

        response["commission_sum"] = "{0:.2f} zł".format(
            self.get_commissions().total()
        ).replace(".", ",")
        return response

    def _get_sale_netto(self, queryset):
        return queryset.total(price_type="netto")

    def _get_sale_brutto(self, queryset):
        return queryset.total(price_type="brutto")

    def get_wares(self):
        if self.wares is not None:
            return self.wares
        self.wares = Ware.objects.filter(
            created_date__date__gte=self.date_from, created_date__date__lte=self.date_to
        )
        return self.wares

    def get_suppliers(self):
        if self.suppliers is not None:
            return self.suppliers
        self.suppliers = Supplier.objects.filter(
            created_date__date__gte=self.date_from, created_date__date__lte=self.date_to
        )
        return self.suppliers

    def get_purchase_invoices(self):
        if self.purchase_invoices is not None:
            return self.purchase_invoices
        self.purchase_invoices = Invoice.objects.filter(
            date__gte=self.date_from, date__lte=self.date_to
        )
        return self.purchase_invoices

    def get_contractors(self):
        if self.contractors is not None:
            return self.contractors
        self.contractors = Contractor.objects.filter(
            created_date__date__gte=self.date_from, created_date__date__lte=self.date_to
        )
        return self.contractors

    def get_weights(self):
        if self.weights is not None:
            return self.weights
        self.weights = RefrigerantWeights.objects.filter(
            sale_invoice__issue_date__gte=self.date_from,
            sale_invoice__issue_date__lte=self.date_to,
        )
        return self.weights

    def get_sale_invoices(self):
        if self.sale_invoices is not None:
            return self.sale_invoices
        self.sale_invoices = SaleInvoice.objects.filter(
            issue_date__gte=self.date_from, issue_date__lte=self.date_to
        ).exclude(
            invoice_type__in=[
                SaleInvoice.TYPE_PRO_FORMA,
                SaleInvoice.TYPE_CORRECTIVE,
                SaleInvoice.TYPE_WDT_PRO_FORMA,
            ]
        )
        return self.sale_invoices

    def get_commissions(self):
        if self.commissions is not None:
            return self.commissions
        self.commissions = Commission.objects.filter(
            end_date__gte=self.date_from,
            end_date__lte=self.date_to,
            status=Commission.DONE,
        )
        return self.commissions

    def get_ptus(self):
        if self.ptus is not None:
            return self.ptus
        self.ptus = ReceiptPTU.objects.filter(
            date__gte=self.date_from, date__lte=self.date_to
        )
        return self.ptus


class PTUList(StaffOnlyMixin, View):
    def get(self, *args, **kwargs):
        try:
            date_from = date_parser.parse(self.request.GET.get("date_from")).date()
            date_to = date_parser.parse(self.request.GET.get("date_to")).date()
        except TypeError:
            return JsonResponse(
                {"status": "error", "message": "Niepoprawny zakres dat."}, status=400
            )
        delta = date_to - date_from
        response = {"ptu": []}
        ptu_sum = 0
        for i in range(delta.days + 1):
            date = date_from + timedelta(days=i)
            try:
                ptu = ReceiptPTU.objects.get(date=date)
                ptu_sum += ptu.value
                response["ptu"].append(
                    {
                        "date": _date(ptu.date, "d E Y (l)"),
                        "date_value": _date(ptu.date, "d.m.Y"),
                        "value": "{0:.2f} zł".format(ptu.value).replace(".", ","),
                        "warning": False,
                    }
                )
            except ReceiptPTU.DoesNotExist:
                response["ptu"].append(
                    {
                        "date": _date(date, "d E Y (l)"),
                        "date_value": _date(date, "d.m.Y"),
                        "value": "0,00 zł",
                        "warning": True,
                    }
                )
        response["sum"] = ("{0:.2f} zł".format(ptu_sum).replace(".", ","),)
        return JsonResponse(response)


class GetPTUValue(StaffOnlyMixin, View):
    def get(self, *args, **kwargs):
        try:
            date = date_parser.parse(self.request.GET.get("date")).date()
        except TypeError:
            return JsonResponse(
                {"status": "error", "message": "Niepoprawna data."}, status=400
            )
        try:
            ptu = ReceiptPTU.objects.get(date=date)
            return JsonResponse({"value": ptu.value})
        except ReceiptPTU.DoesNotExist:
            return JsonResponse({"value": 0})


class SavePTU(StaffOnlyMixin, View):
    def post(self, *args, **kwargs):
        date = date_parser.parse(self.request.POST.get("date"), dayfirst=True).date()
        value = self.request.POST.get("value")
        if not date or not value:
            return JsonResponse(
                {"status": "error", "message": "Niepoprawne dane."}, status=400
            )
        try:
            ptu = ReceiptPTU.objects.get(date=date)
        except ReceiptPTU.DoesNotExist:
            ptu = ReceiptPTU(date=date)
        value = value.replace(",", ".")
        ptu.value = value
        ptu.save()
        return JsonResponse({"status": "success", "message": "Poprawnie zapisano PTU."})


class GetSummary(StaffOnlyMixin, View):
    def get(self, *args, **kwargs):
        try:
            date_from = date_parser.parse(self.request.GET.get("date_from")).date()
            date_to = date_parser.parse(self.request.GET.get("date_to")).date()
        except TypeError:
            return JsonResponse(
                {"status": "error", "message": "Niepoprawny zakres dat."}, status=400
            )
        response = {}
        ptu_sum = self._get_ptu(date_from, date_to)
        response["ptu"] = "{0:.2f} zł".format(ptu_sum).replace(".", ",")

        commissions_sum = self._get_commissions(date_from, date_to)
        response["commissions"] = "{0:.2f} zł".format(commissions_sum).replace(".", ",")

        vat_sum = self._get_vat(date_from, date_to)
        response["vat"] = "{0:.2f} zł".format(vat_sum).replace(".", ",")

        purchase_sum = self._get_purchase(date_from, date_to)
        response["purchase"] = "{0:.2f} zł".format(purchase_sum).replace(".", ",")

        all_sum = (
            float(commissions_sum)
            - float(ptu_sum)
            - float(vat_sum)
            - float(purchase_sum)
        )
        response["sum"] = "{0:.2f} zł".format(all_sum).replace(".", ",")
        date_range = self._get_date_range(date_from, date_to)
        response["urls"] = {
            "commissions": "{}?end_date={}&status=__ALL__".format(
                reverse("commission:commissions"), date_range
            ),
            "invoices": "{}?issue_date={}".format(
                reverse("invoicing:sale_invoices"), date_range
            ),
            "purchase": "{}?date={}".format(reverse("warehouse:invoices"), date_range),
            "wares": "{}?purchase_date={}".format(
                reverse("warehouse:wares"), date_range
            ),
        }
        response[
            "invoices_without_commission"
        ] = self._get_sale_invoices_wthout_commission(date_from, date_to)
        return JsonResponse(response)

    def _get_date_range(self, date_from, date_to):
        return "{}+-+{}".format(
            date_from.strftime("%d.%m.%Y"), date_to.strftime("%d.%m.%Y")
        )

    def _get_ptu(self, date_from, date_to):
        ptu_sum = 0
        ptu_objects = ReceiptPTU.objects.filter(date__gte=date_from, date__lte=date_to)
        if ptu_objects:
            ptu_sum = ptu_objects.aggregate(Sum("value"))["value__sum"]
        return ptu_sum

    def _get_commissions(self, date_from, date_to):
        commissions = Commission.objects.filter(
            end_date__gte=date_from, end_date__lte=date_to, status=Commission.DONE
        )
        return commissions.total()

    def _get_vat(self, date_from, date_to):
        invoices = (
            SaleInvoice.objects.filter(
                issue_date__gte=date_from, issue_date__lte=date_to
            )
            .exclude(contractor__nip=None,)
            .exclude(
                invoice_type__in=[
                    SaleInvoice.TYPE_PRO_FORMA,
                    SaleInvoice.TYPE_CORRECTIVE,
                    SaleInvoice.TYPE_WDT_PRO_FORMA,
                ]
            )
        )
        return invoices.total(price_type="brutto") - invoices.total(price_type="netto")

    def _get_purchase(self, date_from, date_to):
        invoices = Invoice.objects.filter(date__gte=date_from, date__lte=date_to)
        return invoices.total()

    def _get_sale_invoices_wthout_commission(self, date_from, date_to):
        invoices = SaleInvoice.objects.filter(
            issue_date__gte=date_from, issue_date__lte=date_to, commission=None
        )
        return [
            {
                "url": reverse(
                    "invoicing:sale_invoice_detail",
                    kwargs={"pk": invoice.pk, "slug": slugify(invoice)},
                ),
                "number": invoice.number,
                "brutto_price": "{0:.2f} zł".format(invoice.total_value_brutto).replace(
                    ".", ","
                ),
                "contractor": {
                    "url": reverse(
                        "invoicing:contractor_detail",
                        kwargs={
                            "pk": invoice.contractor.pk,
                            "slug": slugify(invoice.contractor),
                        },
                    ),
                    "name": invoice.contractor.name,
                },
            }
            for invoice in invoices
        ]


class UnpayedDekoInvoicesView(StaffOnlyMixin, View):
    def get(self, *args, **kwargs):
        self.settings = InvoiceDownloadSettings.load()
        with requests.Session() as s:
            url = "http://sklep.dekoautoparts.pl/pl"
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                    " Chrome/75.0.3770.80 Safari/537.36"
                )
            }
            r = s.get(url, headers=headers)
            if r.status_code != 200:
                return JsonResponse({}, status=500)

            soup = BeautifulSoup(r.content, "html5lib")
            data = {
                "__EVENTTARGET": "ctl00$ctl00$BodyContentPlaceHolder$LoginForm$LoginButton",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": soup.find("input", attrs={"name": "__VIEWSTATE"})[
                    "value"
                ],
                "__VIEWSTATEGENERATOR": soup.find(
                    "input", attrs={"name": "__VIEWSTATEGENERATOR"}
                )["value"],
                "__EVENTVALIDATION": soup.find(
                    "input", attrs={"name": "__EVENTVALIDATION"}
                )["value"],
                "ctl00$ctl00$BodyContentPlaceHolder$LoginForm$Username": self.settings.DEKO_LOGIN,
                "ctl00$ctl00$BodyContentPlaceHolder$LoginForm$Password": self.settings.DEKO_PASSWORD,
            }
            r = s.post(url, data=data, headers=headers)
            if r.status_code != 200:
                return JsonResponse({}, status=500)

            url = "http://sklep.dekoautoparts.pl/AjaxServices/Informations.svc/GetFilteredInvoices"
            data = {
                "dateFrom": (date.today() - timedelta(60)).strftime("%Y-%m-%d"),
                "dateTo": (date.today() + timedelta(1)).strftime("%Y-%m-%d"),
                "overdueOnly": False,
            }
            r = s.post(url, json=data, headers=headers)
            if r.status_code != 200:
                return JsonResponse({}, status=500)

            invoices = []
            sum_to_pay = 0
            soup = BeautifulSoup(r.json()["d"], "html5lib")
            for row in soup.find("table").find_all("tr", attrs={"class": None})[1:]:
                to_pay = row.find(
                    "td", attrs={"class": "flex-price-to-pay"}
                ).text.strip()
                if to_pay == "0 PLN":
                    continue
                to_pay = Decimal(
                    to_pay.rstrip(" PLN").replace(" ", "").replace(",", ".")
                )
                sum_to_pay += to_pay
                number = row.find("td").text.strip()
                invoice = {
                    "number": number,
                    "date": _date(
                        date_parser.parse(
                            row.find("td", attrs={"attr-text": "Wydane:"}).text.strip(),
                            dayfirst=True,
                        ).date()
                    ),
                    "to_pay": to_pay,
                }
                try:
                    obj = Invoice.objects.get(
                        number=number, supplier=self.settings.DEKO_SUPPLIER
                    )
                    invoice["url"] = reverse(
                        "warehouse:invoice_detail",
                        kwargs={"slug": slugify(obj), "pk": obj.pk},
                    )
                except Invoice.DoesNotExist:
                    pass
                invoices.append(invoice)
            return JsonResponse({"invoices": invoices, "to_pay": sum_to_pay})
