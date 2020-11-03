from django import forms
from dateutil import parser as date_parser
from apps.employees.models import Employee, WorkAbsence


class EmployeeModelForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["first_name", "last_name", "email", "phone", "user"]

    def clean_phone(self):
        data = self.cleaned_data["phone"]
        if data:
            return data.replace(" ", "")
        return data


class WorkAbsenceModelForm(forms.ModelForm):
    date_range = forms.CharField(
        label="Termin nieobecności",
        widget=forms.TextInput(attrs={"class": "date-range-input"}),
    )

    class Meta:
        model = WorkAbsence
        fields = ["employee", "date_range", "reason", "date_from", "date_to", "comment"]
        widgets = {
            "date_to": forms.HiddenInput,
            "date_from": forms.HiddenInput,
            "employee": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date_from"].required = False
        self.fields["date_to"].required = False
        if self.instance and self.instance.pk:
            self.fields[
                "date_range"
            ].initial = f"{self.instance.date_from.strftime('%d.%m.%Y')} - {self.instance.date_to.strftime('%d.%m.%Y')}"

    def clean(self):
        try:
            date_from, date_to = self.cleaned_data.get("date_range").split(" - ")
            date_from = date_parser.parse(date_from, dayfirst=True).date()
            date_to = date_parser.parse(date_to, dayfirst=True).date()
            self.cleaned_data["date_from"] = date_from
            self.cleaned_data["date_to"] = date_to
        except ValueError:
            self.add_error("date_range", "Nieprawidłowy zakres dat")
        return self.cleaned_data
