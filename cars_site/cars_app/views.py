import json

from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .models import Car
from .serializers import CarSerializer, CarUpdateSerializer, CarPkSerializer


@api_view(["GET"])
def get_car(request):
    try:
        show_category, show_type = _get_flags_from_params(request)
        id_ = request.GET["pk"]
    except (WrongParamsException, KeyError):
        return HttpResponse(status=422)
    else:
        needed_fields = _get_needed_fields(show_category, show_type)
        try:
            # TODO: Needed fields filtering is probably of no use here as it still returns the
            #  whole object.
            [car] = Car.objects.only(*needed_fields).filter(id=id_)
        except (Car.DoesNotExist, ValueError):
            return HttpResponse(status=422)
        else:
            car_serialized = json.dumps(model_to_dict(car, fields=needed_fields),
                                        cls=DjangoJSONEncoder)
            return HttpResponse(car_serialized, content_type="application/json")


@api_view(["GET"])
def get_cars_list(request):
    try:
        show_category, show_type = _get_flags_from_params(request)
    except WrongParamsException:
        return HttpResponse(status=422)
    else:
        needed_fields = _get_needed_fields(show_category, show_type)
        # TODO: Needed fields filtering is probably of no use here as it still returns the
        #  whole object.
        cars = Car.objects.only(*needed_fields)

        return HttpResponse(
            serializers.serialize("json", cars, fields=needed_fields),
            content_type="application/json",
        )


def _get_flags_from_params(request):
    # TODO: Change for parser
    show_category = request.GET.get("show_category", "false")
    show_type = request.GET.get("show_type", "false")
    if show_category.lower() not in ["true", "false"] and show_type.lower() not in [
        "true",
        "false",
    ]:
        raise WrongParamsException("Flags should have values either 'true' or 'false'")
    else:
        return show_category, show_type


def _get_needed_fields(show_category, show_type):
    show_category = show_category.lower() == "true"
    show_type = show_type.lower() == "true"
    needed_fields = [field.name for field in Car._meta.get_fields()]
    if show_category is False:
        needed_fields.remove("category")
    if show_type is False:
        needed_fields.remove("motor_type")

    return needed_fields


@api_view(["POST"])
def add_car(request):
    serializer = CarSerializer(data=request.data)
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
    except (KeyError, Car.DoesNotExist):
        return HttpResponse(status=422)
    else:
        serializer = CarUpdateSerializer(instance=to_update, data=data)
        if serializer.is_valid():
            # This should update the model, as the instance is not empty.
            serializer.save()
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=422)


# TODO: Check if can be changed to generic? (but rather not)
@api_view(["POST"])
def delete_car(request):
    serializer = CarPkSerializer(data=request.data)
    if serializer.is_valid():
        try:
            id_ = request.data["pk"]
            Car.objects.get(id=id_).delete()
        except (KeyError, Car.DoesNotExist):
            return HttpResponse(status=422)
        else:
            return HttpResponse(status=204)


class WrongParamsException(Exception):
    pass
