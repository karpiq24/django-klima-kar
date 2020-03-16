import os

from django.urls import reverse

from KlimaKar.forms import IssueForm
from KlimaKar import settings


def issue_form(request):
    return {
        "issue_form": IssueForm(),
        "issue_submit_url": reverse("send_issue"),
        "issue_list_url": os.path.join(
            "https://github.com", settings.GITHUB_REPOSITORY, "issues"
        ),
    }


def debug(request):
    return {"DEBUG": settings.DEBUG}
