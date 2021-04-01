from django.forms import model_to_dict
from django.test import TestCase

from .views import *


class TestGetCarView(TestCase):
    def test_returns_error_code_when_pk_not_provided(self):
        response = self.client.get("/car:retrieve")
        self.assertEqual(response.status_code, 422)

    def test_returns_error_code_when_no_car_present(self):
        response = self.client.get("/car:retrieve", data={"pk": 3})
        self.assertEqual(response.status_code, 422)

    def test_returns_car_in_json_format_if_pk_exists(self):
        car = Car.objects.create(
            max_passengers=4, registration_number="asdf", year_of_manufacture=2000
        )
        response = self.client.get("/car:retrieve", data={"pk": car.pk})
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                "id": car.pk,
                "registration_number": "asdf",
                "max_passengers": 4,
                "year_of_manufacture": 2000,
                "manufacturer": "",
                "model": "",
            },
        )

    def test_category_and_motor_type_are_only_returned_when_asked(self):
        car = Car.objects.create(
            max_passengers=4, registration_number="asdf", year_of_manufacture=2000
        )
        response = self.client.get("/car:retrieve", data={"pk": car.pk})
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("category", response_json.keys())
        self.assertNotIn("motor_type", response_json.keys())

        # TODO: Change show_type to more explicit name - show_motor_type
        response2 = self.client.get(
            "/car:retrieve", data={"pk": car.pk, "show_category": True, "show_type": True}
        )
        response_json2 = response2.json()

        self.assertEqual(response2.status_code, 200)
        self.assertIn("category", response_json2.keys())
        self.assertIn("motor_type", response_json2.keys())

        response3 = self.client.get(
            "/car:retrieve",
            data={"pk": car.pk, "show_category": True, "show_type": False},
        )
        response_json3 = response3.json()

        self.assertEqual(response3.status_code, 200)
        self.assertIn("category", response_json3.keys())
        self.assertNotIn("motor_type", response_json3.keys())

        response4 = self.client.get(
            "/car:retrieve",
            data={"pk": car.pk, "show_category": False, "show_type": True},
        )
        response_json4 = response4.json()

        self.assertEqual(response4.status_code, 200)
        self.assertNotIn("category", response_json4.keys())
        self.assertIn("motor_type", response_json4.keys())


class TestCarsListView(TestCase):
    def test_returns_list_of_car_objects(self):
        car = Car.objects.create(
            max_passengers=4, registration_number="car-1", year_of_manufacture=2000
        )
        car2 = Car.objects.create(
            max_passengers=5, registration_number="car-2", year_of_manufacture=2001
        )
        car3 = Car.objects.create(
            max_passengers=6, registration_number="car-3", year_of_manufacture=2002
        )

        response = self.client.get("/car:list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "model": "cars_app.car",
                    "pk": car.pk,
                    "fields": {
                        "registration_number": "car-1",
                        "max_passengers": 4,
                        "year_of_manufacture": 2000,
                        "manufacturer": "",
                        "model": "",
                    },
                },
                {
                    "model": "cars_app.car",
                    "pk": car2.pk,
                    "fields": {
                        "registration_number": "car-2",
                        "max_passengers": 5,
                        "year_of_manufacture": 2001,
                        "manufacturer": "",
                        "model": "",
                    },
                },
                {
                    "model": "cars_app.car",
                    "pk": car3.pk,
                    "fields": {
                        "registration_number": "car-3",
                        "max_passengers": 6,
                        "year_of_manufacture": 2002,
                        "manufacturer": "",
                        "model": "",
                    },
                },
            ],
        )

    def test_returns_empty_list_if_no_cars_created(self):
        response = self.client.get("/car:list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_returns_category_and_motor_type_only_when_asked(self):
        Car.objects.create(
            max_passengers=4, registration_number="car-1", year_of_manufacture=2000
        )
        Car.objects.create(
            max_passengers=5, registration_number="car-2", year_of_manufacture=2001
        )
        Car.objects.create(
            max_passengers=6, registration_number="car-3", year_of_manufacture=2002
        )

        response = self.client.get("/car:list")
        response_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("category", response_json[0]["fields"].keys())
        self.assertNotIn("motor_type", response_json[0]["fields"].keys())

        # TODO: Change show_type to more explicit name - show_motor_type
        response2 = self.client.get(
            "/car:list", data={"show_category": True, "show_type": True}
        )

        self.assertEqual(response2.status_code, 200)
        response_json2 = response2.json()
        self.assertIn("category", response_json2[0]["fields"].keys())
        self.assertIn("motor_type", response_json2[0]["fields"].keys())

        response3 = self.client.get(
            "/car:list",
            data={"show_category": True, "show_type": False},
        )

        self.assertEqual(response3.status_code, 200)
        response_json3 = response3.json()
        self.assertIn("category", response_json3[0]["fields"].keys())
        self.assertNotIn("motor_type", response_json3[0]["fields"].keys())

        response4 = self.client.get(
            "/car:list", data={"show_category": False, "show_type": True}
        )

        self.assertEqual(response4.status_code, 200)
        response_json4 = response4.json()
        self.assertNotIn("category", response_json4[0]["fields"].keys())
        self.assertIn("motor_type", response_json4[0]["fields"].keys())


# TODO: urls as class properties
class TestAddCarView(TestCase):
    def test_single_car_can_be_added(self):
        post_data = {
            "registration_number": "asdf-123",
            "max_passengers": 444,
            "year_of_manufacture": 2000,
            "model": "a",
            "manufacturer": "b",
        }
        response = self.client.post("/car:add", data=post_data)

        self.assertEqual(response.status_code, 201)
        cars = Car.objects.all()

        self.assertEqual(1, len(cars))

        car = model_to_dict(cars[0])
        # These 3 params are not the subject of test
        car.pop("motor_type")
        car.pop("category")
        car.pop("id")

        self.assertEqual(post_data, car)

    def test_add_multiple_cars(self):
        post_data = {
            "registration_number": "asdf-123",
            "max_passengers": 444,
            "year_of_manufacture": 2000,
            "model": "a",
            "manufacturer": "b",
        }
        response = self.client.post("/car:add", data=post_data)
        self.assertEqual(response.status_code, 201)

        post_data2 = {
            "registration_number": "gjhk-123",
            "max_passengers": 444,
            "year_of_manufacture": 2000,
            "model": "a",
            "manufacturer": "b",
        }
        response2 = self.client.post("/car:add", data=post_data2)
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
        }
        response = self.client.post("/car:add", data=post_data)

        self.assertEqual(response.status_code, 400)
        cars = Car.objects.all()

        self.assertEqual(0, len(cars))

    def test_resource_is_not_created_when_not_enough_data(self):
        post_data = {
            "registration_number": "asdf-123",
            "max_passengers": 4,
            "year_of_manufacture": 2000,
            "model": "a",
            # No manufacturer
        }
        response = self.client.post("/car:add", data=post_data)

        self.assertEqual(response.status_code, 400)
        cars = Car.objects.all()

        self.assertEqual(0, len(cars))


class TestUpdateCarView(TestCase):
    def setUp(self) -> None:
        self.url = "/car:update"

    def test_only_specified_parameter_gets_updated(self):
        car = Car.objects.create(
            **{
                "registration_number": "asdf-123",
                "max_passengers": 444,
                "year_of_manufacture": 2000,
                "model": "a",
                "manufacturer": "b",
            }
        )

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

        # TODO: checking of additional parameters could also be done for code consistency. (
        #  helper function?)

    def test_multiple_parameters_can_be_updated(self):
        car = Car.objects.create(
            **{
                "registration_number": "asdf-123",
                "max_passengers": 444,
                "year_of_manufacture": 2000,
                "model": "a",
                "manufacturer": "b",
            }
        )

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
        car = Car.objects.create(
            **{
                "registration_number": "asdf-123",
                "max_passengers": 444,
                "year_of_manufacture": 2000,
                "model": "a",
                "manufacturer": "b",
            }
        )
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
                "max_passengers": 444,
                "year_of_manufacture": 2000,
                "model": "a",
                "manufacturer": "b",
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
