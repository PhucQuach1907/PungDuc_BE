import uuid
from django.db import models

from tasks.models import Task


# Create your models here.
class Notification(models.Model):
    TYPE_CHOICES = [
        ('deadline', 'Deadline sắp tới'),
        ('overdue', 'Quá hạn'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return f"Notification for {self.task.title} - {self.type}"

    class Meta:
        db_table = 'notifications'
        ordering = ['-sent_date']
