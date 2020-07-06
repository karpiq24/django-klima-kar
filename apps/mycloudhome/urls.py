from django.urls import path
from apps.mycloudhome import views

app_name = "mycloudhome"
urlpatterns = [
    path(
        "temporary_file_upload",
        views.TemporaryFileUploadView.as_view(),
        name="temporary_file_upload",
    ),
    path(
        "delete_temp_file", views.DeleteTemporaryFile.as_view(), name="delete_temp_file"
    ),
]
