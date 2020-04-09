from django import forms

from apps.search.models import SearchDocument


class SearchForm(forms.Form):
    models = forms.MultipleChoiceField(
        choices=[
            (
                f"{model._meta.app_label}.{model._meta.model_name}",
                model._meta.verbose_name_plural,
            )
            for model in SearchDocument.indexed_models
        ],
        widget=forms.CheckboxSelectMultiple,
    )
