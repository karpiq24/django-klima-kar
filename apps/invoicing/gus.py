from gusregon import GUS as GUSREGON
from KlimaKar import settings


class GUSSession(object):
    session = None

    def _initialize_session(self):
        if not self.session:
            return self.reload_session()
        return True

    def reload_session(self):
        try:
            if settings.GUS_SANDBOX or not settings.GUS_KEY:
                self.session = GUSREGON(sandbox=True)
            else:
                self.session = GUSREGON(api_key=settings.GUS_KEY)
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
