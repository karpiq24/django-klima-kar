from django.http import JsonResponse, HttpResponseForbidden


class AjaxableResponseMixin(object):
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class GroupAccessControlMixin(object):
    allowed_groups = []

    def dispatch(self, request, *args, **kwargs):
        if not self.allowed_groups or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        for group in self.allowed_groups:
            if request.user.groups.filter(name=group).exists():
                return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("Brak wymaganych uprawnień.")
