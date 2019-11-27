import unicodedata

from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from django_tables2 import SingleTableView
from dal import autocomplete
from github import Github
from smsapi.client import SmsApiPlClient

from KlimaKar import settings
from KlimaKar.forms import IssueForm
from KlimaKar.email import get_email_message
from django.core.mail import mail_admins


class HomeView(TemplateView):
    template_name = "stats/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        has_permission = False
        if self.request.user.is_superuser:
            has_permission = True
        elif self.request.user.groups.filter(name='boss').exists():
            has_permission = True

        context['has_permission'] = has_permission
        context['stats'] = {
            'purchase': {
                'group': 'purchase',
                'metrics': self._get_purchase_metrics(has_permission),
                'charts': self._get_purchase_charts(has_permission),
                'ware_price_changes_url': reverse('stats:ware_price_changes')
            },
            'sale': {
                'group': 'sale',
                'metrics': self._get_sale_metrics(has_permission),
                'charts': self._get_sale_charts(has_permission)
            }
        }
        return context

    def _get_purchase_charts(self, has_permission):
        charts = []
        if has_permission:
            charts.append({
                'title': 'Historia faktur zakupowych',
                'url': reverse('stats:purchase_invoices_history'),
                'big': True,
                'select_date': {
                    'extra': True
                },
                'custom_select': [('Sum', 'Suma'), ('Avg', 'Średnia'), ('Count', 'Ilość')]
            })
            charts.append({
                'title': 'Historia zakupów u dostawców',
                'select_date': True,
                'custom_select': [('Sum', 'Suma'), ('Avg', 'Średnia'), ('Count', 'Ilość')],
                'url': reverse('stats:supplier_purchase_history')
            })
        charts.append({
            'title': 'Historia zakupów towarów',
            'select_date': True,
            'custom_select': [('Count', 'Ilość'), ('Sum', 'Suma')],
            'url': reverse('stats:ware_purchase_history')
        })
        return charts

    def _get_purchase_metrics(self, has_permission):
        metrics = []
        metrics.append({
            'icon': 'fa-tags',
            'color': '#E21E00',
            'title': 'Liczba dodanych towarów',
            'class': 'ware_count'
        })
        metrics.append({
            'icon': 'fa-truck',
            'color': '#C1456E',
            'title': 'Liczba dodanych dostawców',
            'class': 'supplier_count'
        })
        metrics.append({
            'icon': 'fa-file-alt',
            'color': '#8355C5',
            'title': 'Liczba dodanych faktur',
            'class': 'invoice_count'
        })
        if has_permission:
            metrics.append({
                'icon': 'fa-file-alt',
                'color': '#8355C5',
                'title': 'Kwota netto dodanych faktur',
                'class': 'invoice_sum'
            })
        return metrics

    def _get_sale_charts(self, has_permission):
        charts = []
        if has_permission:
            charts.append({
                'title': 'Historia faktur sprzedażowych',
                'url': reverse('stats:sale_invoices_history'),
                'big': True,
                'select_date': {
                    'extra': True
                },
                'custom_select': [
                    ('SumNetto', 'Suma netto'),
                    ('SumBrutto', 'Suma brutto'),
                    ('AvgNetto', 'Średnia netto'),
                    ('AvgBrutto', 'Średnia brutto'), ('Count', 'Ilość')]
            })
            charts.append({
                'title': 'Historia zleceń',
                'url': reverse('stats:commission_history'),
                'big': True,
                'select_date': {
                    'extra': True
                },
                'custom_select': [
                    ('Sum', 'Suma'),
                    ('Avg', 'Średnia'),
                    ('Count', 'Ilość')]
            })
        charts.append({
            'title': 'Historia sprzedaży czynników',
            'url': reverse('stats:refrigerant_history'),
            'big': True,
            'select_date': {
                'extra': True
            },
            'custom_select': [('r134a', 'R134a'), ('r1234yf', 'R1234yf'), ('r12', 'R12'), ('r404', 'R404')]
        })
        return charts

    def _get_sale_metrics(self, has_permission):
        metrics = []
        metrics.append({
            'icon': 'fa-book',
            'color': '#89D23A',
            'title': 'Liczba dodanych faktur',
            'class': 'sale_invoice_count'
        })
        if has_permission:
            metrics.append({
                'icon': 'fa-book',
                'color': '#89D23A',
                'title': 'Kwota netto dodanych faktur',
                'class': 'sale_invoice_sum'
            })
            metrics.append({
                'icon': 'fa-book',
                'color': '#89D23A',
                'title': 'Kwota brutto dodanych faktur',
                'class': 'sale_invoice_sum_brutto'
            })
            metrics.append({
                'icon': 'fa-percentage',
                'color': '#E21E00',
                'title': 'Podatek VAT',
                'class': 'vat_sum'
            })
            metrics.append({
                'icon': 'fa-percentage',
                'color': '#E21E00',
                'title': 'Podatek VAT od firm',
                'class': 'company_vat_sum'
            })
            metrics.append({
                'icon': 'fa-percentage',
                'color': '#E21E00',
                'title': 'Podatek VAT od osób fizycznych',
                'class': 'person_vat_sum'
            })
            metrics.append({
                'icon': 'fa-hand-holding-usd',
                'color': '#E21E00',
                'title': 'Kwota PTU',
                'class': 'ptu_sum'
            })

        metrics.append({
            'icon': 'fa-tasks',
            'color': '#427BD2',
            'title': 'Liczba zakończonych zleceń',
            'class': 'commission_count'
        })
        if has_permission:
            metrics.append({
                'icon': 'fa-tasks',
                'color': '#427BD2',
                'title': 'Kwota zakończonych zleceń',
                'class': 'commission_sum'
            })

        metrics.append({
            'icon': 'fa-users',
            'color': '#00A0DF',
            'title': 'Liczba dodanych kontrahentów',
            'class': 'contractor_count'
        })
        metrics.append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Sprzedaż czynnika R134a',
            'class': 'r134a_sum'
        })
        metrics.append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Sprzedaż czynnika R1234yf',
            'class': 'r1234yf_sum'
        })
        metrics.append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Sprzedaż czynnika R12',
            'class': 'r12_sum'
        })
        metrics.append({
            'icon': 'fa-flask',
            'color': '#F8640B',
            'title': 'Sprzedaż czynnika R404',
            'class': 'r404_sum'
        })
        return metrics


class SendIssueView(View):
    def post(self, request, *args, **kwargs):
        issue_form = IssueForm(data=request.POST)
        if issue_form.is_valid():
            data = issue_form.cleaned_data
            g = Github(settings.GITHUB_TOKEN)
            repo = g.get_repo(settings.GITHUB_REPOSITORY)
            repo.create_issue(
                title=data['title'],
                body=data['body'],
                labels=[data['label']],
                assignee=settings.GITHUB_USERNAME)

            if settings.ADMINS:
                get_email_message(
                    subject='Nowe zgłoszenie: {}'.format(data['title']),
                    body='{}\n\n{}'.format(data['body'], data.get('secret')),
                    to=[admin[1] for admin in settings.ADMINS]
                ).send(fail_silently=True)
            return JsonResponse({'status': 'success', 'message': 'Zgłoszenie zostało wysłane'}, status=200)
        return JsonResponse({'status': 'error', 'message': 'Wystąpił błąd. Spróbuj ponownie.'}, status=400)


class CustomSelect2QuerySetView(autocomplete.Select2QuerySetView):
    modal_create = False
    always_show_create = False
    create_empty_label = 'Nowy obiekt'

    def get_create_option(self, context, q):
        create_option = []
        display_create_option = False
        if self.always_show_create:
            display_create_option = True
        elif self.modal_create and q:
            display_create_option = True
        elif self.create_field and q:
            page_obj = context.get('page_obj', None)
            if ((page_obj is None or page_obj.number == 1)
                    and not self.get_queryset().filter(**{self.create_field: q}).exists()):
                display_create_option = True

        if display_create_option:
            create_option = [{
                'id': q or self.create_empty_label,
                'text': ('Dodaj "%(new_value)s"') % {'new_value': q or self.create_empty_label},
                'create_id': True,
            }]
        return create_option

    def post(self, request):
        if self.modal_create:
            return JsonResponse({'status': 'disabled'})
        if not self.create_field:
            raise ImproperlyConfigured('Missing "create_field"')

        text = request.POST.get('text', None)

        if text is None:
            return HttpResponseBadRequest()

        result = self.create_object(text)

        return JsonResponse({
            'id': result.pk,
            'text': str(result),
        })

    def get_results(self, context):
        return [
            dict({
                'id': self.get_result_value(result),
                'text': self.get_result_label(result),
                'selected_text': self.get_selected_result_label(result),
            }, **self.extend_result_data(result)) for result in context['object_list']
        ]

    def extend_result_data(self, data):
        return {}


class FilteredSingleTableView(SingleTableView):
    filter_class = None
    tab_filter = None
    tab_filter_default = None
    tab_filter_choices = None
    tab_filter_all_choice = ('__ALL__', 'Wszystkie')

    def get_table_data(self):
        self.data = super(FilteredSingleTableView, self).get_table_data()
        self.filter = self.filter_class(self.get_filter_params(), queryset=self.data)
        return self.filter.qs

    def get_filter_params(self):
        params = self.request.GET.copy()
        if self.tab_filter and self.tab_filter not in params:
            params[self.tab_filter] = self.tab_filter_default
        if params.get(self.tab_filter) == self.tab_filter_all_choice[0]:
            params.pop(self.tab_filter)
        return params

    def get_tab_counts(self):
        counts = {}
        params = self.get_filter_params()
        for choice in self.get_tab_filter_choices():
            params = self.process_params_per_choice(params, choice)
            params.pop(self.tab_filter, None)
            tab_filter = self.filter_class(params, queryset=self.data)
            if choice[0] == self.tab_filter_all_choice[0]:
                counts[choice[0]] = tab_filter.qs.count()
            else:
                counts[choice[0]] = self.get_tab_filter_count(choice[0], tab_filter.qs)
        return counts

    def process_params_per_choice(self, params, choice):
        return params

    def get_context_data(self, **kwargs):
        context = super(FilteredSingleTableView, self).get_context_data(**kwargs)
        context['filter'] = self.filter
        if self.tab_filter:
            context['current_tab_filter'] = self.request.GET.get(self.tab_filter, self.tab_filter_default)
            context['{}_data'.format(self.tab_filter)] = self.get_tab_filter_choices()
        return context

    def get_tab_filter_choices(self):
        return self.tab_filter_choices + [(*self.tab_filter_all_choice, )]

    def get_tab_filter_count(self, choice, qs):
        return qs.filter(
            **{self.tab_filter: choice}).count()

    def get(self, request, *args, **kwargs):
        key = "{}_params".format(self.model.__name__)
        self.request.session[key] = self.request.GET
        if self.request.is_ajax():
            table = self.get_table(**self.get_table_kwargs())
            return JsonResponse({
                'table': table.as_html(request),
                'tab_counts': self.get_tab_counts() if self.tab_filter else None
            })
        else:
            return super().get(request, args, kwargs)


class SendSMSView(View):
    def post(self, request, *args, **kwargs):
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        message = self._strip_accents(message)

        if not phone or not message or not len(phone) == 9:
            return JsonResponse({'status': 'error', 'message': 'Coś poszło nie tak. Spróbuj ponownie.'}, status=400)

        client = SmsApiPlClient(access_token=settings.SMSAPI_TOKEN)
        if int(client.account.balance().pro_count) < settings.SMSAPI_LOW_BALANCE_COUNT:
            mail_admins('SMSAPI low balance', str(client.account.balance()))
        client.sms.send(to=phone, message=message)
        return JsonResponse({
            'status': 'success',
            'message': 'Wiadomość została wysłana.',
            }, status=200)

    def _strip_accents(self, text):
        return ''.join(c for c in unicodedata.normalize(
            'NFKD', text) if unicodedata.category(c) != 'Mn').replace('ł', 'l').replace('Ł', 'L')
