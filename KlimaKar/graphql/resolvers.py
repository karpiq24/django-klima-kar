import enum


class BaseModelFormResolver(object):
    form_class = None
    inlines = {}
    inlines_parent = None

    def __init__(self, data, instance=None):
        self.object = instance
        self.inlines_data = {}
        self.inlines_forms = {}
        for key, _ in self.inlines.items():
            self.inlines_data[key] = [
                self._enum_to_choice(inline) for inline in data.pop(key, [])
            ]
        self.data = self._enum_to_choice(data)

    def _enum_to_choice(self, data):
        for key, value in data.items():
            if issubclass(type(value), enum.Enum):
                data[key] = value.value
        return data

    def validate(self):
        self.form = self.form_class(data=self.data, instance=self.object)
        valid = self.form.is_valid()
        for key, form_class in self.inlines.items():
            self.inlines_forms[key] = []
            for form_data in self.inlines_data[key]:
                form = form_class(data=form_data)
                self.inlines_forms[key].append(form)
                if not form.is_valid():
                    valid = False
        return valid

    def errors(self):
        errors = []
        for field, error_list in self.form.errors.get_json_data().items():
            for error in error_list:
                errors.append(
                    {"field": field, "message": error["message"], "code": error["code"]}
                )
        for key, form_list in self.inlines_forms.items():
            for index, form in enumerate(form_list):
                for field, error_list in form.errors.get_json_data().items():
                    for error in error_list:
                        errors.append(
                            {
                                "inline": f"{key}.{index}",
                                "field": field,
                                "message": error["message"],
                                "code": error["code"],
                            }
                        )
        return errors

    def save(self):
        self.object = self.form.save()
        for key, form_list in self.inlines_forms.items():
            for form in form_list:
                obj = form.save(commit=False)
                setattr(obj, self.inlines_parent, self.object)
                obj.save()
        return self.object

    def process(self):
        if self.validate():
            obj = self.save()
            return {"status": True, "errors": [], "object": obj}
        return {"status": False, "errors": self.errors(), "object": None}
