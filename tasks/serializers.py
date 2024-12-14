from rest_framework import serializers

from accounts.serializers import UserProfileSerializer
from tasks.models import Project, TableColumn, Task


class ProjectSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


class GetTableColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableColumn
        fields = ['id', 'name', 'order', 'created_at', 'updated_at']


class CreateUpdateDeleteTableColumnSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), write_only=True)

    class Meta:
        model = TableColumn
        fields = '__all__'

    def update(self, instance, validated_data):
        validated_data.pop('project', None)

        return super().update(instance, validated_data)


class GetTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'content', 'deadline', 'priority', 'status', 'finish_at', 'created_at', 'updated_at']


class GetDetailTasksSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'


class GetAllTaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    column = serializers.PrimaryKeyRelatedField(queryset=TableColumn.objects.all())

    class Meta:
        model = Task
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), write_only=True)
    column = serializers.PrimaryKeyRelatedField(queryset=TableColumn.objects.all(), write_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        
    def update(self, instance, validated_data):
        validated_data.pop('project', None)
        validated_data.pop('column', None)
        
        return super().update(instance, validated_data)
