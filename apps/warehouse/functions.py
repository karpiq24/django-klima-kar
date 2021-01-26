import io
import datetime
import requests
import xml.dom.minidom

from django.db.models import Count, Q
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from xlsxwriter import Workbook
from tqdm import tqdm

from apps.settings.models import InvoiceDownloadSettings
from apps.warehouse.models import Invoice, Ware
from apps.warehouse.management.commands.loadintercars import getData
from apps.audit.functions import (
    post_save_handler as audit_post,
    pre_save_handler as audit_pre,
)
from apps.search.utils import post_save_handler as search_post


def generate_ware_inventory(queryset):
    output = io.BytesIO()
    workbook = Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({"bold": True})
    bold_money = workbook.add_format({"num_format": "#,##0.00 zł", "bold": True})
    border = workbook.add_format({"border": 1})
    bold_border = workbook.add_format({"border": 1, "bold": True})
    border_money = workbook.add_format({"border": 1, "num_format": "#,##0.00 zł"})
    columns = [
        ("Lp.", 5),
        ("Nr kat.", 35),
        ("Nazwa", 35),
        ("szt.", 5),
        ("cena", 15),
        ("wartość", 15),
    ]

    today = datetime.date.today()
    worksheet.write(
        0, 1, "INWENTARYZACJA NA DZIEŃ {}".format(today.strftime("%d.%m.%Y"))
    )

    row = 2
    col = 0

    for column in columns:
        worksheet.write(row, col, column[0], bold_border)
        worksheet.set_column(col, col, column[1])
        col += 1

    row = 3
    col = 0

    for ware in queryset.order_by("index"):
        worksheet.write(row, col, row - 2, border)
        worksheet.write(row, col + 1, ware.index, border)
        worksheet.write(row, col + 2, ware.name, border)
        worksheet.write(row, col + 3, ware.stock, border)
        worksheet.write(row, col + 4, ware.last_price, border_money)
        if ware.last_price:
            worksheet.write(row, col + 5, ware.stock * ware.last_price, border_money)
        else:
            worksheet.write(row, col + 5, "", border_money)
        row += 1

    worksheet.write(row + 1, 4, "SUMA", bold)
    worksheet.write(row + 1, 5, "=SUM(F4:F{})".format(row), bold_money)

    worksheet.write(row + 3, 1, "Remanent zakończono na pozycji {}.".format(row - 3))
    worksheet.write(row + 4, 1, "Wartość słownie: ")

    workbook.close()
    output.seek(0)
    return output


def get_inter_cars_barcodes():
    pre_save.disconnect(audit_pre, sender=Invoice)
    post_save.disconnect(audit_post, sender=Invoice)
    post_save.disconnect(search_post, sender=Invoice)
    pre_save.disconnect(audit_pre, sender=Ware)
    post_save.disconnect(audit_post, sender=Ware)
    post_save.disconnect(search_post, sender=Ware)

    config = InvoiceDownloadSettings.load()
    invoices = (
        Invoice.objects.filter(supplier=config.INTER_CARS_SUPPLIER)
        .annotate(item_count=Count("invoiceitem"))
        .order_by("-item_count")
    )
    checked_wares = []

    url = settings.IC_API_URL + "GetInvoices"
    url_detail = settings.IC_API_URL + "GetInvoice"
    headers = {
        "kh_kod": config.INTER_CARS_CLIENT_NUMBER,
        "token": config.INTER_CARS_TOKEN,
    }

    for invoice in tqdm(invoices):
        wares = (
            Ware.objects.filter(invoiceitem__invoice=invoice, barcode="")
            .exclude(pk__in=checked_wares)
            .distinct()
        )
        if not wares:
            continue

        if not invoice.remote_id:
            r = requests.get(
                url,
                params={
                    "from": invoice.date.strftime("%Y%m%d"),
                    "to": invoice.date.strftime("%Y%m%d"),
                },
                headers=headers,
            )
            if r.status_code != 200:
                print(f"Invoice {invoice} failed fetching")
                continue
            DOMTree = xml.dom.minidom.parseString(r.text)
            collection = DOMTree.documentElement
            xml_invoices = collection.getElementsByTagName("nag")
            xml_invoice = [
                i for i in xml_invoices if getData(i, "numer") == invoice.number
            ]
            if not xml_invoice:
                continue
            xml_invoice = xml_invoice[0]
            if not invoice.remote_id:
                invoice.remote_id = getData(xml_invoice, "id")
                invoice.save()

        r = requests.get(url_detail, params={"id": invoice.remote_id}, headers=headers)
        if r.status_code != 200:
            print(f"Invoice {invoice} failed fetching")
            continue

        DOMTree = xml.dom.minidom.parseString(r.text)
        collection = DOMTree.documentElement
        xml_wares = collection.getElementsByTagName("poz")
        for xml_ware in xml_wares:
            barcode_list = getData(xml_ware, "kod_kre")
            if not barcode_list:
                continue
            ean_list = [
                code.strip()
                for code in barcode_list.split(",")
                if len(code.strip()) == 13 and code.strip().isdigit()
            ]
            barcode = ean_list[0] if ean_list else ""
            if not barcode:
                continue
            try:
                ware = wares.get(
                    Q(index=getData(xml_ware, "indeks"))
                    | Q(index_slug=Ware.slugify(getData(xml_ware, "indeks")))
                )
                checked_wares.append(ware.pk)
                ware.barcode = barcode
                ware.save()
            except Ware.DoesNotExist:
                continue
            except Ware.MultipleObjectsReturned:
                print(f"Multiple wares with same index: {getData(xml_ware, 'indeks')}")

    pre_save.connect(audit_pre, sender=Invoice)
    post_save.connect(audit_post, sender=Invoice)
    post_save.connect(search_post, sender=Invoice)
    pre_save.connect(audit_pre, sender=Ware)
    post_save.connect(audit_post, sender=Ware)
    post_save.connect(search_post, sender=Ware)
