from unittest.mock import patch

from django.forms import model_to_dict
from django.test import TestCase

from .models import Car

EXAMPLE_CAR_DATA = {
    "registration_number": "asdf-123",
    "max_passengers": 5,
    "year_of_manufacture": 2000,
    "model": "a",
    "manufacturer": "b",
    "category": "economy",
    "motor_type": "first class",
}
EXAMPLE_CAR_DATA2 = {
    "registration_number": "GHJK-123",
    "max_passengers": 5,
    "year_of_manufacture": 2001,
    "model": "a",
    "manufacturer": "b",
    "category": "economy",
    "motor_type": "first class",
}
EXAMPLE_CAR_DATA3 = {
    "registration_number": "xxxx-123",
    "max_passengers": 6,
    "year_of_manufacture": 2002,
    "model": "a",
    "manufacturer": "b",
    "category": "economy",
    "motor_type": "first class",
}


class TestGetCarView(TestCase):
    def setUp(self) -> None:
        self.url = "/car:retrieve"

    def test_returns_error_code_when_pk_not_provided(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 422)

    def test_returns_error_code_when_no_car_present(self):
        response = self.client.get(self.url, data={"id": 3})
        self.assertEqual(response.status_code, 422)

    def test_returns_car_in_json_format_if_pk_exists(self):
        car = Car.objects.create(**EXAMPLE_CAR_DATA)
        response = self.client.get(self.url, data={"id": car.pk})
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(), model_to_dict(car, exclude=["category", "motor_type"])
        )

    def test_category_and_motor_type_are_only_returned_when_asked(self):
        car = Car.objects.create(**EXAMPLE_CAR_DATA)
        response = self.client.get(self.url, data={"id": car.pk})
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("category", response_json.keys())
        self.assertNotIn("motor_type", response_json.keys())

        response2 = self.client.get(
            self.url, data={"id": car.pk, "show_category": True, "show_motor_type": True}
        )
        response_json2 = response2.json()

        self.assertEqual(response2.status_code, 200)
        self.assertIn("category", response_json2.keys())
        self.assertIn("motor_type", response_json2.keys())

        response3 = self.client.get(
            self.url,
            data={"id": car.pk, "show_category": True, "show_motor_type": False},
        )
        response_json3 = response3.json()

        self.assertEqual(response3.status_code, 200)
        self.assertIn("category", response_json3.keys())
        self.assertNotIn("motor_type", response_json3.keys())

        response4 = self.client.get(
            self.url,
            data={"id": car.pk, "show_category": False, "show_motor_type": True},
        )
        response_json4 = response4.json()

        self.assertEqual(response4.status_code, 200)
        self.assertNotIn("category", response_json4.keys())
        self.assertIn("motor_type", response_json4.keys())


class TestCarsListView(TestCase):
    def setUp(self) -> None:
        self.url = "/car:list"

    def test_returns_list_of_car_objects(self):
        car = Car.objects.create(**EXAMPLE_CAR_DATA)
        car2 = Car.objects.create(**EXAMPLE_CAR_DATA2)
        car3 = Car.objects.create(**EXAMPLE_CAR_DATA3)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "model": "cars_app.car",
                    "pk": car.pk,
                    "fields": model_to_dict(
                        car, exclude=["category", "motor_type", "id"]
                    ),
                },
                {
                    "model": "cars_app.car",
                    "pk": car2.pk,
                    "fields": model_to_dict(
                        car2, exclude=["category", "motor_type", "id"]
                    ),
                },
                {
                    "model": "cars_app.car",
                    "pk": car3.pk,
                    "fields": model_to_dict(
                        car3, exclude=["category", "motor_type", "id"]
                    ),
                },
            ],
        )

    def test_returns_empty_list_if_no_cars_created(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_returns_category_and_motor_type_only_when_asked(self):
        # TODO: Check why it is possible to create car with not all parameters.
        Car.objects.create(**EXAMPLE_CAR_DATA)
        Car.objects.create(**EXAMPLE_CAR_DATA2)
        Car.objects.create(**EXAMPLE_CAR_DATA3)

        response = self.client.get(self.url)
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("category", response_json[0]["fields"].keys())
        self.assertNotIn("motor_type", response_json[0]["fields"].keys())

        response2 = self.client.get(
            self.url, data={"show_category": True, "show_motor_type": True}
        )

        self.assertEqual(response2.status_code, 200)
        response_json2 = response2.json()
        self.assertIn("category", response_json2[0]["fields"].keys())
        self.assertIn("motor_type", response_json2[0]["fields"].keys())

        response3 = self.client.get(
            self.url,
            data={"show_category": True, "show_motor_type": False},
        )

        self.assertEqual(response3.status_code, 200)
        response_json3 = response3.json()
        self.assertIn("category", response_json3[0]["fields"].keys())
        self.assertNotIn("motor_type", response_json3[0]["fields"].keys())

        response4 = self.client.get(
            self.url, data={"show_category": False, "show_motor_type": True}
        )

        self.assertEqual(response4.status_code, 200)
        response_json4 = response4.json()
        self.assertNotIn("category", response_json4[0]["fields"].keys())
        self.assertIn("motor_type", response_json4[0]["fields"].keys())

    def test_possibility_to_filter_by_various_fields_and_types(self):
        Car.objects.create(**EXAMPLE_CAR_DATA)
        Car.objects.create(**EXAMPLE_CAR_DATA2)
        Car.objects.create(**EXAMPLE_CAR_DATA3)

        # Test filter for not exact value
        response = self.client.get(self.url, data={"max_passengers__gt": 5})
        self.assertEqual(response.status_code, 200)

        cars_with_more_then_5_passengers = response.json()

        self.assertEqual(len(cars_with_more_then_5_passengers), 1)
        # TODO: Change the view so that all fields are returned in single dict, not nested one
        #  like here
        self.assertGreater(
            cars_with_more_then_5_passengers[0]["fields"]["max_passengers"], 5
        )

        # Test filter for exact value
        response2 = self.client.get(self.url, data={"max_passengers": 5})
        self.assertEqual(response2.status_code, 200)

        cars_with_5_passengers = response2.json()

        self.assertEqual(len(cars_with_5_passengers), 2)
        self.assertTrue(
            all([car["fields"]["max_passengers"] == 5 for car in cars_with_5_passengers])
        )

        # Test filter returning all objects
        response3 = self.client.get(self.url, data={"manufacturer": "b"})
        self.assertEqual(response3.status_code, 200)

        economy_cars = response3.json()

        self.assertEqual(len(economy_cars), 3)
        self.assertTrue(
            all([car["fields"]["manufacturer"] == "b" for car in economy_cars])
        )

        # Test filter for similar registration number
        response3 = self.client.get(self.url, data={"registration_number__icontains": "xxx"})
        self.assertEqual(response3.status_code, 200)

        economy_cars = response3.json()

        self.assertEqual(len(economy_cars), 1)


class TestAddCarView(TestCase):
    def setUp(self) -> None:
        self.url = "/car:add"

    @patch("cars_app.views.info_api.get_manufacturer_models")
    def test_single_car_can_be_added(self, get_models):
        manufacturer = "Volkswagen"
        model = "Passat"

        get_models.return_value = ["Passat"]

        post_data = {
            "registration_number": "KNS-123 HH",
            "max_passengers": 4,
            "year_of_manufacture": 2000,
            "model": model,
            "manufacturer": manufacturer,
            "category": "economy",
            "motor_type": "electric",
        }
        response = self.client.post(self.url, data=post_data)

        self.assertEqual(response.status_code, 201)
        cars = Car.objects.all()

        self.assertEqual(1, len(cars))

        car = model_to_dict(cars[0])
        car.pop("id")

        self.assertEqual(post_data, car)

    @patch("cars_app.views.info_api.get_manufacturer_models")
    def test_add_multiple_cars(self, get_models):
        get_models.return_value = ["Passat", "Golf"]

        post_data = {
            "registration_number": "asdf-123",
            "max_passengers": 4,
            "year_of_manufacture": 2000,
            "model": "Golf",
            "manufacturer": "Volkswagen",
            "category": "economy",
            "motor_type": "electric",
        }
        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, 201)

        post_data2 = {
            "registration_number": "gjhk-123",
            "max_passengers": 4,
            "year_of_manufacture": 2001,
            "model": "Passat",
            "manufacturer": "Volkswagen",
            "category": "economy",
            "motor_type": "electric",
        }
        response2 = self.client.post(self.url, data=post_data2)
        self.assertEqual(response2.status_code, 201)

        cars = Car.objects.all()

        self.assertEqual(2, len(cars))

    def test_resource_is_not_created_when_invalid_data(self):
        max_passengers = "asdf"
        year_of_manufacture = "349?hn.;34"
        post_data = {
            "registration_number": "asdf-123",
            "max_passengers": max_passengers,
            "year_of_manufacture": year_of_manufacture,
            "model": "a",
            "manufacturer": "b",
            "category": "economy",
            "motor_type": "electric",
        }
        response = self.client.post(self.url, data=post_data)

        self.assertEqual(response.status_code, 400)
        cars = Car.objects.all()

        self.assertEqual(0, len(cars))

    @patch("cars_app.views.info_api.get_manufacturer_models")
    def test_resource_is_not_created_when_not_enough_data(self, get_models):
        post_data = {
            "registration_number": "asdf-123",
            "max_passengers": 4,
            "year_of_manufacture": 2000,
            "model": "a",
            "category": "economy",
            # no motor_type
        }
        response = self.client.post(self.url, data=post_data)

        self.assertEqual(response.status_code, 400)
        cars = Car.objects.all()

        self.assertEqual(0, len(cars))

    @patch("cars_app.views.info_api.get_manufacturer_models")
    def test_car_with_invalid_manufacturer_cant_be_created(self, get_models):
        # Invalid manufacturer should result in empty results from API
        get_models.return_value = []

        invalid_manufacturer = "Folkswagen"

        post_data = {
            "registration_number": "asdf-123",
            "max_passengers": 4,
            "year_of_manufacture": 2000,
            "model": "a",
            "manufacturer": invalid_manufacturer,
            "category": "economy",
            "motor_type": "electric",
        }

        response = self.client.post(self.url, data=post_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(Car.objects.all()), 0)

    @patch("cars_app.views.info_api.get_manufacturer_models")
    def test_car_with_invalid_model_cant_be_created(self, get_models):
        get_models.return_value = ["Golf", "Passat"]
        manufacturer = "Volkswagen"
        invalid_model = "126p"

        post_data = {
            "registration_number": "asdf-123",
            "max_passengers": 4,
            "year_of_manufacture": 2000,
            "model": invalid_model,
            "manufacturer": manufacturer,
            "category": "economy",
            "motor_type": "electric",
        }

        response = self.client.post(self.url, data=post_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(Car.objects.all()), 0)


class TestUpdateCarView(TestCase):
    def setUp(self) -> None:
        self.url = "/car:update"

    @patch("cars_app.views.info_api.get_manufacturer_models")
    def test_only_specified_parameter_gets_updated(self, get_models):
        car = Car.objects.create(**EXAMPLE_CAR_DATA)

        response = self.client.post(
            self.url,
            data={"pk": car.pk, "max_passengers": "4"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 204)

        car_updated = Car.objects.get(id=car.pk)
        self.assertEqual(car_updated.max_passengers, 4)

        self.assertEqual(car_updated.registration_number, car.registration_number)
        self.assertEqual(car_updated.year_of_manufacture, car.year_of_manufacture)
        self.assertEqual(car_updated.model, car.model)
        self.assertEqual(car_updated.manufacturer, car.manufacturer)

        response2 = self.client.post(
            self.url,
            data={"pk": car.pk, "registration_number": "KNS-xxxx23"},
            content_type="application/json",
        )

        self.assertEqual(response2.status_code, 204)

        car_updated_second_time = Car.objects.get(id=car.pk)
        self.assertEqual(car_updated_second_time.registration_number, "KNS-xxxx23")

    @patch("cars_app.views.info_api.get_manufacturer_models")
    def test_multiple_parameters_can_be_updated(self, get_models):
        car = Car.objects.create(**EXAMPLE_CAR_DATA)

        response = self.client.post(
            self.url,
            data={"pk": car.pk, "max_passengers": 4, "year_of_manufacture": 2010},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 204)

        car_updated = Car.objects.get(id=car.pk)
        self.assertEqual(car_updated.max_passengers, 4)
        self.assertEqual(car_updated.year_of_manufacture, 2010)

    def test_car_doesnt_get_updated_if_invalid_pk(self):
        car = Car.objects.create(**EXAMPLE_CAR_DATA)
        invalid_pk = 999999

        response = self.client.post(
            self.url,
            data={"pk": invalid_pk, "max_passengers": 4, "year_of_manufacture": 2010},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)

        car_updated = Car.objects.get(id=car.pk)
        self.assertDictEqual(model_to_dict(car), model_to_dict(car_updated))

    def test_car_doesnt_get_updated_if_invalid_parameter_value_sent(self):
        car = Car.objects.create(
            **{
                "registration_number": "asdf-123",
                "max_passengers": 4,
                "year_of_manufacture": 2000,
                "model": "a",
                "manufacturer": "b",
                "category": "economy",
                "motor_type": "first_class",
            }
        )
        invalid_passengers_value = "asdf"

        response = self.client.post(
            self.url,
            data={
                "pk": car.pk,
                "max_passengers": invalid_passengers_value,
                "year_of_manufacture": 2010,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 422)

        car_updated = Car.objects.get(id=car.pk)
        self.assertDictEqual(model_to_dict(car), model_to_dict(car_updated))

    @patch("cars_app.views.info_api.get_manufacturer_models")
    def test_car_cant_be_updated_with_invalid_manufacturer(self, get_models):
        # Invalid manufacturer should result in empty results from API
        get_models.return_value = []

        car = Car.objects.create(
            **{
                "registration_number": "asdf-123",
                "max_passengers": 4,
                "year_of_manufacture": 2000,
                "model": "Passat",
                "manufacturer": "Porshe",
                "category": "economy",
                "motor_type": "first_class",
            }
        )

        invalid_manufacturer = "Folkswagen"

        post_data = {"manufacturer": invalid_manufacturer, "pk": car.pk}

        response = self.client.post(
            self.url, data=post_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(Car.objects.get(pk=car.pk).manufacturer, "Porshe")

    @patch("cars_app.views.info_api.get_manufacturer_models")
    def test_car_cant_be_updated_with_invalid_model(self, get_models_mock):
        get_models_mock.return_value = ["Golf", "Passat"]
        invalid_model = "126p"

        car = Car.objects.create(
            **{
                "registration_number": "asdf-123",
                "max_passengers": 4,
                "year_of_manufacture": 2000,
                "model": "Passat",
                "manufacturer": "Volkswagen",
                "category": "economy",
                "motor_type": "first_class",
            }
        )

        post_data = {"model": invalid_model, "pk": car.pk}

        response = self.client.post(
            self.url, data=post_data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(Car.objects.get(pk=car.pk).manufacturer, "Volkswagen")


class TestDeleteCarView(TestCase):
    def setUp(self) -> None:
        self.url = "/car:delete"

    def test_object_gets_deleted(self):
        car = Car.objects.create(**EXAMPLE_CAR_DATA)

        response = self.client.post(self.url, data={"pk": car.pk})

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(Car.objects.all()), 0)

    def test_dont_delete_anything_if_non_existing_pk(self):
        Car.objects.create(**EXAMPLE_CAR_DATA)

        non_existing_pk = 99999
        response = self.client.post(self.url, data={"pk": non_existing_pk})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(len(Car.objects.all()), 1)

    def test_dont_delete_anything_if_invalid_pk(self):
        Car.objects.create(**EXAMPLE_CAR_DATA)

        invalid_pk = "asdf"
        response = self.client.post(self.url, data={"pk": invalid_pk})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(len(Car.objects.all()), 1)

    def test_dont_delete_anything_if_pk_not_specified(self):
        Car.objects.create(**EXAMPLE_CAR_DATA)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(len(Car.objects.all()), 1)
