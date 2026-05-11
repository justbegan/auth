from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.profile.models import Notification, UserProfile
from apps.user.models import CustomUser


class ProfileApiTests(APITestCase):
    def setUp(self):
        self.password = 'StrongPass123!'
        self.user = CustomUser.objects.create_user(
            username='profile@example.com',
            email='profile@example.com',
            password=self.password,
        )
        self.admin = CustomUser.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password=self.password,
            account_type=CustomUser.AccountType.ADMIN,
            is_staff=True,
        )

    def test_profile_me_creates_profile(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('profile-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_notification_mark_read_endpoint(self):
        notification = Notification.objects.create(
            user=self.user,
            type='system',
            title='Hello',
            body='World',
        )
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse('profile-notifications-mark-read', kwargs={'pk': notification.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertIsNotNone(notification.read_at)

    def test_audit_logs_are_admin_only(self):
        self.client.force_authenticate(self.user)
        forbidden_response = self.client.get(reverse('profile-audit-logs-list'))
        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.admin)
        allowed_response = self.client.get(reverse('profile-audit-logs-list'))
        self.assertEqual(allowed_response.status_code, status.HTTP_200_OK)
