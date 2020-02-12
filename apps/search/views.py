from haystack.generic_views import SearchView
from django.template.loader import render_to_string
from django.http import JsonResponse


class AjaxSearchView(SearchView):
    def get(self, *args, **kwargs):
        response = super().get(self.request, *args, **kwargs)
        html = render_to_string(
            'search/search_results.html',
            response.context_data,
            request=self.request,
        )
        if self.request.is_ajax():
            return JsonResponse({'html': html})
        return response
