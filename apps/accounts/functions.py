import os
import base64

from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2

from geoip2.errors import AddressNotFoundError
from pyotp import TOTP

from KlimaKar.email import mail_managers, get_email_message


def report_user_login(user_session):
    country = "-"
    if os.path.exists(os.path.join(settings.GEOIP_PATH, settings.GEOIP_COUNTRY)):
        geoip = GeoIP2()
        try:
            country = geoip.country(user_session.client_ip)["country_name"]
            user_session.country = country
            user_session.save()
        except AddressNotFoundError:
            pass

    mail_managers(
        "Nowe logowanie do Klima-Kar",
        (
            f"Użytkownik: {user_session.user}\n"
            f"Data logowania: {user_session.created}\n"
            f"Adres IP: {user_session.client_ip}\n"
            f"Kraj: {user_session.country}\n"
            f"User agent: {user_session.user_agent}"
        ),
    )


def send_token_email(user):
    token = get_auth_token(user)
    body = (
        f"Witaj {user.username}!\n\n"
        f"Nastąpiła próba logowania na Twoje konto, które jest zabezpieczone dwuskładnikowym uwierzytelnianiem.\n\n"
        f"Twój token autoryzacyjny to: {token}\n\n"
        f"Toen jest ważny przez 10 minut."
    )
    email = get_email_message(
        subject="Logowanie do Klima-Kar - token autoryzacyjny",
        body=body,
        to=[user.email],
    )
    email.send(fail_silently=True)


def get_auth_token(user):
    key = f"{user.email}{settings.SECRET_SALT}"
    key = base64.b32encode(bytearray(key, "ascii")).decode("utf-8")
    totp = TOTP(key, interval=settings.TOKEN_VALID_TIME)
    return totp.now()


def validate_auth_token(user, token):
    key = f"{user.email}{settings.SECRET_SALT}"
    key = base64.b32encode(bytearray(key, "ascii")).decode("utf-8")
    totp = TOTP(key, interval=settings.TOKEN_VALID_TIME)
    return totp.verify(token)
