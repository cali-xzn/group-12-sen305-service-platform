
from django.contrib import admin

from .models import Category, ServiceRequest, WorkOrder, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "requester",
        "status",
        "priority",
        "due_at",
        "resolved_at",
        "created_at",
    )

    list_filter = ("status", "priority", "category")
    search_fields = ("title", "description", "resolution_summary")
    readonly_fields = ("created_at", "updated_at")

    ordering = ("-created_at",)

    fieldsets = (
        ("Request Information", {
            "fields": (
                "title",
                "description",
                "category",
                "requester",
                "status",
                "priority",
            )
        }),
        ("Service Level", {
            "fields": ("due_at",)
        }),
        ("Resolution Information", {
            "fields": ("resolved_at", "resolution_summary")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = (
        "service_request",
        "technician",
        "started_at",
        "completed_at",
        "created_at",
    )

    search_fields = ("service_request__title", "technician__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "service_request",
        "author",
        "is_internal",
        "created_at",
    )

    list_filter = ("is_internal",)
    search_fields = ("body", "author__username")
