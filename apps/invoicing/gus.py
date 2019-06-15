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


def get_gus_pkd(nip):
    global gus_session
    result = gus_session.get_pkd(nip=nip)
    if result:
        return result
    else:
        reload_session()
    return gus_session.get_pkd(nip=nip)


def get_gus_data(nip):
    global gus_session
    result = gus_session.search(nip=nip)
    if result:
        return result
    else:
        reload_session()
    return gus_session.search(nip=nip)


gus_session = reload_session()
