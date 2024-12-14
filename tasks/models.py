import uuid
from django.db import models
from accounts.models import CustomUser


# Create your models here.
class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tasks_projects'
        ordering = ['-created_at', 'name']


class TableColumn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    order = models.IntegerField(null=False, blank=False)
    is_done_column = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, editable=False, related_name='columns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tasks_table_columns'
        ordering = ['order', 'name']


class Task(models.Model):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
    ]
    DOING = 1
    DONE = 2
    OVERDUE = 3
    STATUS_CHOICES = [
        (DOING, 'Doing'),
        (DONE, 'Done'),
        (OVERDUE, 'Overdue'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, null=False, blank=False)
    content = models.TextField(null=True, blank=True)
    deadline = models.DateTimeField()
    priority = models.IntegerField(choices=PRIORITY_CHOICES)
    status = models.IntegerField(choices=STATUS_CHOICES)
    finish_at = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    column = models.ForeignKey(TableColumn, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'tasks'
        ordering = ['-deadline', '-priority', 'title']
