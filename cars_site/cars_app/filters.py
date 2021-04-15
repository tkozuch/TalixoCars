from django_filters import rest_framework as filters

from .models import Car


class CarFilter(filters.FilterSet):
    class Meta:
        model = Car
        fields = {
            "max_passengers": ["exact", "gt"],
            "year_of_manufacture": ["lt", "exact", "gt"],
            "manufacturer": ["exact"],
            "registration_number": ["icontains"],
        }
