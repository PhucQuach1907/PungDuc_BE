import calendar
from datetime import timedelta

from django.utils import timezone
import numpy as np

from tasks.models import Task


def analyze_weekly_trends(user_id, start_of_period, end_of_period):
    tasks = Task.objects.filter(
        project__user_id=user_id,
        finish_at__gte=start_of_period,
        finish_at__lt=end_of_period,
        status=Task.DONE
    )

    # Tính số lượng tasks đã hoàn thành theo từng ngày trong tuần và từng giờ trong ngày
    day_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_tasks = np.zeros(7)
    hourly_tasks = np.zeros(24)
    for task in tasks:
        finish_time = timezone.localtime(task.finish_at)
        weekly_tasks[finish_time.weekday()] += 1
        hourly_tasks[finish_time.hour] += 1
    week_days_report = {day_of_week[day]: weekly_tasks[day] for day in range(7)}
    hours_report = {hour: hourly_tasks[hour] for hour in range(24)}

    peak_hour = np.argmax(hourly_tasks)
    peak_day = np.argmax(weekly_tasks)

    advice = f"Bạn hoàn thành nhiều công việc nhất vào ngày {['Thứ hai', 'Thứ ba', 'Thứ tư', 'Thứ năm', 'Thứ sáu', 'Thứ bảy', 'Chủ nhật'][peak_day]} và vào giờ {peak_hour}:00. " \
             "Hãy thử tập trung làm việc vào khoảng thời gian này để đạt hiệu suất cao nhất."

    return week_days_report, hours_report, advice


def analyze_monthly_trends(user_id, start_of_month, end_of_month, num_days_in_month):
    tasks = Task.objects.filter(
        project__user_id=user_id,
        finish_at__gte=start_of_month,
        finish_at__lt=end_of_month,
        status=Task.DONE
    )

    day_of_month = np.zeros(num_days_in_month + 1)
    for task in tasks:
        day_of_month[timezone.localtime(task.finish_at).day] += 1
    monthly_report = {day + 1: day_of_month[day] for day in range(num_days_in_month)}
    peak_day = np.argmax(day_of_month)
    advice = f"Bạn hoàn thành nhiều công việc nhất vào ngày {peak_day} với số công việc hoàn thành là {day_of_month[peak_day]}. "

    return monthly_report, advice
