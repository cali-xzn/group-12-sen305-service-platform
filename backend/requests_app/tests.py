
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.utils import timezone

from .models import Category, ServiceRequest


class ServiceRequestDueDateTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

        self.category = Category.objects.create(
            name="Technical Support",
            description="Technical issues",
        )

        self.service_request = ServiceRequest.objects.create(
            title="Computer repair",
            description="My computer is not working.",
            category=self.category,
            requester=self.user,
        )

    def test_due_at_is_nullable(self):
        self.assertIsNone(self.service_request.due_at)

    def test_due_at_accepts_a_date_and_time(self):
        due_date = timezone.now() + timedelta(days=3)

        self.service_request.due_at = due_date
        self.service_request.save()

        self.service_request.refresh_from_db()

        self.assertEqual(self.service_request.due_at, due_date)

    def test_due_at_field_allows_null_and_blank(self):
        field = ServiceRequest._meta.get_field("due_at")

        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_status_due_at_index_exists(self):
        indexes = ServiceRequest._meta.indexes

        index_exists = any(
            index.name == "req_status_due_idx"
            and index.fields == ["status", "due_at"]
            for index in indexes
        )

        self.assertTrue(index_exists)

    def test_status_due_at_database_index_exists(self):
        table_name = ServiceRequest._meta.db_table

        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(
                cursor,
                table_name,
            )

        index_exists = any(
            constraint.get("index")
            and constraint.get("columns") == ["status", "due_at"]
            for constraint in constraints.values()
        )

        self.assertTrue(index_exists)
