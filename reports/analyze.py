import calendar
from datetime import timedelta

from django.utils import timezone
import numpy as np

from tasks.models import Task


def analyze_weekly_trends(user_id):
    today = timezone.localtime(timezone.now())
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=7)
    start_of_period = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_period = end_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    tasks = Task.objects.filter(
        project__user_id=user_id,
        created_at__gte=start_of_period,
        created_at__lt=end_of_period,
        status=Task.DONE
    )

    # Tính số lượng tasks đã hoàn thành theo từng ngày trong tuần và từng giờ trong ngày
    day_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_tasks = np.zeros(7)
    hourly_tasks = np.zeros(24)
    for task in tasks:
        weekly_tasks[timezone.localtime(task.finish_at).weekday()] += 1
        hourly_tasks[timezone.localtime(task.finish_at).hour] += 1
    week_days_report = {day_of_week[day]: weekly_tasks[day] for day in range(7)}
    hours_report = {hour: hourly_tasks[hour] for hour in range(24)}

    peak_hour = np.argmax(hourly_tasks)
    peak_day = np.argmax(weekly_tasks)

    advice = f"Bạn hoàn thành nhiều công việc nhất vào ngày {['Thứ hai', 'Thứ ba', 'Thứ tư', 'Thứ năm', 'Thứ sáu', 'Thứ bảy', 'Chủ nhật'][peak_day]} và vào giờ {peak_hour}:00. " \
             "Hãy thử tập trung làm việc vào khoảng thời gian này để đạt hiệu suất cao nhất."

    return week_days_report, hours_report, advice


def analyze_monthly_trends(user_id):
    today = timezone.localtime(timezone.now())
    month = today.month
    year = today.year
    _, num_days_in_month = calendar.monthrange(year, month)

    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = start_of_month + timedelta(days=num_days_in_month)

    tasks = Task.objects.filter(
        project__user_id=user_id,
        created_at__gte=start_of_month,
        created_at__lt=end_of_month,
        status=Task.DONE
    )

    day_of_month = np.zeros(num_days_in_month + 1)
    for task in tasks:
        day_of_month[timezone.localtime(task.finish_at).day] += 1
    monthly_report = {day: day_of_month[day] for day in range(num_days_in_month)}
    peak_day = np.argmax(day_of_month)
    advice = f"Bạn hoàn thành nhiều công việc nhất vào ngày {peak_day} với số công việc hoàn thành là {day_of_month[peak_day]}. "

    return monthly_report, advice
