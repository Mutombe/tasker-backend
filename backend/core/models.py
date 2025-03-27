from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_student = models.BooleanField(default=True)
    is_resident = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True)

    # Add related_name arguments to resolve accessor conflicts
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to.",
        related_name="core_user_set",
        related_query_name="core_user",
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="core_user_set",
        related_query_name="core_user",
    )

    def __str__(self):
        return self.username


class Task(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]
    resident = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=200)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    urgent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="applications"
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.title} - {self.student.username}"

    class Meta:
        unique_together = ("task", "student")

    def save(self, *args, **kwargs):
        if self.status == "accepted":
            self.task.status = "in_progress"
            self.task.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status == "accepted":
            self.task.status = "open"
            self.task.save()
        super().delete(*args, **kwargs)


class Review(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="reviews")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
