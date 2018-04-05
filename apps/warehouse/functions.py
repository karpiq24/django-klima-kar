# -*- coding: utf-8 -*-

import io
import datetime

from xlsxwriter import Workbook

from KlimaKar import settings
from apps.warehouse.models import WarePriceChange, Invoice


def export_wares(queryset):
    output = io.BytesIO()
    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': True})
    bold_money = workbook.add_format({'num_format': '#,##0.00 zł', 'bold': True})
    border = workbook.add_format({'border': 1})
    bold_border = workbook.add_format({'border': 1, 'bold': True})
    border_money = workbook.add_format({'border': 1, 'num_format': '#,##0.00 zł'})
    columns = [
        ('Lp.', 5),
        ('Nr kat.', 35),
        ('Nazwa', 35),
        ('szt.', 5),
        ('cena', 15),
        ('wartość', 15)
    ]

    today = datetime.date.today()
    worksheet.write(0, 1, "INWENTARYZACJA NA DZIEŃ {}".format(today.strftime('%d.%m.%Y')))

    row = 2
    col = 0

    for column in columns:
        worksheet.write(row, col, column[0], bold_border)
        worksheet.set_column(col, col, column[1])
        col += 1

    row = 3
    col = 0

    for ware in queryset.order_by('index'):
        worksheet.write(row, col, row - 2, border)
        worksheet.write(row, col + 1, ware.index, border)
        worksheet.write(row, col + 2, ware.name, border)
        worksheet.write(row, col + 3, ware.stock, border)
        worksheet.write(row, col + 4, ware.last_price, border_money)
        if ware.last_price:
            worksheet.write(row, col + 5, ware.stock * ware.last_price, border_money)
        else:
            worksheet.write(row, col + 5, '', border_money)
        row += 1

    worksheet.write(row + 1, 4, 'SUMA', bold)
    worksheet.write(row + 1, 5, '=SUM(F4:F{})'.format(row), bold_money)

    worksheet.write(row + 3, 1, 'Remanent zakończono na pozycji {}.'.format(row - 3))
    worksheet.write(row + 4, 1, 'Wartość słownie: ')

    workbook.close()
    output.seek(0)
    return output


def check_ware_price_changes(invoice):
    for item in invoice.invoiceitem_set.all():
        last_invoice = Invoice.objects.filter(supplier=invoice.supplier, invoiceitem__ware=item.ware).exclude(
            pk=invoice.pk).order_by('-date').first()
        if not last_invoice:
            continue
        last_price = last_invoice.invoiceitem_set.filter(ware=item.ware).first().price
        percent_change = ((item.price - last_price) / last_price) * 100
        if percent_change >= settings.PRICE_CHHANGE_PERCENTAGE or percent_change <= -settings.PRICE_CHHANGE_PERCENTAGE:
            WarePriceChange.objects.create(invoice=invoice, ware=item.ware, last_price=last_price, new_price=item.price)
