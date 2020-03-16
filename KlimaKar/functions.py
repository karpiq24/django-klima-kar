import json

from urllib3.filepost import encode_multipart_formdata, choose_boundary
from urllib3.fields import RequestField


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
