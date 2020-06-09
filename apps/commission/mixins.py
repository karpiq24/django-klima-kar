from django.core.exceptions import PermissionDenied


class CommissionAccessMixin(object):
    def dispatch(self, *args, **kwargs):
        commission = self.get_object()
        if self.request.user.is_staff:
            return super().dispatch(*args, **kwargs)
        if not commission.is_editable:
            raise PermissionDenied
        return super().dispatch(*args, **kwargs)
