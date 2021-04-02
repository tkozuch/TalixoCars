import logging

import requests
from rest_framework import serializers

from .models import Car

log = logging.getLogger(__file__)


class ValidationMixin:
    """Mixin for Serializers that implements methods for validating manufacturer and model
    fields."""

    VALIDATING_API = "https://vpic.nhtsa.dot.gov/api/"
    _MANUFACTURER_MODELS = None

    def validate_manufacturer(self, value):
        if self._MANUFACTURER_MODELS is None:
            self._MANUFACTURER_MODELS = self._get_manufacturer_models(manufacturer=value)

        if not self._MANUFACTURER_MODELS:
            raise serializers.ValidationError("This manufacturer does not exist.")
        else:
            return value

    def validate_model(self, value):
        # TODO: Dry this - perhaps move to property
        if self._MANUFACTURER_MODELS is None:
            self._MANUFACTURER_MODELS = self._get_manufacturer_models(manufacturer=value)

        if not self._MANUFACTURER_MODELS:
            raise serializers.ValidationError(
                "Unable to validate this field because wrong "
                "manufacturer was provided."
            )
        elif not any(
            [result["Model_Name"] == value for result in self._MANUFACTURER_MODELS]
        ):
            raise serializers.ValidationError(
                "There is no such model for this manufacturer"
            )
        else:
            return value

    def _get_manufacturer_models(self, manufacturer):
        try:
            response = requests.get(
                f"{self.VALIDATING_API}/vehicles/GetModelsForMake/{manufacturer}",
                params={"format": "json"},
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            log.exception(
                "External API signaled a problem. Check status code for further "
                "information. Aborting."
            )
        except requests.exceptions.RequestException:
            log.exception(
                "An exception occurred while making request to external API: {}. Aborting.".format(
                    self.VALIDATING_API
                )
            )

        return response.json()["Results"]


class CarCreateSerializer(serializers.ModelSerializer, ValidationMixin):
    """Serializer for fields needed for Car resource creation."""

    class Meta:
        model = Car
        fields = "__all__"


class CarUpdateSerializer(serializers.ModelSerializer, ValidationMixin):
    """Serializer for fields needed for Car resource update."""

    class Meta:
        model = Car
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_all_fields_except_pk_as_not_required()

    def _set_all_fields_except_pk_as_not_required(self):
        for field_name, field in self.fields.items():
            if field_name != "pk":
                field.required = False
