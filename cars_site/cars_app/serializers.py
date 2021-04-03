import logging

import requests
from rest_framework import serializers

from .models import Car

log = logging.getLogger(__file__)


class CarsInfoCheckApi:
    URL = "https://vpic.nhtsa.dot.gov/api/"

    def __init__(self):
        self._manufacturer_models = None

    def get_manufacturer_models(self, manufacturer):
        if self._manufacturer_models is None:
            try:
                response = requests.get(
                    f"{self.URL}/vehicles/GetModelsForMake/{manufacturer}",
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
                        self.URL
                    )
                )
            else:
                results = response.json()["Results"]
                self._manufacturer_models = self._format_manufacturer_models(results)

        return self._manufacturer_models

    @staticmethod
    def _format_manufacturer_models(data):
        return [model["Model_Name"] for model in data]


class GeneralCarSerializer(serializers.ModelSerializer):
    """Serializer for all fields of a Car model."""

    class Meta:
        model = Car
        fields = "__all__"

    def __init__(self, info_api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info_api = info_api

    def validate(self, data):
        manufacturer = data.get("manufacturer")
        model = data.get("model")
        manufacturer_models = self.info_api.get_manufacturer_models(manufacturer)

        if manufacturer and not manufacturer_models:
            raise serializers.ValidationError("This manufacturer does not exist.")
        elif model and not any([result == model for result in manufacturer_models]):
            raise serializers.ValidationError(
                "There is no such model for this manufacturer"
            )
        else:
            return data


class CarUpdateSerializer(GeneralCarSerializer):
    """Serializer for fields needed for Car resource update."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_all_fields_except_pk_as_not_required()

    def _set_all_fields_except_pk_as_not_required(self):
        for field_name, field in self.fields.items():
            if field_name != "pk":
                field.required = False
