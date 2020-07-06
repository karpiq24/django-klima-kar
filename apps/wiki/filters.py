import django_filters
from dal import autocomplete
from django import forms

from apps.wiki.models import Article, Tag


class ArticleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())
    contents = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput()
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url="wiki:tags_autocomplete"),
    )

    class Meta:
        model = Article
        fields = ["title", "contents", "tags"]
