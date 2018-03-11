import six

from django.views.generic import TemplateView, CreateView
from django.http import JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from django_tables2 import SingleTableView
from dal import autocomplete


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


class AjaxCreateView(CreateView):
    model = None
    form_class = None
    title = None
    url = None
    identifier = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['url'] = reverse(self.url)
        context['identifier'] = self.identifier
        return context

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            self.initial = self.request.GET.dict()
            super().get(self.request)
            html_form = render_to_string(
                'forms/modal_form.html',
                self.get_context_data(),
                request=self.request,
            )
            return JsonResponse({'html_form': html_form})
        return JsonResponse({'error': "Not allowed"})

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            html_form = render_to_string(
                'forms/modal_form.html',
                self.get_context_data(),
                request=self.request,
            )
            return JsonResponse({'html_form': html_form}, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
                'text': str(self.object)
            }
            return JsonResponse(data)
        else:
            return response

    def get_success_url(self, **kwargs):
        return None


class CustomSelect2QuerySetView(autocomplete.Select2QuerySetView):
    modal_create = False

    def get_create_option(self, context, q):
        create_option = []
        display_create_option = False
        if self.modal_create and q:
            display_create_option = True
        elif self.create_field and q:
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
            'text': six.text_type(result),
        })


class FilteredSingleTableView(SingleTableView):
    filter_class = None

    def get_table_data(self):
        data = super(FilteredSingleTableView, self).get_table_data()
        self.filter = self.filter_class(self.request.GET, queryset=data)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super(FilteredSingleTableView, self).get_context_data(**kwargs)
        context['filter'] = self.filter
        key = "{}_params".format(self.filter_class)
        self.request.session[key] = self.request.GET
        return context
