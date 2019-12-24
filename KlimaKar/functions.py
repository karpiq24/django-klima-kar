import json

from urllib3.filepost import encode_multipart_formdata, choose_boundary
from urllib3.fields import RequestField


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


def send_token_email(user, token):
    from KlimaKar.email import get_email_message

    body = (
        f'Witaj {user.username}!\n\n'
        f'Nastąpiła próba logowania na Twoje konto, które jest zabezpieczone dwuskładnikowym uwierzytelnianiem.\n\n'
        f'Twój token autoryzacyjny to: {token}'
    )
    email = get_email_message(
        subject='Logowanie do Klima-Kar - token autoryzacyjny',
        body=body,
        to=[user.email]
    )
    email.send(fail_silently=True)
