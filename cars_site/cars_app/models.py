from django.db import models


class CarClassChoices(models.TextChoices):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST_CLASS = "first class"


class MotorTypeChoices(models.TextChoices):
    HYBRID = "hybrid"
    ELECTRIC = "electric"


class Car(models.Model):
    objects = models.Manager()

    registration_number = models.fields.CharField(max_length=15, unique=True)
    max_passengers = models.fields.IntegerField()
    year_of_manufacture = models.fields.IntegerField()
    manufacturer = models.fields.CharField(max_length=20)
    model = models.fields.CharField(max_length=20)
    category = models.CharField(
        choices=CarClassChoices.choices, max_length=30, default=CarClassChoices.BUSINESS
    )
    motor_type = models.CharField(
        choices=MotorTypeChoices.choices, max_length=40, default=MotorTypeChoices.HYBRID
    )
