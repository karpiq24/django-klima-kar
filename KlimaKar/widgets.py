from django import forms


class PrettySelect(forms.RadioSelect):
    template_name = 'forms/pretty_select_field.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'pretty-select'
