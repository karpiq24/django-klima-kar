from haystack.forms import SearchForm


class HighlightedSearchForm(SearchForm):
    def search(self):
        sqs = super().search()
        kwargs = {
            'hl.simple.pre': '<span class="highlighted">',
            'hl.simple.post': '</span>'
        }
        return sqs.highlight(**kwargs)
