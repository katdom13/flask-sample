import json
import pytest

from flask import url_for

from app.lib import TestMixin
from app.models import Account


class TestAPI(TestMixin):
    def test_login(self):
        """
        Login is successful
        """
        response = self.login()

        actual_data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert actual_data["status"] == "success"

    def test_login_empty(self):
        """
        Login error: No credentials provided
        """
        response = self.client.post(url_for("v1.login"), json={})

        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "Could not verify"}

        assert response.status_code == 401
        assert actual_data == expected_data

    def test_login_not_found(self):
        """
        Login error: No user found
        """
        response = self.client.post(
            url_for("v1.login"), json={"identity": "none", "password": "password"}
        )

        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "No user found"}

        assert response.status_code == 404
        assert actual_data == expected_data

    def test_login_invalid(self):
        """
        Login error: Password is invalid
        """
        response = self.client.post(
            url_for("v1.login"), json={"identity": "admin", "password": "pass"}
        )

        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "Invalid credentials provided"}

        assert response.status_code == 401
        assert actual_data == expected_data

    def test_login_inactive(self, users):
        """
        Login error: Inactive account
        """
        response = self.client.post(
            url_for("v1.login"), json={"identity": "disabled", "password": "password"}
        )

        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "Account is inactive"}

        assert response.status_code == 401
        assert actual_data == expected_data

    def test_get_users(self):
        """
        Get json of all user accounts
        """
        response = self.login()
        token = json.loads(response.get_data(as_text=True))['token']
        response = self.client.get(url_for("v1.get_users"), headers={'x-access-token': token})

        assert response.status_code == 200
        assert Account.query.count() == 1

    def test_get_users_fail(self):
        """
        Fetching of data fails because login login is required
        """
        response = self.client.get(url_for("v1.get_users"))

        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "You are unauthorized to do that"}

        assert response.status_code == 401
        assert actual_data == expected_data

    def test_get_user(self):
        """
        Get a single user
        """
        response = self.login()
        token = json.loads(response.get_data(as_text=True))['token']
        response = self.client.get(url_for("v1.get_user", username="admin"), headers={'x-access-token': token})
        actual_data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert actual_data["user"]["username"] == "admin"

    def test_get_non_user(self):
        """
        Fetching error: No user found
        """
        response = self.login()
        token = json.loads(response.get_data(as_text=True))['token']
        response = self.client.get(url_for("v1.get_user", username="none"), headers={'x-access-token': token})
        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "No user found"}

        assert response.status_code == 404
        assert actual_data == expected_data

    def test_get_user_fail(self):
        """
        Fetching error: Login is required
        """
        response = self.client.get(url_for("v1.get_user", username="none"))
        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "You are unauthorized to do that"}

        assert response.status_code == 401
        assert actual_data == expected_data

    def test_create_user(self, users):
        """
        Create a user
        """
        old_user_count = Account.query.count()

        user = {
            "first_name": "Admin",
            "last_name": "Dummy 2",
            "username": "admin2",
            "password": "password",
        }

        response = self.client.post(url_for("v1.create_user"), json=user)
        actual_data = json.loads(response.get_data(as_text=True))
        new_user_count = Account.query.count()

        assert response.status_code == 200
        assert actual_data["status"] == "success"
        assert new_user_count == (old_user_count + 1)
        assert actual_data["user"]["username"] == "admin2"

    def test_update_user(self, users):
        """
        Update a user
        """
        old_pass = Account.find("admin").password

        data = {"username": "@dmin", "password": "pass"}

        response = self.login()
        token = json.loads(response.get_data(as_text=True))['token']
        response = self.client.put(
            url_for("v1.update_user", username="admin"), json=data, headers={'x-access-token': token}
        )
        actual_data = json.loads(response.get_data(as_text=True))
        new_pass = actual_data["user"]["password"]

        assert response.status_code == 200
        assert actual_data["status"] == "success"
        assert actual_data["user"]["username"] == "@dmin"
        assert old_pass != new_pass

    def test_update_user_fail(self, users):
        """
        Update user error: Login is required
        """
        data = {"username": "@dmin"}

        response = self.client.put(
            url_for("v1.update_user", username="admin"), json=data
        )
        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "You are unauthorized to do that"}

        assert response.status_code == 401
        assert actual_data == expected_data

    def test_update_non_user(self, users):
        """
        Update user error: No user found
        """
        data = {"username": "@dmin"}

        response = self.login()
        token = json.loads(response.get_data(as_text=True))['token']
        response = self.client.put(
            url_for("v1.update_user", username="none"), json=data, headers={'x-access-token': token}
        )
        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "No user found"}

        assert response.status_code == 404
        assert actual_data == expected_data

    def test_delete_user(self, users):
        """
        Delete a user
        """
        old_user_count = Account.query.count()

        response = self.login()
        token = json.loads(response.get_data(as_text=True))['token']
        response = self.client.delete(url_for("v1.delete_user", username="disabled"), headers={'x-access-token': token})

        new_user_count = Account.query.count()

        actual_data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert new_user_count == (old_user_count - 1)
        assert actual_data["status"] == "success"

    def test_delete_user_fail(self, users):
        """
        Delete user error: Login is required
        """
        response = self.client.delete(url_for("v1.delete_user", username="disabled"))
        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "You are unauthorized to do that"}

        assert response.status_code == 401
        assert actual_data == expected_data

    def test_delete_non_user(self, users):
        """
        Delete user error: No user found
        """
        response = self.login()
        token = json.loads(response.get_data(as_text=True))['token']
        response = self.client.delete(url_for("v1.delete_user", username="none"), headers={'x-access-token': token})
        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "No user found"}

        assert response.status_code == 404
        assert actual_data == expected_data

    def test_logout(self):
        """
        Log the user out
        """
        response = self.login()
        token = json.loads(response.get_data(as_text=True))['token']
        response = self.logout(token)
        actual_data = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert actual_data["status"] == "success"

    def test_logout_fail(self):
        """
        Logout error: Login is required
        """
        response = self.logout()
        actual_data = json.loads(response.get_data(as_text=True))
        expected_data = {"error": "You are unauthorized to do that"}

        assert response.status_code == 401
        assert actual_data == expected_data
