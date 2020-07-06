from dal import autocomplete
from django import forms
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe
from extra_views import InlineFormSet

from apps.wiki.models import Tag, Article, ExternalLink, ArticleFile


class ArticleModelForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        label="Tagi",
        queryset=Tag.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2Multiple(url="wiki:tags_autocomplete_create"),
    )
    upload_key = forms.CharField(
        label="Klucz wysyłania plików", widget=forms.HiddenInput(), required=False
    )
    main_image = forms.ModelChoiceField(
        queryset=ArticleFile.objects.all(), required=False, widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs.update({"placeholder": "Podaj tytuł"})
        self.fields["contents"].help_text = mark_safe(
            '<a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet" '
            'target="_blank">Składnia Markdown</a>'
        )
        self.fields["tags"].widget.attrs.update({"data-placeholder": "Wybierz tagi"})
        self.fields["upload_key"].initial = get_random_string(length=32)

    def save(self, commit=True):
        main_image = self.cleaned_data.get("main_image")
        if main_image and self.instance:
            self.instance.articlefile_set.all().update(is_main_image=False)
            main_image.is_main_image = True
            main_image.save()
        return super().save(commit=commit)

    class Meta:
        model = Article
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ExternalLinkModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"placeholder": "Podaj nazwę"})
        self.fields["url"].widget.attrs.update({"placeholder": "Podaj adres URL"})

    class Meta:
        model = ExternalLink
        fields = ["name", "url"]


class ExternalLinkInline(InlineFormSet):
    model = ExternalLink
    form_class = ExternalLinkModelForm
    factory_kwargs = {"extra": 10}
