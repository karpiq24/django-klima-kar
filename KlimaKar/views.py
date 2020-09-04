from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ImproperlyConfigured

from django_tables2 import SingleTableView
from dal import autocomplete
from github import Github

from KlimaKar import settings
from KlimaKar.forms import IssueForm
from KlimaKar.email import get_email_message
from apps.commission.models import Commission
from apps.invoicing.models import SaleInvoice
from apps.warehouse.models import Invoice
from apps.wiki.models import Article


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["commissions"] = Commission.objects.filter(status=Commission.OPEN)
        context["purchase_invoices"] = Invoice.objects.order_by("-created_date")[:10]
        context["sale_invoices"] = SaleInvoice.objects.order_by("-created_date")[:10]
        context["articles"] = Article.objects.order_by("-create_time")[:10]
        return context


class SendIssueView(View):
    def post(self, request, *args, **kwargs):
        issue_form = IssueForm(data=request.POST)
        if issue_form.is_valid():
            data = issue_form.cleaned_data
            g = Github(settings.GITHUB_TOKEN)
            repo = g.get_repo(settings.GITHUB_REPOSITORY)
            repo.create_issue(
                title=data["title"],
                body=data["body"],
                labels=[data["label"]],
                assignee=settings.GITHUB_USERNAME,
            )

            if settings.ADMINS:
                get_email_message(
                    subject="Nowe zgłoszenie: {}".format(data["title"]),
                    body="{}\n\n{}".format(data["body"], data.get("secret")),
                    to=[admin[1] for admin in settings.ADMINS],
                ).send(fail_silently=True)
            return JsonResponse(
                {"status": "success", "message": "Zgłoszenie zostało wysłane"},
                status=200,
            )
        return JsonResponse(
            {"status": "error", "message": "Coś poszło nie tak. Spróbuj ponownie."},
            status=400,
        )


class CustomSelect2QuerySetView(autocomplete.Select2QuerySetView):
    modal_create = False
    always_show_create = False
    create_empty_label = "Nowy obiekt"

    def get_create_option(self, context, q):
        create_option = []
        display_create_option = False
        if self.always_show_create:
            display_create_option = True
        elif self.modal_create and q:
            display_create_option = True
        elif self.create_field and q:
            page_obj = context.get("page_obj", None)
            if (
                page_obj is None or page_obj.number == 1
            ) and not self.get_queryset().filter(**{self.create_field: q}).exists():
                display_create_option = True

        if display_create_option:
            create_option = [
                {
                    "id": q or self.create_empty_label,
                    "text": ('Dodaj "%(new_value)s"')
                    % {"new_value": q or self.create_empty_label},
                    "create_id": True,
                }
            ]
        return create_option

    def post(self, request):
        if self.modal_create:
            return JsonResponse({"status": "disabled"})
        if not self.create_field:
            raise ImproperlyConfigured('Missing "create_field"')

        text = request.POST.get("text", None)

        if text is None:
            return HttpResponseBadRequest()

        result = self.create_object(text)

        return JsonResponse({"id": result.pk, "text": str(result)})

    def get_results(self, context):
        return [
            dict(
                {
                    "id": self.get_result_value(result),
                    "text": self.get_result_label(result),
                    "selected_text": self.get_selected_result_label(result),
                },
                **self.extend_result_data(result)
            )
            for result in context["object_list"]
        ]

    def extend_result_data(self, data):
        return {}


class FilteredSingleTableView(SingleTableView):
    filter_class = None
    tab_filter = None
    tab_filter_default = None
    tab_filter_choices = None
    tab_filter_all_choice = ("__ALL__", "Wszystkie")

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
        context["filter"] = self.filter
        if self.tab_filter:
            context["current_tab_filter"] = self.request.GET.get(
                self.tab_filter, self.tab_filter_default
            )
            context["{}_data".format(self.tab_filter)] = self.get_tab_filter_choices()
        return context

    def get_tab_filter_choices(self):
        return self.tab_filter_choices + [(*self.tab_filter_all_choice,)]

    def get_tab_filter_count(self, choice, qs):
        return qs.filter(**{self.tab_filter: choice}).count()

    def get(self, request, *args, **kwargs):
        key = "{}_params".format(self.model.__name__)
        export = self.request.GET.get("_export")
        if export:
            self.request.GET = self.request.GET.copy()
            self.request.GET.update(self.request.session[key])
        else:
            self.request.session[key] = self.request.GET
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            table = self.get_table(**self.get_table_kwargs())
            return JsonResponse(
                {
                    "table": table.as_html(request),
                    "tab_counts": self.get_tab_counts() if self.tab_filter else None,
                }
            )
        else:
            return super().get(request, args, kwargs)


class ChangeLogView(TemplateView):
    template_name = "changelog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with open("CHANGELOG.md") as f:
            context["changelog"] = f.read()
        return context
