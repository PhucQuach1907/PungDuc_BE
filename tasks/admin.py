from django.contrib import admin
from .models import Project, TableColumn, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'created_at', 'updated_at')
    search_fields = ('name', 'user__email')
    list_filter = ('created_at',)


@admin.register(TableColumn)
class TableColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order', 'project', 'created_at')
    search_fields = ('name', 'project__name')
    list_filter = ('created_at',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'priority', 'project', 'column', 'deadline', 'created_at')
    search_fields = ('title', 'project__name', 'column__name')
    list_filter = ('priority', 'deadline', 'created_at')
