import datetime
import io

from xlsxwriter import Workbook

from apps.invoicing.models import SaleInvoice


def get_next_invoice_number(invoice_type):
    year = datetime.date.today().year
    invoices = SaleInvoice.objects.filter(invoice_type=invoice_type, number_year=year)
    if invoice_type == SaleInvoice.TYPE_VAT:
        invoices = (
            invoices
            | SaleInvoice.objects.filter(
                invoice_type=SaleInvoice.TYPE_WDT, number_year=year
            )
        ).distinct()
    elif invoice_type == SaleInvoice.TYPE_WDT:
        invoices = (
            invoices
            | SaleInvoice.objects.filter(
                invoice_type=SaleInvoice.TYPE_VAT, number_year=year
            )
        ).distinct()
    elif invoice_type == SaleInvoice.TYPE_PRO_FORMA:
        invoices = (
            invoices
            | SaleInvoice.objects.filter(
                invoice_type=SaleInvoice.TYPE_WDT_PRO_FORMA, number_year=year
            )
        ).distinct()
    elif invoice_type == SaleInvoice.TYPE_WDT_PRO_FORMA:
        invoices = (
            invoices
            | SaleInvoice.objects.filter(
                invoice_type=SaleInvoice.TYPE_PRO_FORMA, number_year=year
            )
        ).distinct()
    if not invoices.exists():
        return "1/{}".format(year)
    last_number = invoices.order_by("-number_value").first().number_value
    return "{}/{}".format(last_number + 1, year)


def generate_refrigerant_weights_report(queryset):
    output = io.BytesIO()
    workbook = Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet()
    worksheet.freeze_panes(1, 0)
    worksheet.set_row(0, 30)

    bold = workbook.add_format({"bold": True})
    bold_weight = workbook.add_format({"num_format": '#0 "g"', "bold": True})
    border = workbook.add_format({"border": 1})
    bold_border = workbook.add_format({"border": 1, "bold": True})
    border_weight = workbook.add_format({"border": 1, "num_format": '#0 "g"'})
    big_bold = workbook.add_format({"font_size": 22, "bold": True})
    columns = [
        ("Typ faktury", 15),
        ("Numer", 15),
        ("Data wystawienia", 15),
        ("Kontrahent", 50),
        ("R134a", 10),
        ("R1234yf", 10),
        ("R12", 10),
        ("R404", 10),
    ]

    row = 0
    col = 0

    for column in columns:
        worksheet.write(row, col, column[0], bold_border)
        worksheet.set_column(col, col, column[1])
        col += 1

    row = 1
    col = 0

    for invoice in queryset.order_by("number_year", "number_value"):
        worksheet.write(row, col, invoice.get_invoice_type_display(), border)
        worksheet.write(row, col + 1, invoice.number, border)
        worksheet.write(row, col + 2, invoice.issue_date.strftime("%d.%m.%Y"), border)
        worksheet.write(row, col + 3, invoice.contractor.name, border)
        worksheet.write(row, col + 4, invoice.refrigerantweights.r134a, border_weight)
        worksheet.write(row, col + 5, invoice.refrigerantweights.r1234yf, border_weight)
        worksheet.write(row, col + 6, invoice.refrigerantweights.r12, border_weight)
        worksheet.write(row, col + 7, invoice.refrigerantweights.r404, border_weight)
        row += 1

    worksheet.write(row + 1, 0, "SUMA", bold)
    worksheet.write(row + 1, 4, "=SUM(E2:E{})".format(row), bold_weight)
    worksheet.write(row + 1, 5, "=SUM(F2:F{})".format(row), bold_weight)
    worksheet.write(row + 1, 6, "=SUM(G2:G{})".format(row), bold_weight)
    worksheet.write(row + 1, 7, "=SUM(H2:H{})".format(row), bold_weight)

    worksheet.write(0, 9, "R134a", big_bold)
    worksheet.write(0, 10, "=E{}".format(row + 2), big_bold)
    worksheet.set_column(9, 9, 15)
    worksheet.set_column(10, 10, 25)
    worksheet.write(0, 11, "R1234yf", big_bold)
    worksheet.write(0, 12, "=F{}".format(row + 2), big_bold)
    worksheet.set_column(11, 11, 15)
    worksheet.set_column(12, 12, 25)
    worksheet.write(0, 13, "R12", big_bold)
    worksheet.write(0, 14, "=G{}".format(row + 2), big_bold)
    worksheet.set_column(13, 13, 15)
    worksheet.set_column(14, 14, 25)
    worksheet.write(0, 15, "R404", big_bold)
    worksheet.write(0, 16, "=H{}".format(row + 2), big_bold)
    worksheet.set_column(15, 15, 15)
    worksheet.set_column(16, 16, 25)

    workbook.close()
    output.seek(0)
    return output
