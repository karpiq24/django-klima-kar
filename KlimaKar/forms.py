from django import forms
from django.utils.crypto import get_random_string

from KlimaKar.templatetags.slugify import slugify
from KlimaKar.widgets import PrettySelect


class ToggleInput(forms.CheckboxInput):
    template_name = "forms/toggle.html"


class IssueForm(forms.Form):
    BUG = "bug"
    LABELS = [
        (BUG, "Błąd"),
        ("enhancement", "Usprawnienie"),
        ("new feature", "Nowa funkcjonalność"),
    ]

    label = forms.ChoiceField(
        widget=PrettySelect, choices=LABELS, label="Typ zgłoszenia"
    )
    title = forms.CharField(label="Tytuł")
    body = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), label="Opis")
    secret = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2}),
        label="Poufne informacje",
        help_text="Na przykład hasła lub tokeny dostępu",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["label"] = self.BUG


class ScannerForm(forms.Form):
    FLATBEAD = "FLAT"
    ADF = "ADF"
    SCANNER_TYPE = [(FLATBEAD, "Bezpośrednie"), (ADF, "Podajnik dokumentów")]

    JPG = "JPG"
    PDF = "PDF"
    FILE_TYPES = [(JPG, "JPG"), (PDF, "PDF")]

    scanner_type = forms.ChoiceField(
        widget=PrettySelect,
        choices=SCANNER_TYPE,
        label="Typ skanowania",
        initial=FLATBEAD,
    )
    file_type = forms.ChoiceField(
        widget=PrettySelect, choices=FILE_TYPES, label="Format pliku", initial=JPG
    )
    trim_image = forms.BooleanField(
        widget=ToggleInput, label="Przytnij obraz", required=False
    )
    file_name = forms.CharField(label="Nazwa pliku")
    upload_key = forms.CharField(
        label="Klucz wysyłania plików",
        widget=forms.HiddenInput(),
        required=False,
        initial=get_random_string(length=32),
    )
    file_content_type = forms.CharField(widget=forms.HiddenInput())
    content_type = forms.CharField(widget=forms.HiddenInput())
    object_pk = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        if self.cleaned_data["scanner_type"] == self.ADF:
            self.cleaned_data["file_type"] = self.PDF
        self.cleaned_data["file_name"] = slugify(self.cleaned_data["file_name"])
        return self.cleaned_data

    def get_scan_command(self):
        data = self.cleaned_data
        command = f"scanimage --format tiff --resolution 150"
        if data["scanner_type"] == self.ADF:
            command = f"{command} --batch=document-p%d.tiff"
        return command

    def get_convert_command(self):
        data = self.cleaned_data
        command = f"convert document-p*.tiff -compress jpeg -quality 70"
        if data["trim_image"]:
            command = f"{command} -fuzz 35% -trim +repage"
        command = f"{command} {data['file_name']}.{data['file_type'].lower()}"
        return command

    def get_filename(self):
        return (
            f"{self.cleaned_data['file_name']}.{self.cleaned_data['file_type'].lower()}"
        )
