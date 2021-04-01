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
            "/car:list",
            data={"show_category": False, "show_type": True}
        )

        self.assertEqual(response4.status_code, 200)
        response_json4 = response4.json()
        self.assertNotIn("category", response_json4[0]["fields"].keys())
        self.assertIn("motor_type", response_json4[0]["fields"].keys())

