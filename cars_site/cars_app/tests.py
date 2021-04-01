from django.test import Client, TestCase

from .models import Car
from .views import *


class TestGetCarView(TestCase):
    def setUp(self):
        self.client = Client()

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
                "model": ""
            }
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
        response2 = self.client.get("/car:retrieve", data={"pk": car.pk, "show_category": True,
                                                           "show_type": True})
        response_json2 = response2.json()

        self.assertEqual(response2.status_code, 200)
        self.assertIn("category", response_json2.keys())
        self.assertIn("motor_type", response_json2.keys())

        response3 = self.client.get("/car:retrieve", data={"pk": car.pk, "show_category": True,
                                                           "show_type": False})
        response_json3 = response3.json()

        self.assertEqual(response3.status_code, 200)
        self.assertIn("category", response_json3.keys())
        self.assertNotIn("motor_type", response_json3.keys())

        response4 = self.client.get("/car:retrieve", data={"pk": car.pk, "show_category": False,
                                                           "show_type": True})
        response_json4 = response4.json()

        self.assertEqual(response4.status_code, 200)
        self.assertNotIn("category", response_json4.keys())
        self.assertIn("motor_type", response_json4.keys())


class T(TestCase):
    pass
