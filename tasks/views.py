from collections import defaultdict

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

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
                'total_tasks': len(serializer.data),
                'tasks': serializer.data,
            }, pagination=pagination)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse({
                'total_tasks': len(serializer.data),
                'tasks': serializer.data,
            })

    def get_queryset(self):
        return Task.objects.filter(project__user=self.request.user, deadline__gte=timezone.now())


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
