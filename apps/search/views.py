from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.generic import ListView

from KlimaKar.functions import strip_accents
from apps.search.forms import SearchForm
from apps.search.models import SearchDocument


class AjaxSearchView(ListView):
    paginate_by = 10
    model = SearchDocument
    template_name = "search/search.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["form"] = SearchForm()
        context["query"] = self.request.GET.get("q")
        return context

    def get_queryset(self):
        if not self.request.GET.get("q"):
            return SearchDocument.objects.none()
        qs = SearchDocument.objects.all()
        models = self.request.GET.getlist("models", [])
        if models:
            model_names = [m.split(".")[1] for m in models]
            qs = qs.filter(content_type__model__in=model_names)
        words = [
            word.strip()
            for word in strip_accents(self.request.GET["q"]).split(" ")
            if word.strip()
        ]
        for word in words:
            qs = qs.filter(text_search__icontains=word)
        return qs

    def get(self, *args, **kwargs):
        response = super().get(self.request, *args, **kwargs)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "html": render_to_string(
                        "search/search_results.html",
                        response.context_data,
                        request=self.request,
                    )
                }
            )
        return response
