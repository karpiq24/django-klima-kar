from django.template.loader import render_to_string
from django.http import HttpResponseForbidden, JsonResponse


class GroupAccessControlMixin(object):
    allowed_groups = []

    def dispatch(self, request, *args, **kwargs):
        if not self.allowed_groups or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        for group in self.allowed_groups:
            if request.user.groups.filter(name=group).exists():
                return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("Brak wymaganych uprawnień.")


class AjaxFormMixin(object):
    title = None
    url = None
    identifier = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['url'] = self.request.path
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
