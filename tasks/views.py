from collections import defaultdict
from datetime import datetime, timedelta
from http import HTTPStatus

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from tasks.permissions import IsOwner
from tasks.serializers import *
from tasks.utils import Pagination, APIResponse, PaginationAPIResponse


# Create your views here.
class ProjectListView(generics.ListCreateAPIView):
    model = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = Pagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = {
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
                'page_size': self.paginator.page_size,
                'current_page': self.paginator.page.number
            }

            return PaginationAPIResponse(serializer.data, pagination=pagination)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(serializer.data)

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    model = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return APIResponse(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse(status_code=status.HTTP_200_OK)

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


class TableColumnListView(generics.ListAPIView):
    model = TableColumn.objects.all()
    serializer_class = GetTableColumnSerializer
    pagination_class = Pagination

    def list(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return APIResponse({
                'error': 'Project not found'
            }, status_code=status.HTTP_404_NOT_FOUND)
        project_serializer = ProjectSerializer(project)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = {
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
                'page_size': self.paginator.page_size,
                'current_page': self.paginator.page.number
            }

            return PaginationAPIResponse({
                'project': project_serializer.data,
                'table_columns': serializer.data
            }, pagination=pagination)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse({
            'project': project_serializer.data,
            'table_columns': serializer.data
        })

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return TableColumn.objects.filter(project_id=project_id)


class TableColumnCreateView(generics.CreateAPIView):
    model = TableColumn.objects.all()
    serializer_class = CreateUpdateDeleteTableColumnSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(serializer.data)


class CreateManyTableColumnView(generics.CreateAPIView):
    model = TableColumn
    serializer_class = CreateUpdateDeleteTableColumnSerializer

    def create(self, request, *args, **kwargs):
        columns_data = request.data

        if isinstance(columns_data, list):
            data = []
            serializers = [self.get_serializer(data=column_data) for column_data in columns_data]
            for serializer in serializers:
                serializer.is_valid(raise_exception=True)
            for serializer in serializers:
                self.perform_create(serializer)
                data.append(serializer.data)

            return APIResponse(data)
        else:
            return APIResponse(status_code=status.HTTP_400_BAD_REQUEST)


class TableColumnDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TableColumn.objects.all()
    serializer_class = CreateUpdateDeleteTableColumnSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return APIResponse(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse(status_code=status.HTTP_200_OK)


class TaskListView(generics.ListAPIView):
    model = Task.objects.all()
    serializer_class = GetTaskSerializer
    pagination_class = Pagination

    def list(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return APIResponse({
                'error': 'Project not found'
            }, status_code=status.HTTP_404_NOT_FOUND)

        project_serializer = ProjectSerializer(project)

        columns = TableColumn.objects.filter(project=project).order_by('order')

        tasks = Task.objects.filter(project=project).order_by('column__order')

        tasks_grouped_by_column = defaultdict(list)
        for task in tasks:
            tasks_grouped_by_column[task.column.id].append(task)

        column_data = []
        for column in columns:
            column_tasks = tasks_grouped_by_column.get(column.id, [])
            task_serializer = GetTaskSerializer(column_tasks, many=True)
            column_data.append({
                'column': {
                    'id': column.id,
                    'name': column.name,
                    'order': column.order,
                },
                'tasks': task_serializer.data
            })

        page = self.paginate_queryset(column_data)
        if page is not None:
            pagination = {
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
                'page_size': self.paginator.page_size,
                'current_page': self.paginator.page.number
            }
            return PaginationAPIResponse({
                'project': project_serializer.data,
                'columns': page,
            }, pagination=pagination)

        return APIResponse({
            'project': project_serializer.data,
            'columns': column_data,
        })

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Task.objects.filter(project_id=project_id)


class AllTaskListView(generics.ListAPIView):
    model = Task.objects.all()
    serializer_class = GetAllTaskSerializer
    pagination_class = Pagination

    def list(self, request, *args, **kwargs):
        time_param = request.GET.get('time')
        time_filter = None

        if time_param:
            try:
                time_filter = datetime.strptime(time_param, '%Y-%m-%d %H:%M:%S')
                time_filter = timezone.make_aware(time_filter)
            except ValueError:
                return APIResponse({"error": "Invalid time format, use 'YYYY-MM-DD HH:mm:ss'."},
                                   status_code=HTTPStatus.BAD_REQUEST)

        queryset = self.filter_queryset(self.get_queryset(time_filter))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = {
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
                'page_size': self.paginator.page_size,
                'current_page': self.paginator.page.number
            }
            return PaginationAPIResponse({
                'total_tasks': len(serializer.data),
                'tasks': serializer.data,
            }, pagination=pagination)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse({
            'total_tasks': len(serializer.data),
            'tasks': serializer.data,
        })

    def get_queryset(self, time_filter=None):
        return Task.objects.filter(project__user=self.request.user, deadline__gte=time_filter, status=1)


class OverdueTasksListView(generics.ListAPIView):
    model = Task.objects.all()
    serializer_class = GetAllTaskSerializer
    pagination_class = Pagination

    def list(self, request, *args, **kwargs):
        time_param = request.GET.get('time')
        time_filter = None

        if time_param:
            try:
                time_filter = datetime.strptime(time_param, '%Y-%m-%d %H:%M:%S')
                time_filter = timezone.make_aware(time_filter)
            except ValueError:
                return APIResponse({"error": "Invalid time format, use 'YYYY-MM-DD HH:mm:ss'."},
                                   status_code=HTTPStatus.BAD_REQUEST)

        queryset = self.filter_queryset(self.get_queryset(time_filter))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = {
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
                'page_size': self.paginator.page_size,
                'current_page': self.paginator.page.number
            }
            return PaginationAPIResponse({
                'total_tasks': len(serializer.data),
                'tasks': serializer.data,
            }, pagination=pagination)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse({
            'total_tasks': len(serializer.data),
            'tasks': serializer.data,
        })

    def get_queryset(self, time_filter=None):
        queryset = Task.objects.filter(project__user=self.request.user, status=3)
        if time_filter:
            queryset = queryset.filter(deadline__lt=time_filter)
        else:
            queryset = queryset.filter(deadline__lt=timezone.localtime(timezone.now()))

        return queryset


class OnDeadlineTasksListView(generics.ListAPIView):
    model = Task.objects.all()
    serializer_class = GetAllTaskSerializer
    pagination_class = Pagination

    def list(self, request, *args, **kwargs):
        time_param = request.GET.get('time')
        time_filter = None

        if time_param:
            try:
                time_filter = datetime.strptime(time_param, '%Y-%m-%d %H:%M:%S')
                time_filter = timezone.make_aware(time_filter)
            except ValueError:
                return APIResponse({"error": "Invalid time format, use 'YYYY-MM-DD HH:mm:ss'."},
                                   status_code=HTTPStatus.BAD_REQUEST)

        queryset = self.filter_queryset(self.get_queryset(time_filter))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            pagination = {
                'count': self.paginator.page.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
                'page_size': self.paginator.page_size,
                'current_page': self.paginator.page.number
            }
            return PaginationAPIResponse({
                'total_tasks': len(serializer.data),
                'tasks': serializer.data,
            }, pagination=pagination)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse({
            'total_tasks': len(serializer.data),
            'tasks': serializer.data,
        })

    def get_queryset(self, time_filter=None):
        queryset = Task.objects.filter(project__user=self.request.user, status=1)

        if time_filter:
            start_of_day = time_filter.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = time_filter.replace(hour=23, minute=59, second=59, microsecond=999999)

            queryset = queryset.filter(deadline__range=[start_of_day, end_of_day])

        return queryset


class TasksByMonthView(APIView):

    def get(self, request, *args, **kwargs):
        month = request.GET.get('month')
        year = request.GET.get('year')

        try:
            month = int(month)
            year = int(year)
        except (ValueError, TypeError):
            return APIResponse({"error": "Invalid month or year."}, status_code=400)

        if month < 1 or month > 12 or year < 1900:
            return APIResponse({"error": "Invalid month or year."}, status_code=400)

        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month != 12 else datetime(year + 1, 1, 1)

        start_date = timezone.make_aware(start_date, timezone.get_default_timezone())
        end_date = timezone.make_aware(end_date, timezone.get_default_timezone())

        tasks_by_day = {}

        current_date = start_date
        while current_date < end_date:
            start_of_day = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            doing_count = Task.objects.filter(deadline__gte=start_of_day, status=1, project__user=self.request.user,
                                              created_at__lte=end_of_day).count()
            on_deadline_count = Task.objects.filter(deadline__range=[start_of_day, end_of_day],
                                                    project__user=self.request.user).count()
            overdue_count = Task.objects.filter(deadline__lt=start_of_day, status=3,
                                                project__user=self.request.user).count()

            tasks_by_day[current_date.strftime('%Y-%m-%d')] = {
                'doing': doing_count,
                'on_deadline': on_deadline_count,
                'overdue': overdue_count
            }

            current_date += timedelta(days=1)

        return APIResponse(tasks_by_day)


class TasksByDateView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = GetDetailTasksSerializer

    def list(self, request, *args, **kwargs):
        time_param = request.GET.get('date')
        time_filter = None

        if time_param:
            try:
                time_filter = datetime.strptime(time_param, '%Y-%m-%d %H:%M:%S')
                time_filter = timezone.make_aware(time_filter)
            except ValueError:
                return APIResponse({"error": "Invalid time format, use 'YYYY-MM-DD HH:mm:ss'."},
                                   status_code=HTTPStatus.BAD_REQUEST)

        queryset = self.filter_queryset(self.get_queryset(time_filter))

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse({
            'total_tasks': len(serializer.data),
            'tasks': serializer.data,
        })

    def get_queryset(self, time_filter=None):
        return Task.objects.filter(project__user=self.request.user, deadline__gte=time_filter, status=1)


class TaskCreateView(generics.CreateAPIView):
    model = Task.objects.all()
    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(serializer.data)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        column_id = request.data.get("column")
        if column_id:
            try:
                column = TableColumn.objects.get(id=column_id)

                if column.is_done_column:
                    instance.status = Task.DONE
                    instance.finished_at = timezone.make_aware(instance.finished_at, timezone.get_default_timezone())
                else:
                    instance.status = Task.DOING
                    instance.finished_at = None
            except TableColumn.DoesNotExist:
                return APIResponse({'error': 'COLUMN_NOT_FOUND'}, status_code=HTTPStatus.NOT_FOUND)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return APIResponse(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse(status_code=status.HTTP_200_OK)
