
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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


class ServiceRequestResolutionTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="resolutionuser",
            password="testpassword123",
        )

        self.category = Category.objects.create(
            name="Network Support",
            description="Network-related issues",
        )

        self.service_request = ServiceRequest.objects.create(
            title="Internet connection issue",
            description="Internet is not working.",
            category=self.category,
            requester=self.user,
        )

    def test_resolution_summary_is_blank_by_default(self):
        self.assertEqual(self.service_request.resolution_summary, "")

    def test_resolved_at_is_nullable(self):
        self.assertIsNone(self.service_request.resolved_at)

    def test_resolved_request_requires_resolution_date(self):
        self.service_request.status = ServiceRequest.Status.RESOLVED
        self.service_request.resolution_summary = "Router was restarted."

        with self.assertRaises(ValidationError):
            self.service_request.full_clean()

    def test_resolved_request_requires_resolution_summary(self):
        self.service_request.status = ServiceRequest.Status.RESOLVED
        self.service_request.resolved_at = timezone.now()
        self.service_request.resolution_summary = ""

        with self.assertRaises(ValidationError):
            self.service_request.full_clean()

    def test_closed_request_requires_resolution_details(self):
        self.service_request.status = ServiceRequest.Status.CLOSED

        with self.assertRaises(ValidationError):
            self.service_request.full_clean()

    def test_resolved_request_with_required_details_passes_validation(self):
        self.service_request.status = ServiceRequest.Status.RESOLVED
        self.service_request.resolved_at = timezone.now()
        self.service_request.resolution_summary = (
            "The internet connection was restored successfully."
        )

        self.service_request.full_clean()

    def test_open_request_does_not_require_resolution_details(self):
        self.service_request.status = ServiceRequest.Status.OPEN

        self.service_request.full_clean()

    def test_resolution_fields_can_be_saved(self):
        self.service_request.status = ServiceRequest.Status.RESOLVED
        self.service_request.resolved_at = timezone.now()
        self.service_request.resolution_summary = "Issue fixed."

        self.service_request.save()

        self.service_request.refresh_from_db()

        self.assertEqual(
            self.service_request.resolution_summary,
            "Issue fixed.",
        )
        self.assertIsNotNone(self.service_request.resolved_at)
