from django.core.exceptions import PermissionDenied


class SaleInvoiceAccessMixin(object):
    def dispatch(self, *args, **kwargs):
        invoice = self.get_object()
        if self.request.user.is_staff:
            return super().dispatch(*args, **kwargs)
        if not invoice.is_editable:
            raise PermissionDenied
        return super().dispatch(*args, **kwargs)
