from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Task


User = get_user_model()


class TaskSecurityTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass12345")
        self.u2 = User.objects.create_user(username="u2", password="pass12345")
        self.t1 = Task.objects.create(user=self.u1, title="A", content="")
        self.t2 = Task.objects.create(user=self.u2, title="B", content="")

    def test_user_sees_only_own_tasks(self):
        self.client.login(username="u1", password="pass12345")
        res = self.client.get(reverse("tasks:task_list"))
        self.assertContains(res, "A")
        self.assertNotContains(res, "B")

    def test_user_cannot_delete_other_users_task(self):
        self.client.login(username="u1", password="pass12345")
        url = reverse("tasks:task_delete", args=[self.t2.pk])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 404)

    def test_toggle_requires_post(self):
        self.client.login(username="u1", password="pass12345")
        url = reverse("tasks:task_toggle", args=[self.t1.pk])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 405)