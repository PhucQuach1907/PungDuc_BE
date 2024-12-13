from django.urls import path

from tasks.views import *

urlpatterns = [
    path('project/', ProjectListView.as_view(), name='project_get_create'),
    path('project/<uuid:pk>/', ProjectDetailView.as_view(), name='project_update_delete'),
    path('column/get/<uuid:project_id>/', TableColumnListView.as_view(), name='column_get'),
    path('column/create/', TableColumnCreateView.as_view(), name='column_create'),
    path('column/create-many/', CreateManyTableColumnView.as_view(), name='column_create_many'),
    path('column/<uuid:pk>/', TableColumnDetailView.as_view(), name='column_update_delete'),
    path('task/get/<uuid:project_id>/', TaskListView.as_view(), name='task_get'),
    path('all-task/', AllTaskListView.as_view(), name='all_task_list'),
    path('overdue-tasks/', OverdueTasksListView.as_view(), name='overdue_task_list'),
    path('on-deadline-tasks/', OnDeadlineTasksListView.as_view(), name='on_deadline_task_list'),
    path('tasks-by-month/', TasksByMonthView.as_view(), name='tasks_by_month'),
    path('task/', TaskCreateView.as_view(), name='task_create'),
    path('task/<uuid:pk>/', TaskDetailView.as_view(), name='task_update_delete'),
]
