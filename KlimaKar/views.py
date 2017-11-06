from django.views.generic import TemplateView, CreateView
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse

from KlimaKar.mixins import AjaxableResponseMixin


class HomeView(TemplateView):
    template_name = "base.html"


class AjaxCreateView(AjaxableResponseMixin, CreateView):
    model = None
    form_class = None
    title = None
    url = None

    def get_context_data(self, **kwargs):
        context = super(AjaxCreateView, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['url'] = reverse(self.url)
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
