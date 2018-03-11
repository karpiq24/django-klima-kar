from django.http import HttpResponseForbidden


class GroupAccessControlMixin(object):
    allowed_groups = []

    def dispatch(self, request, *args, **kwargs):
        if not self.allowed_groups or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        for group in self.allowed_groups:
            if request.user.groups.filter(name=group).exists():
                return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("Brak wymaganych uprawnień.")
