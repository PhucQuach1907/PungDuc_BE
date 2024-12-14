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

        tasks_created_in_week = Task.objects.filter(
            created_at__gte=start_of_period,
            created_at__lt=end_of_period,
            project__user=user,
        ).order_by('id')

        tasks_finished_in_week = Task.objects.filter(
            finish_at__gte=start_of_period,
            finish_at__lt=end_of_period,
            project__user=user,
        ).order_by('id')

        overdue_tasks_in_week = Task.objects.filter(
            deadline__gte=start_of_period,
            deadline__lte=end_of_period,
            status=3,
            project__user=user,
        ).order_by('id')

        tasks = tasks_created_in_week | tasks_finished_in_week | overdue_tasks_in_week
        tasks = tasks.distinct('id')

        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status=Task.DONE).count()
        pending_tasks = tasks.filter(status=Task.DOING).count()
        overdue_tasks = overdue_tasks_in_week.count()
        average_completion_time = 0
        if completed_tasks > 0:
            completion_times = tasks.annotate(
                completion_time=F('finish_at') - F('created_at')
            ).values_list('completion_time', flat=True)

            total_time_in_seconds = sum((completion_time.total_seconds() for completion_time in completion_times), 0)
            average_completion_time = round(total_time_in_seconds / (completed_tasks * 3600), 2)

        week_days_report, hours_report, advice = analyze_weekly_trends(user.id, start_of_period, end_of_period)
        week_days_report = [
            ('Monday', week_days_report['Monday']),
            ('Tuesday', week_days_report['Tuesday']),
            ('Wednesday', week_days_report['Wednesday']),
            ('Thursday', week_days_report['Thursday']),
            ('Friday', week_days_report['Friday']),
            ('Saturday', week_days_report['Saturday']),
            ('Sunday', week_days_report['Sunday'])
        ]
        weekly_analysis = {'week_days_report': week_days_report, 'hours_report': hours_report, 'advice': advice}

        report = Report(
            start_time=start_of_period,
            end_time=end_of_period,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            overdue_tasks=overdue_tasks,
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
        tasks_created_in_month = Task.objects.filter(
            created_at__gte=start_of_previous_month,
            created_at__lt=end_of_previous_month,
            project__user=user,
        ).order_by('id')

        tasks_finished_in_month = Task.objects.filter(
            finish_at__gte=start_of_previous_month,
            finish_at__lt=end_of_previous_month,
            project__user=user,
        ).order_by('id')

        overdue_tasks_in_month = Task.objects.filter(
            deadline__gte=start_of_previous_month,
            deadline__lte=end_of_previous_month,
            status=3,
            project__user=user,
        ).order_by('id')

        tasks = tasks_created_in_month | tasks_finished_in_month | overdue_tasks_in_month
        tasks = tasks.distinct('id')

        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status=Task.DONE).count()
        pending_tasks = tasks.filter(status=Task.DOING).count()
        overdue_tasks = overdue_tasks_in_month.count()
        average_completion_time = 0
        if completed_tasks > 0:
            completion_times = tasks.annotate(
                completion_time=F('finish_at') - F('created_at')
            ).values_list('completion_time', flat=True)

            total_time_in_seconds = sum((completion_time.total_seconds() for completion_time in completion_times), 0)
            average_completion_time = round(total_time_in_seconds / (completed_tasks * 3600), 2)

        monthly_report, advice = analyze_monthly_trends(user.id, start_of_month=start_of_previous_month, end_of_month=end_of_previous_month, num_days_in_month=num_days_in_previous_month)
        monthly_analysis = {'monthly_report': monthly_report, 'advice': advice}

        report = Report(
            start_time=start_of_previous_month,
            end_time=end_of_previous_month,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            overdue_tasks=overdue_tasks,
            average_completion_time=average_completion_time,
            weekly_analysis=None,
            monthly_analysis=monthly_analysis,
            user=user,
            type=2
        )
        report.save()
