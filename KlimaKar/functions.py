import json
import unicodedata
import requests

from urllib3.filepost import encode_multipart_formdata, choose_boundary
from urllib3.fields import RequestField
from smsapi.client import SmsApiPlClient
from bs4 import BeautifulSoup

from django.conf import settings


def encode_multipart_related(fields, boundary=None):
    if boundary is None:
        boundary = choose_boundary()
    body, _ = encode_multipart_formdata(fields, boundary)
    content_type = str("multipart/related; boundary=%s" % boundary)
    return body, content_type


def encode_media_related(metadata, media=None):
    rf1 = RequestField(
        name="placeholder",
        data=json.dumps(metadata),
        headers={"Content-Type": "application/json; charset=UTF-8"},
    )
    if media:
        rf2 = RequestField(name="placeholder2", data=media)
        return encode_multipart_related([rf1, rf2])
    return encode_multipart_related([rf1])


def strip_accents(text):
    return (
        "".join(
            c
            for c in unicodedata.normalize("NFKD", text)
            if unicodedata.category(c) != "Mn"
        )
        .replace("ł", "l")
        .replace("Ł", "L")
        .replace("'", "")
    )


def send_sms(phone, message):
    from KlimaKar.email import mail_admins

    message = strip_accents(message)
    if not phone or not message or not len(phone) == 9:
        return False

    client = SmsApiPlClient(access_token=settings.SMSAPI_TOKEN)
    if int(client.account.balance().pro_count) < settings.SMSAPI_LOW_BALANCE_COUNT:
        mail_admins("SMSAPI low balance", str(client.account.balance()))
    client.sms.send(to=phone, message=message)
    return True


def get_garbage_collection_dates():
    data = {
        "action": "waste_disposal_form_get_schedule",
        "id_numeru": settings.EKOSYSTEM_NUMBER,
    }
    r = requests.post(settings.EKOSYSTEM_ENDPOINT, data)
    rows = BeautifulSoup(r.json()["wiadomoscRWD"], "html5lib").find_all("tr")
    headers = [
        header.text.strip().capitalize() for header in rows.pop(0).find_all("td")
    ]
    data = {"headers": headers, "rows": []}

    for row in rows:
        data["rows"].append([value.text.strip() for value in row.find_all("td")])
    return data
