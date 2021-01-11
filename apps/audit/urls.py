from django.urls import path

from apps.audit import views

app_name = "audit"
urlpatterns = [
    path("", views.AuditLogTableView.as_view(), name="audit_logs"),
    path(
        "obiekt/<str:slug>,<int:content_type>,<int:object_id>",
        views.ObjectAuditLogTableView.as_view(),
        name="object_audit_logs",
    ),
]
