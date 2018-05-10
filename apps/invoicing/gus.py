from gusregon import GUS
from KlimaKar import settings


def reload_session():
    if settings.GUS_SANDBOX or not settings.GUS_KEY:
        gus_session = GUS(sandbox=True)
    else:
        gus_session = GUS(api_key=settings.GUS_KEY)
    return gus_session


def get_gus_address(nip):
    global gus_session
    result = gus_session.get_address(nip=nip)
    if result:
        return result
    else:
        reload_session()
    return gus_session.get_address(nip=nip)


gus_session = reload_session()
