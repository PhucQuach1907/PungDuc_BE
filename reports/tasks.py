import calendar
from datetime import timedelta

from celery import shared_task
from django.db.models import F
from django.utils import timezone

from accounts.models import CustomUser
from reports.analyze import analyze_weekly_trends, analyze_monthly_trends
from reports.models import Report
from tasks.models import Task


@shared_task
def create_weekly_report():
    users = CustomUser.objects.all()
    for user in users:
        today = timezone.localtime(timezone.now())
        start_of_period = today - timedelta(days=today.weekday()) - timedelta(days=7)
        end_of_period = start_of_period + timedelta(days=7)
        start_of_period = start_of_period.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_period = end_of_period.replace(hour=0, minute=0, second=0, microsecond=0)

        tasks = Task.objects.filter(
            created_at__gte=start_of_period,
            created_at__lt=end_of_period,
            project__user=user,
        )

        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status=Task.DONE).count()
        pending_tasks = tasks.filter(status=Task.DOING).count()
        average_completion_time = 0
        if completed_tasks > 0:
            completion_times = tasks.annotate(
                completion_time=F('finish_at') - F('created_at')
            ).values_list('completion_time', flat=True)

            total_time_in_seconds = sum((completion_time.total_seconds() for completion_time in completion_times), 0)
            average_completion_time = round(total_time_in_seconds / (completed_tasks * 3600), 2)

        week_days_report, hours_report, advice = analyze_weekly_trends(user.id)
        weekly_analysis = {'week_days_report': week_days_report, 'hours_report': hours_report, 'advice': advice}

        report = Report(
            start_time=start_of_period,
            end_time=end_of_period,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            average_completion_time=average_completion_time,
            weekly_analysis=weekly_analysis,
            monthly_analysis=None,
            user=user,
            type=1
        )
        report.save()


@shared_task
def create_monthly_report():
    users = CustomUser.objects.all()
    for user in users:
        today = timezone.localtime(timezone.now())
        start_of_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if today.month == 1:
            start_of_previous_month = start_of_current_month.replace(year=today.year - 1, month=12)
        else:
            start_of_previous_month = start_of_current_month.replace(month=today.month - 1)

        _, num_days_in_previous_month = calendar.monthrange(start_of_previous_month.year, start_of_previous_month.month)
        start_of_previous_month = start_of_previous_month.replace(day=1)
        end_of_previous_month = start_of_previous_month + timedelta(days=num_days_in_previous_month)
        tasks = Task.objects.filter(
            created_at__gte=start_of_previous_month,
            created_at__lt=end_of_previous_month,
            project__user=user,
        )

        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status=Task.DONE).count()
        pending_tasks = tasks.filter(status=Task.DOING).count()
        average_completion_time = 0
        if completed_tasks > 0:
            completion_times = tasks.annotate(
                completion_time=F('finish_at') - F('created_at')
            ).values_list('completion_time', flat=True)

            total_time_in_seconds = sum((completion_time.total_seconds() for completion_time in completion_times), 0)
            average_completion_time = round(total_time_in_seconds / (completed_tasks * 3600), 2)

        monthly_report, advice = analyze_monthly_trends(user.id)
        monthly_analysis = {'monthly_report': monthly_report, 'advice': advice}

        report = Report(
            start_time=start_of_previous_month,
            end_time=end_of_previous_month,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            average_completion_time=average_completion_time,
            weekly_analysis=None,
            monthly_analysis=monthly_analysis,
            user=user,
            type=2
        )
        report.save()
