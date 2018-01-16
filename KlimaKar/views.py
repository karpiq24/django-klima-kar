import six

from django.views.generic import TemplateView, CreateView
from django.http import JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from dal import autocomplete

from KlimaKar.mixins import AjaxableResponseMixin


class HomeView(TemplateView):
    template_name = "stats/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        charts = []
        charts.append({
            'title': 'Wartość zakupów w miesiącach',
            'url': reverse('stats:invoices_value_monthly')
        })
        charts.append({
            'title': 'Wartosć zakupów w latach',
            'url': reverse('stats:invoices_value_yearly')
        })
        charts.append({
            'title': 'Wartość zakupów u dostawców od początku',
            'url': reverse('stats:supplier_all_invoices_value')
        })
        charts.append({
            'title': 'Wartość zakupów u dostawców w ostatnim roku',
            'url': reverse('stats:supplier_last_year_invoices_value')
        })
        charts.append({
            'title': 'Najczęściej kupowane towary od początku',
            'url': reverse('stats:ware_purchase_quantity')
        })
        charts.append({
            'title': 'Najczęściej kupowane towary w ostatnim roku',
            'url': reverse('stats:ware_purchase_quantity_last_year')
        })
        context['charts'] = charts
        return context


class AjaxCreateView(AjaxableResponseMixin, CreateView):
    model = None
    form_class = None
    title = None
    url = None
    identifier = 1

    def get_context_data(self, **kwargs):
        context = super(AjaxCreateView, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['url'] = reverse(self.url)
        context['identifier'] = self.identifier
        return context

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            super(AjaxCreateView, self).get(self.request)
            html_form = render_to_string(
                'modal_form.html',
                self.get_context_data(),
                request=self.request,
            )
            return JsonResponse({'html_form': html_form})
        return JsonResponse({'error': "Not allowed"})

    def get_success_url(self, **kwargs):
        return None


class CustomSelect2QuerySetView(autocomplete.Select2QuerySetView):
    def get_create_option(self, context, q):
        create_option = []
        display_create_option = False
        if self.create_field and q:
            page_obj = context.get('page_obj', None)
            if ((page_obj is None or page_obj.number == 1)
                    and not self.get_queryset().filter(**{self.create_field: q}).exists()):
                display_create_option = True

        if display_create_option:
            create_option = [{
                'id': q,
                'text': ('Dodaj "%(new_value)s"') % {'new_value': q},
                'create_id': True,
            }]
        return create_option

    def post(self, request):
        if not self.create_field:
            raise ImproperlyConfigured('Missing "create_field"')

        text = request.POST.get('text', None)

        if text is None:
            return HttpResponseBadRequest()

        result = self.create_object(text)

        return JsonResponse({
            'id': result.pk,
            'text': six.text_type(result),
        })
