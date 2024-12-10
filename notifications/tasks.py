from datetime import timedelta

from celery import shared_task
from django.core.mail import EmailMessage
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.timezone import now

from PungDuc_BE import settings
from notifications.models import Notification
from tasks.models import Task


@shared_task
def send_deadline_notifications():
    tasks = Task.objects.filter(deadline__gte=now(), status=Task.DOING)

    for task in tasks:
        if Notification.objects.filter(task=task, sent=True, type='deadline').exists():
            continue

        time_left = task.deadline - now()

        if task.priority == Task.HIGH and time_left <= timedelta(days=1, hours=12):
            subject = f"Công việc sắp tới hạn (Ưu tiên cao)"
            html_message = render_to_string(
                'notifications/deadline_notification.html',
                {'task': task}
            )
            recipient_list = [task.project.user.email]
            from_email = settings.DEFAULT_FROM_EMAIL
            message = EmailMessage(subject, html_message, from_email, recipient_list)
            message.content_subtype = 'html'
            message.send()

            def create_notification():
                Notification.objects.create(task=task, sent=True, type='deadline')

            transaction.on_commit(create_notification)

        elif task.priority in [Task.MEDIUM, Task.LOW] and time_left <= timedelta(days=1):
            subject = f"Công việc sắp tới hạn"
            html_message = render_to_string(
                'notifications/deadline_notification.html',
                {'task': task}
            )
            recipient_list = [task.project.user.email]
            from_email = settings.DEFAULT_FROM_EMAIL
            message = EmailMessage(subject, html_message, from_email, recipient_list)
            message.content_subtype = 'html'
            message.send()

            def create_notification():
                Notification.objects.create(task=task, sent=True, type='deadline')

            transaction.on_commit(create_notification)


@shared_task
def send_notification_overdue_tasks():
    tasks = Task.objects.filter(deadline__lte=now(), status=Task.DOING)

    for task in tasks:
        if Notification.objects.filter(task=task, sent=True, type='overdue').exists():
            print(f"Notification already sent for task: {task.title}")
            continue

        subject = f"Công việc đã quá hạn: {task.title}"
        html_message = render_to_string(
            'notifications/overdue_task_notification.html',
            {'task': task}
        )
        recipient_list = [task.project.user.email]
        from_email = settings.DEFAULT_FROM_EMAIL
        message = EmailMessage(subject, html_message, from_email, recipient_list)
        message.content_subtype = 'html'
        message.send()

        def create_notification():
            Notification.objects.create(task=task, sent=True, type='overdue')

        transaction.on_commit(create_notification)
