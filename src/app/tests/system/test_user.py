import json

from app.modules.users.models_users import UserModel
from app.tests.base_test import BaseTest


class UserTest(BaseTest):
    def setUp(self):
        super(UserTest, self).setUp()
        with self.app() as client:
            with self.app_context():
                client.post(
                    "/register",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(
                        {
                            "name": "fanny",
                            "company_name": "certi",
                            "email": "fanny@email.com",
                            "username": "fcs",
                            "password": "abcd",
                        }
                    ),
                )

                auth_request = client.post(
                    "/login",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"username": "fcs", "password": "abcd"}),
                )

                token = json.loads(auth_request.data)["access_token"]
                self.access_token = token

    def test_register_user(self):
        with self.app() as client:
            with self.app_context():
                response = client.post(
                    "/register",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(
                        {
                            "name": "fanny",
                            "company_name": "certi",
                            "email": "fanny@email.com",
                            "username": "test",
                            "password": "abcd",
                        }
                    ),
                )

                self.assertEqual(response.status_code, 201)
                self.assertIsNotNone(UserModel.find_by_username("fcs"))

    def test_get_user_with_missing_auth(self):
        with self.app() as client:
            with self.app_context():
                response = client.get("user/1")
                self.assertEqual(response.status_code, 401)

    def test_get_user(self):
        with self.app() as client:
            with self.app_context():

                token = self.access_token

                response = client.get(
                    "/user/1",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer {}".format(token),
                    },
                )
                self.assertEqual(response.status_code, 200)

    def test_register_and_login(self):
        with self.app() as client:
            with self.app_context():
                client.post(
                    "/register",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(
                        {
                            "name": "fanny",
                            "company_name": "certi",
                            "email": "fanny@email.com",
                            "username": "fcs",
                            "password": "abcd",
                        }
                    ),
                )

                response = client.post(
                    "/login",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"username": "fcs", "password": "abcd"}),
                )

                self.assertIn("access_token", json.loads(response.data).keys())

    def test_register_duplicate_user(self):
        with self.app() as client:
            with self.app_context():
                client.post(
                    "/register",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(
                        {
                            "name": "fanny",
                            "company_name": "certi",
                            "email": "fanny@email.com",
                            "username": "fcs",
                            "password": "abcd",
                        }
                    ),
                )

                response = client.post(
                    "/register",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(
                        {
                            "name": "fanny",
                            "company_name": "certi",
                            "email": "fanny@email.com",
                            "username": "fcs",
                            "password": "abcd",
                        }
                    ),
                )

                self.assertEqual(response.status_code, 400)
