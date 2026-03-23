from django.contrib import admin
from .models import Task
from django.utils.safestring import mark_safe


class DeletedFilter(admin.SimpleListFilter):
    title = "Būsena"
    parameter_name = "deleted"

    def lookups(self, request, model_admin):
        return (
            ("active", "Aktyvios"),
            ("deleted", "Ištrintos"),
        )

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(deleted_at__isnull=True)
        if self.value() == "deleted":
            return queryset.filter(deleted_at__isnull=False)
        return queryset


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "priority",
        "is_done",
        "due_date",
        "created_at",
        "deleted_status",
    )

    list_filter = (
        DeletedFilter,
        "priority",
        "is_done",
        "due_date",
        "created_at",
    )

    search_fields = (
        "title",
        "content",
        "user__username",
    )

    readonly_fields = (
        "created_at",
        "deleted_at",
    )

    ordering = ("-created_at",)

    def deleted_status(self, obj):
        if obj.deleted_at:
            return mark_safe('<span style="color:#dc3545;font-weight:600;">Ištrinta</span>')
        if obj.is_done:
            return mark_safe('<span style="color:#0d6efd;font-weight:600;">Atlikta</span>')
        return mark_safe('<span style="color:#198754;font-weight:600;">Vykdoma</span>')

    deleted_status.short_description = "Statusas"