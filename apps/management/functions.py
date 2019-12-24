import os

from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError

from KlimaKar.email import mail_managers


def report_user_login(user_session):
    country = '-'
    if os.path.exists(os.path.join(settings.GEOIP_PATH, settings.GEOIP_COUNTRY)):
        geoip = GeoIP2()
        try:
            country = geoip.country(user_session.client_ip)['country_name']
            user_session.country = country
            user_session.save()
        except AddressNotFoundError:
            pass

    mail_managers(
        'Nowe logowanie do Klima-Kar',
        (
            f'Użytkownik: {user_session.user}\n'
            f'Data logowania: {user_session.created}\n'
            f'Adres IP: {user_session.client_ip}\n'
            f'Kraj: {user_session.country}\n'
            f'User agent: {user_session.user_agent}'
        )
    )
