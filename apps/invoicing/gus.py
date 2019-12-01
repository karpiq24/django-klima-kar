from gusregon import GUS as GUSREGON
from KlimaKar import settings


class GUSSession(object):
    session = None

    def _initialize_session(self):
        if not self.session:
            self.reload_session()

    def reload_session(self):
        if settings.GUS_SANDBOX or not settings.GUS_KEY:
            self.session = GUSREGON(sandbox=True)
        else:
            self.session = GUSREGON(api_key=settings.GUS_KEY)

    def get_gus_address(self, nip):
        self._initialize_session()
        result = self.session.get_address(nip=nip)
        if result:
            return result
        else:
            self.reload_session()
        return self.session.get_address(nip=nip)

    def get_gus_pkd(self, nip):
        self._initialize_session()
        result = self.session.get_pkd(nip=nip)
        if result:
            return result
        else:
            self.reload_session()
        return self.session.get_pkd(nip=nip)

    def get_gus_data(self, nip):
        self._initialize_session()
        result = self.session.search(nip=nip)
        if result:
            return result
        else:
            self.reload_session()
        return self.session.search(nip=nip)


GUS = GUSSession()

if not settings.DEBUG:
    GUS.reload_session()
