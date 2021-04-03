from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models


class CarClassChoices(models.TextChoices):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST_CLASS = "first class"


class MotorTypeChoices(models.TextChoices):
    HYBRID = "hybrid"
    ELECTRIC = "electric"


class Car(models.Model):
    _MIN_MAX_PASSENGERS = 1
    _MAX_MAX_PASSENGERS = 60
    _MIN_YEAR_OF_MANUFACTURE = 1886  # First car's manufacture year
    _MAX_YEAR_OF_MANUFACTURE = datetime.now().year
    _REGISTRATION_NUMBER_FORMAT = r"^[A-Za-z0-9 \.\-]{3,}$"

    objects = models.Manager()

    registration_number = models.fields.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(_REGISTRATION_NUMBER_FORMAT)],
        default=None
    )
    max_passengers = models.fields.PositiveIntegerField(
        validators=[
            MinValueValidator(
                _MIN_MAX_PASSENGERS,
                f"Max passengers value is to low. Min: {_MIN_MAX_PASSENGERS}",
            ),
            MaxValueValidator(
                _MAX_MAX_PASSENGERS,
                f"Max passengers value is to high. Max: {_MAX_MAX_PASSENGERS}",
            ),
        ],
    )
    year_of_manufacture = models.fields.PositiveIntegerField(
        validators=[
            MinValueValidator(
                _MIN_YEAR_OF_MANUFACTURE,
                message=f"Manufacture year is to low. Min: {_MIN_YEAR_OF_MANUFACTURE}",
            ),
            MaxValueValidator(
                _MAX_YEAR_OF_MANUFACTURE,
                message=f"Manufacture year is to high. Max: {_MAX_YEAR_OF_MANUFACTURE}",
            ),
        ],
    )
    manufacturer = models.fields.CharField(max_length=20, default=None)
    model = models.fields.CharField(max_length=20, default=None)
    category = models.CharField(
        choices=CarClassChoices.choices, max_length=30, default=None
    )
    motor_type = models.CharField(
        choices=MotorTypeChoices.choices, max_length=40, default=None
    )
