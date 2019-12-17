from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count, F, FloatField
from django.db.models.functions import ExtractYear, ExtractMonth

from apps.stats.dictionaries import MONTHS, COLORS, DAYS
from apps.stats.models import Round


class ChartDataMixin(object):
    def get_response_data_template(self, chart_type='line', legend_display=True, values_prefix='', values_appendix=''):
        response_data = {
            'type': chart_type,
            'data': {
                'labels': [],
                'datasets': []
            },
            'options': {
                'legend': {
                    'display': legend_display
                }
            },
            'custom': {
                'values_prefix': values_prefix,
                'values_appendix': values_appendix
            }
        }
        return response_data

    def get_dataset(self, data, colors, label='', borderWidth=1, borderColor='#ffffff', fill=True, hidden=False):
        dataset = {
            'label': label,
            'fill': fill,
            'data': data,
            'borderWidth': borderWidth,
            'backgroundColor': colors,
            'borderColor': borderColor,
            'hidden': hidden
        }
        return dataset


class BigChartHistoryMixin(ChartDataMixin, View):
    how_many_shown = 4
    model = None
    date_field = None
    price_field = None
    quantity_field = None
    values_appendix = ' zł'

    def get(self, *args, **kwargs):
        self.date_option = self.request.GET.get(
            'date_select', self._get_default_date_option(**kwargs))
        self.metric = self.request.GET.get('custom_select', 'Sum')
        self.objects = self.model.objects.all()
        self._filter_objects(**kwargs)
        self._generate_response_data()
        return JsonResponse(self.response_data)

    def _filter_objects(self, **kwargs):
        pass

    def _get_default_date_option(self, **kwargs):
        return 'week'

    def _annotate(self, qs):
        annotate_functions = {
            'Sum': self._annotate_sum,
            'Avg': self._annotate_avg,
            'Count': self._annotate_count,
        }
        return annotate_functions[self.metric](qs)

    def _annotate_sum(self, qs):
        return qs.annotate(total=Sum(
            F(self.price_field) * F(self.quantity_field),
            output_field=FloatField()))

    def _annotate_avg(self, qs):
        return qs.annotate(total=Round(Avg(
            F(self.price_field) * F(self.quantity_field),
            output_field=FloatField())))

    def _annotate_count(self, qs):
        self.response_data['custom']['values_appendix'] = ''
        return qs.annotate(total=Count('id'))

    def _generate_response_data(self):
        self.response_data = self.get_response_data_template(
            legend_display=False, values_appendix=self.values_appendix)
        data_functions = {
            'week': self._get_week,
            'month': self._get_month,
            'year': self._get_year,
            'all_monthly': self._get_all_monthly,
            'all_yearly': self._get_all_yearly
        }
        data_functions[self.date_option]()

    def _get_date_filter_kwargs(self, date):
        return {
            '{}__gte'.format(self.date_field): date
        }

    def _get_week(self):
        date = datetime.today() - relativedelta(days=6)
        self.objects = self.objects.filter(**self._get_date_filter_kwargs(date))
        self.objects = self.objects.values(self.date_field)
        self.objects = self._annotate(self.objects)
        self.objects = self.objects.values_list('total', self.date_field).order_by(self.date_field)
        values = list(self.objects.values_list('total', flat=True))
        days_between = (datetime.today() - date).days
        for i in range(days_between + 1):
            x = date + relativedelta(days=i)
            if x.date() not in self.objects.values_list(self.date_field, flat=True):
                values.insert(i, 0)

        self.response_data['data']['labels'] = [DAYS[(date + relativedelta(days=i)).weekday()]
                                                for i in range(days_between + 1)]
        self.response_data['data']['datasets'].append(self.get_dataset(values, COLORS[0]))

    def _get_month(self):
        date = datetime.today() - relativedelta(months=1)
        self.objects = self.objects.filter(**self._get_date_filter_kwargs(date))
        self.objects = self.objects.values(self.date_field)
        self.objects = self._annotate(self.objects)
        self.objects = self.objects.values_list('total', self.date_field).order_by(self.date_field)
        values = list(self.objects.values_list('total', flat=True))
        days_between = (date.today() - date).days
        for i in range(days_between + 1):
            x = date + relativedelta(days=i)
            if x.date() not in self.objects.values_list(self.date_field, flat=True):
                values.insert(i, 0)

        self.response_data['data']['labels'] = [(date + relativedelta(days=i)).strftime('%d/%m')
                                                for i in range(days_between + 1)]
        self.response_data['data']['datasets'].append(self.get_dataset(
            values, COLORS[0]))

    def _get_year(self):
        date = (datetime.today() - relativedelta(years=1, months=-1)).replace(day=1)
        self.objects = self.objects.filter(**self._get_date_filter_kwargs(date))
        self.objects = self.objects.annotate(
                month=ExtractMonth(self.date_field), year=ExtractYear(self.date_field)).values('year', 'month')
        self.objects = self._annotate(self.objects)
        self.objects = self.objects.values_list('year', 'month', 'total').order_by('year', 'month')
        values = list(self.objects.values_list('total', flat=True))
        months = list(self.objects.values_list('month', flat=True))
        self.response_data['data']['labels'] = [MONTHS[i - 1] for i in months]
        self.response_data['data']['datasets'].append(self.get_dataset(
            values, COLORS[0]))

    def _get_all_monthly(self):
        years = self.objects.annotate(year=ExtractYear(self.date_field)).values_list(
                'year', flat=True).distinct().order_by('year')
        self.response_data['data']['labels'] = MONTHS
        self.response_data['options']['legend']['display'] = True

        colors = COLORS[len(years)-1::-1]
        for i, year in enumerate(years):
            year_objects = self.objects.filter(**{'{}__year'.format(self.date_field): year})
            year_objects = year_objects.annotate(month=ExtractMonth(self.date_field)).values('month')
            year_objects = self._annotate(year_objects)
            year_objects = year_objects.values_list('month', 'total').order_by('month')
            values = list(year_objects.values_list('total', flat=True))
            values = [val for val in values if val]
            for j in range(1, 13):
                if j not in year_objects.values_list('month', flat=True):
                    values.insert(j - 1, 0)
            hidden = False
            if i < len(years) - self.how_many_shown:
                hidden = True
            if sum(values) > 0:
                self.response_data['data']['datasets'].append(self.get_dataset(
                    values, colors[i], label=year, fill=False, borderColor=colors[i], hidden=hidden))

    def _get_all_yearly(self):
        self.objects = self.objects.annotate(year=ExtractYear(self.date_field)).values('year')
        self.objects = self._annotate(self.objects)
        self.objects = self.objects.values_list('year', 'total').exclude(total=0).order_by('year')

        self.response_data['data']['labels'] = list(self.objects.values_list('year', flat=True))
        self.response_data['data']['datasets'].append(self.get_dataset(
            list(self.objects.values_list('total', flat=True)),
            COLORS[0]))
