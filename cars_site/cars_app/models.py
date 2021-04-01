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

    registration_number = models.fields.CharField(max_length=15, unique=True, null=False)
    max_passengers = models.fields.IntegerField(null=False)
    year_of_manufacture = models.fields.IntegerField(null=False)
    manufacturer = models.fields.CharField(max_length=20, null=False)
    model = models.fields.CharField(max_length=20, null=False)
    category = models.CharField(
        choices=CarClassChoices.choices, max_length=30, null=False
    )
    motor_type = models.CharField(
        choices=MotorTypeChoices.choices, max_length=40, null=False
    )
