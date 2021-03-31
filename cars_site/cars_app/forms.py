from django.forms import ModelForm

from .models import Car


class UpdateCarForm(ModelForm):
    class Meta:
        model = Car
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_all_fields_except_pk_as_not_required()

    def _set_all_fields_except_pk_as_not_required(self):
        for field_name, field in self.fields.items():
            if field_name != 'pk':
                field.required = False
