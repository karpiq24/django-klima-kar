from django import forms
from KlimaKar.widgets import PrettySelect


class IssueForm(forms.Form):
    BUG = 'bug'
    LABELS = [
        (BUG, 'Błąd'),
        ('enhancement', 'Usprawnienie'),
        ('new feature', 'Nowa funkcjonalność'),
    ]

    label = forms.ChoiceField(
        widget=PrettySelect,
        choices=LABELS,
        label='Typ zgłoszenia')
    title = forms.CharField(
        label='Tytuł')
    body = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Opis')
    secret = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        label='Poufne informacje',
        help_text='Na przykład hasła lub tokeny dostępu',
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['label'] = self.BUG
