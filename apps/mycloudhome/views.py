import json
import os
from datetime import datetime
from io import BytesIO

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.views import View
from django.views.decorators.cache import cache_control

from KlimaKar.templatetags.slugify import slugify
from apps.mycloudhome.utils import get_temporary_files


class FileDownloadView(View):
    model = None
    file_model = None

    @cache_control(public=True, max_age=31536000)
    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(self.model, pk=kwargs.get("pk"))
        file_object = get_object_or_404(
            self.file_model,
            **{"file_name": kwargs.get("name"), self.file_model.PARENT_FIELD: obj}
        )
        response = FileResponse(
            BytesIO(file_object.file_contents), content_type=file_object.mime_type,
        )
        return response


class TemporaryFileUploadView(View):
    def post(self, request, *args, **kwargs):
        upload_key = request.POST.get("key")
        if not upload_key:
            return JsonResponse(
                {"status": "error", "message": "Coś poszło nie tak. Spróbuj ponownie."},
                status=400,
            )

        directory = os.path.join(settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, "timestamp"), "w") as timefile:
            timefile.write(str(datetime.now()))
        for key, file_obj in request.FILES.items():
            with open(
                os.path.join(directory, "{}.meta".format(file_obj.name)), "w"
            ) as metafile:
                metafile.write(
                    json.dumps(
                        {
                            "name": file_obj.name,
                            "size": file_obj.size,
                            "type": file_obj.content_type,
                        }
                    )
                )
            with default_storage.open(
                "{}/{}".format(directory, key), "wb+"
            ) as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
        return JsonResponse(
            {
                "status": "success",
                "message": "Pliki zostały zapisane.",
                "files": get_temporary_files(upload_key),
            },
            status=200,
        )


class CheckUploadFinishedView(View):
    model = None
    file_download_url = None

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(self.model, pk=request.GET.get("pk"))
        if obj.upload:
            return JsonResponse({"status": "progress"}, status=200)
        return JsonResponse(
            {
                "status": "success",
                "files": [
                    {
                        "name": f.file_name,
                        "size": filesizeformat(f.file_size),
                        "url": reverse(
                            self.file_download_url,
                            kwargs={
                                "pk": obj.pk,
                                "slug": slugify(obj),
                                "name": f.file_name,
                            },
                        ),
                    }
                    for f in obj.get_files()
                ],
            },
            status=200,
        )


class DeleteTemporaryFile(View):
    def post(self, request, *args, **kwargs):
        upload_key = request.POST.get("key")
        fname = request.POST.get("file")
        if not upload_key or not fname:
            return JsonResponse(
                {"status": "error", "message": "Coś poszło nie tak. Spróbuj ponownie."},
                status=400,
            )
        fpath = os.path.join(settings.TEMPORARY_UPLOAD_DIRECTORY, upload_key, fname)
        if os.path.exists(fpath):
            os.remove(fpath)
        metapath = "{}.meta".format(fpath)
        if os.path.exists(metapath):
            os.remove(metapath)
        return JsonResponse(
            {"status": "success", "message": "Plik został usunięty."}, status=200
        )


class DeleteSavedFile(View):
    model = None
    file_model = None

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(self.model, pk=request.POST.get("object"))
        file_object = get_object_or_404(
            self.file_model,
            **{"pk": request.POST.get("file"), self.file_model.PARENT_FIELD: obj}
        )
        if not self.check_permission(obj):
            raise PermissionDenied
        file_object.delete()
        return JsonResponse(
            {"status": "success", "message": "Plik został usunięty."}, status=200
        )

    def check_permission(self, obj):
        return True
