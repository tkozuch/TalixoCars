from rest_framework import serializers
from rest_framework import parsers

from .models import Car


# TODO: Dry Serializers
# TODO: Provide better naming (CarCreateFieldsSerializer?)
class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'


class CarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_all_fields_except_pk_as_not_required()

    def _set_all_fields_except_pk_as_not_required(self):
        for field_name, field in self.fields.items():
            if field_name != 'pk':
                field.required = False


class CarPkSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # DRF Serializer somehow recognizes it as not required. Shouldn't it be by default required?
        self.fields["pk"].required = True

    class Meta:
        model = Car
        fields = ["pk"]


class CarsListParamsSerializer(serializers.Serializer):
    show_category = serializers.BooleanField(required=False, default=False)
    show_category = serializers.BooleanField(required=False, default=False)
