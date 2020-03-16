import ipaddress

from ipware import get_client_ip

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm

from apps.accounts.functions import validate_auth_token


class KlimaKarAuthenticationForm(AuthenticationForm):
    token = forms.CharField(
        label="Token",
        widget=forms.HiddenInput(),
        required=False
    )

    def clean(self):
        self.cleaned_data = super().clean()
        if not settings.TWO_STEP_LOGIN_ENABLED:
            return self.cleaned_data
        if not self.get_user() or not self.get_user().email:
            return self.cleaned_data
        if not self.cleaned_data['token']:
            raise forms.ValidationError(
                'Token autoryzacyjny jest wymagany.',
                code='token_required',
            )
        if not validate_auth_token(self.get_user(), self.cleaned_data['token']):
            self.cleaned_data['token'] = ''
            raise forms.ValidationError(
                'Nieprawidłowy token autoryzacyjny.',
                code='token_invalid',
            )
        return self.cleaned_data

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
