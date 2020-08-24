from gusregon import GUS as GUSREGON
from gusregon.gus import ENDPOINT_SANDBOX, WSDL
from requests import Session
from zeep import Client, Transport

from KlimaKar import settings


class GUSREGONTimeout(GUSREGON):
    def __init__(self, api_key=None, sandbox=False):
        if not any([api_key, sandbox]):
            raise AttributeError("Api key is required.")
        self.api_key = api_key
        self.sandbox = sandbox
        if sandbox:
            self.api_key = api_key or "abcde12345abcde12345"
            self.endpoint = ENDPOINT_SANDBOX
        transport = Transport(session=Session(), timeout=5)
        transport.session.headers = self.headers
        client = Client(WSDL, transport=transport)
        self.service = client.create_service("{http://tempuri.org/}e3", self.endpoint)
        self.headers.update({"sid": self._service("Zaloguj", self.api_key)})


class GUSSession(object):
    session = None

    def _initialize_session(self):
        if not self.session:
            return self.reload_session()
        return True

    def reload_session(self):
        try:
            if settings.GUS_SANDBOX or not settings.GUS_KEY:
                self.session = GUSREGONTimeout(sandbox=True)
            else:
                self.session = GUSREGONTimeout(api_key=settings.GUS_KEY)
            return True
        except Exception:
            return False

    def gus_initialize(func):
        def wrapper(self, *args, **kwargs):
            if not self._initialize_session():
                return None
            try:
                result = func(self, *args, **kwargs)
            except Exception:
                return None
            if not result:
                if not self.reload_session():
                    return None
                try:
                    result = func(self, *args, **kwargs)
                except Exception:
                    return None
            return result

        return wrapper

    @gus_initialize
    def get_gus_address(self, nip):
        return self.session.get_address(nip=nip)

    @gus_initialize
    def get_gus_pkd(self, nip):
        return self.session.get_pkd(nip=nip)

    @gus_initialize
    def get_gus_data(self, nip):
        return self.session.search(nip=nip)


GUS = GUSSession()

if not settings.DEBUG:
    GUS.reload_session()
