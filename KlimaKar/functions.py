import os
import json

from urllib3.filepost import encode_multipart_formdata, choose_boundary
from urllib3.fields import RequestField

from django.core.mail import mail_managers
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError


def encode_multipart_related(fields, boundary=None):
    if boundary is None:
        boundary = choose_boundary()
    body, _ = encode_multipart_formdata(fields, boundary)
    content_type = str('multipart/related; boundary=%s' % boundary)
    return body, content_type


def encode_media_related(metadata, media=None):
    rf1 = RequestField(
        name='placeholder',
        data=json.dumps(metadata),
        headers={'Content-Type': 'application/json; charset=UTF-8'},
    )
    if media:
        rf2 = RequestField(
            name='placeholder2',
            data=media
        )
        return encode_multipart_related([rf1, rf2])
    return encode_multipart_related([rf1])


def report_user_login(user_session):
    country = '-'
    if os.path.exists(os.path.join(settings.GEOIP_PATH, settings.GEOIP_COUNTRY)):
        geoip = GeoIP2()
        try:
            country = geoip.country(user_session.client_ip)['country_name']
        except AddressNotFoundError:
            pass

    mail_managers(
        'Nowe logowanie do Klima-Kar',
        (
            f'Użytkownik: {user_session.user}\n'
            f'Data logowania: {user_session.created}\n'
            f'Adres IP: {user_session.client_ip}\n'
            f'Kraj: {country}'
        )
    )
