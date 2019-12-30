from django.urls import path

from apps.audit import views

app_name = 'apps.audit'
urlpatterns = [
    path('', views.AuditLogTableView.as_view(), name='audit_logs'),
    path('diff', views.GetAuditLogDiffrence.as_view(), name='diff'),
]
