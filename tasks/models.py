from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    class Priority(models.IntegerChoices):
        LOW = 1, "Žemas"
        MEDIUM = 2, "Vidutinis"
        HIGH = 3, "Aukštas"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    is_done = models.BooleanField(default=False)

    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "is_done"]),
            models.Index(fields=["user", "deleted_at"]),
            models.Index(fields=["user", "due_date"]),
            models.Index(fields=["user", "priority"]),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self):
        self.deleted_at = timezone.now()

    def restore(self):
        self.deleted_at = None

assigned_to = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="assigned_tasks"
)