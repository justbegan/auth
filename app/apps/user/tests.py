from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.city.models import FeedPost
from apps.profile.models import City
from apps.user.models import CustomUser


@override_settings(PLUSOFON_WEBHOOK_TOKEN="test-plusofon-token")
class UserSecurityTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.user = CustomUser.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password=self.password,
        )
        self.city = City.objects.create(slug="yakutsk", name="Yakutsk", timezone="Asia/Yakutsk", is_active=True)
        self.post = FeedPost.objects.create(
            city=self.city,
            author_user=self.user,
            type=FeedPost.Type.POST,
            body="Test post body",
        )

    def test_user_main_requires_auth_for_list(self):
        response = self.client.get(reverse("user_main"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_plusofon_rejects_request_without_signature(self):
        response = self.client.post(reverse("plusofon"), {"from": "+79991234567"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_plusofon_activates_user_with_valid_signature(self):
        pending_user = CustomUser.objects.create_user(
            username="pending@example.com",
            email="pending@example.com",
            password=self.password,
            phone="+79991234567",
            is_active=False,
        )
        response = self.client.post(
            reverse("plusofon"),
            {"from": "+79991234567"},
            HTTP_X_PLUSOFON_TOKEN="test-plusofon-token",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pending_user.refresh_from_db()
        self.assertTrue(pending_user.is_active)

    def test_city_feed_hide_allows_only_author_or_admin(self):
        intruder = CustomUser.objects.create_user(
            username="intruder@example.com",
            email="intruder@example.com",
            password=self.password,
        )
        hide_url = reverse("city-feed-hide", kwargs={"city_slug": self.city.slug, "pk": self.post.id})

        self.client.force_authenticate(user=intruder)
        intruder_response = self.client.post(hide_url)
        self.assertEqual(intruder_response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user)
        author_response = self.client.post(hide_url)
        self.assertEqual(author_response.status_code, status.HTTP_200_OK)

    def test_registration_cannot_elevate_account_type(self):
        payload = {
            "email": "newadmin@example.com",
            "password": self.password,
            "phone": "+79997654321",
            "account_type": "admin",
        }
        response = self.client.post(reverse("user_main"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        created_user = CustomUser.objects.get(email="newadmin@example.com")
        self.assertEqual(created_user.account_type, CustomUser.AccountType.USER)
