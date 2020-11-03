from django.urls import path
from apps.employees import views

app_name = "employees"
urlpatterns = [
    path("", views.EmployeeTableView.as_view(), name="employees"),
    path("nowy", views.EmployeeCreateView.as_view(), name="employee_create"),
    path(
        "<str:slug>,<int:pk>",
        views.EmployeeDetailView.as_view(),
        name="employee_detail",
    ),
    path(
        "<str:slug>,<int:pk>/edycja",
        views.EmployeeUpdateView.as_view(),
        name="employee_update",
    ),
    path(
        "absence/<int:pk>/update_ajax",
        views.WorkAbsenceUpdateAjaxView.as_view(),
        name="absence_update_ajax",
    ),
    path(
        "absence/<int:pk>/remove",
        views.WorkAbsenceRemoveView.as_view(),
        name="absence_remove",
    ),
    path(
        "absence/create_ajax",
        views.WorkAbsenceCreateAjaxView.as_view(),
        name="absence_create_ajax",
    ),
]
