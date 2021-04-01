from rest_framework import serializers

from .models import Car


class CarCreateSerializer(serializers.ModelSerializer):
    """Serializer for fields needed for Car resource creation."""
    class Meta:
        model = Car
        fields = '__all__'


class CarUpdateSerializer(serializers.ModelSerializer):
    """Serializer for fields needed for Car resource update."""
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
