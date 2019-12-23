import ipaddress

from ipware import get_client_ip

from django import forms
from django.contrib.auth.forms import AuthenticationForm

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


class KlimaKarAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        client_ip, is_routable = get_client_ip(self.request)
        if not ipaddress.ip_address(client_ip).is_private:
            if not user.is_superuser and not user.groups.filter(name='boss').exists():
                raise forms.ValidationError(
                    'Niedozwolony zdalny dostęp.',
                    code='remote_disallowed',
                )
