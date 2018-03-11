from gusregon import GUS
from KlimaKar import settings


if settings.GUS_SANDBOX or not settings.GUS_KEY:
    gus_session = GUS(sandbox=True)
    print("GUS | SANDBOX")
else:
    gus_session = GUS(api_key=settings.GUS_KEY)
    print("GUS | PRODUCTION")
