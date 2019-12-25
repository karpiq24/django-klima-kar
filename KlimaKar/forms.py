import ipaddress
import base64
import django_rq

from ipware import get_client_ip
from pyotp import TOTP

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm

from KlimaKar.widgets import PrettySelect
from KlimaKar.functions import send_token_email


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
    token = forms.CharField(
        label="Token",
        widget=forms.HiddenInput(),
        required=False
    )

    def clean(self):
        self.cleaned_data = super().clean()
        if not self.get_user() or not self.get_user().email:
            return self.cleaned_data
        if not self.cleaned_data['token']:
            django_rq.enqueue(send_token_email, self.get_user(), self.get_token())
            self.add_error('token', 'token_required')
            return self.cleaned_data
        if not self.validate_token(self.cleaned_data['token']):
            self.cleaned_data['token'] = ''
            raise forms.ValidationError(
                    'Nieprawidłowy token autoryzacyjny.',
                    code='token_invalid',
                )
        return self.cleaned_data

    def get_token(self):
        return self._get_totp().now()

    def validate_token(self, token):
        return self._get_totp().verify(token)

    def _get_totp(self):
        key = f'{self.get_user().email}{settings.SECRET_SALT}'
        key = base64.b32encode(bytearray(key, 'ascii')).decode('utf-8')
        return TOTP(key, interval=settings.TOKEN_VALID_TIME)

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        client_ip, is_routable = get_client_ip(self.request)
        if not ipaddress.ip_address(client_ip).is_private:
            if not user.is_superuser and not user.groups.filter(name='boss').exists():
                raise forms.ValidationError(
                    'Niedozwolony zdalny dostęp.',
                    code='remote_disallowed',
                )

    def get_invalid_login_error(self):
        self.add_error('username', '')
        self.add_error('password', '')
        return super().get_invalid_login_error()
