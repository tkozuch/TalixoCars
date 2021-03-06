import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .filters import CarFilter
from .models import Car
from .serializers import (
    CarsInfoCheckApi,
    CarUpdateSerializer,
    FlagSerializer,
    GeneralCarSerializer,
)

info_api = CarsInfoCheckApi()


@api_view(["GET"])
def get_car(request):
    try:
        show_category, show_motor_type = _get_flags_from_params(request.GET)
        id_ = request.GET["id"]
    except (WrongParamsException, KeyError):
        return HttpResponse(status=422)
    else:
        needed_fields = _get_needed_fields(
            show_category, show_motor_type, car_fields=Car._meta.get_fields()
        )
        try:
            [car] = Car.objects.filter(id=id_).values(*needed_fields)
        except ValueError:
            return HttpResponse(status=422)
        else:
            car_serialized = json.dumps(car, cls=DjangoJSONEncoder)
            return HttpResponse(car_serialized, content_type="application/json")


@api_view(["GET"])
def get_cars_list(request):
    try:
        show_category, show_type = _get_flags_from_params(request.GET)
    except WrongParamsException:
        return HttpResponse(status=422)
    else:
        needed_fields = _get_needed_fields(
            show_category, show_type, car_fields=Car._meta.get_fields()
        )
        qs = CarFilter(request.GET).qs
        cars = qs.only(*needed_fields)

        return HttpResponse(
            serializers.serialize("json", cars, fields=needed_fields),
            content_type="application/json",
        )


def _get_flags_from_params(request_params):
    """Get values of boolean flags from request parameters."""

    serializer = FlagSerializer(data=request_params)

    if not serializer.is_valid():
        raise WrongParamsException(
            "Flags should have values either 'true' or 'false' and their "
            "case variations, or 0, 1."
        )

    show_category = serializer.data["show_category"]
    show_motor_type = serializer.data["show_motor_type"]

    return show_category, show_motor_type


def _get_needed_fields(show_category, show_type, car_fields):
    """Get list of fields that we need to fetch from the Car model."""

    needed_fields = [field.name for field in car_fields]

    if show_category is False:
        needed_fields.remove("category")
    if show_type is False:
        needed_fields.remove("motor_type")

    return needed_fields


@api_view(["POST"])
def add_car(request):
    serializer = GeneralCarSerializer(info_api, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def update_car(request):
    data = JSONParser().parse(request)
    try:
        id_ = data["pk"]
        to_update = Car.objects.get(id=id_)
    except (KeyError, ValueError, Car.DoesNotExist):
        return HttpResponse(status=422)
    else:
        serializer = CarUpdateSerializer(info_api, instance=to_update, data=data)
        if serializer.is_valid():
            serializer.update(
                instance=to_update, validated_data=serializer.validated_data
            )
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=422)


@api_view(["POST"])
def delete_car(request):
    try:
        id_ = request.data["pk"]
        Car.objects.get(id=id_).delete()
    except (KeyError, ValueError, Car.DoesNotExist):
        return HttpResponse(status=422)
    else:
        return HttpResponse(status=204)


class WrongParamsException(Exception):
    pass
