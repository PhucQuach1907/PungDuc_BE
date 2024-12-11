import uuid
from django.db import models
from django.utils import timezone

from accounts.models import CustomUser


# Create your models here.
class Report(models.Model):
    WEEKLY = 1
    MONTHLY = 2
    TYPE_CHOICES = [
        (WEEKLY, 'weekly'),
        (MONTHLY, 'monthly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_tasks = models.IntegerField()
    completed_tasks = models.IntegerField()
    pending_tasks = models.IntegerField()
    average_completion_time = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_analysis = models.JSONField(null=True, blank=True)
    monthly_analysis = models.JSONField(null=True, blank=True)
    type = models.IntegerField(choices=TYPE_CHOICES, default=WEEKLY)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Báo cáo {} - {}".format(timezone.localtime(self.start_time).strftime('%Y-%m-%d'),
                                        timezone.localtime(self.end_time).strftime('%Y-%m-%d'))

    class Meta:
        db_table = "reports"
        ordering = ['-created_at']
