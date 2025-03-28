from django.contrib import admin
from .models import User, Application, Task


class AdminUserOverview(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "phone",
    )
    search_fields = ("username",)


class AdminTaskOverview(admin.ModelAdmin):
    list_display = (
        "title",
        "address",
        "tasker",
    )
    search_fields = ("title",)


class AdminApplicationOverview(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "applicant",
        "status",
    )
    search_fields = ("task",)


admin.site.register(User, AdminUserOverview)
admin.site.register(Task, AdminTaskOverview)
admin.site.register(Application, AdminApplicationOverview)
