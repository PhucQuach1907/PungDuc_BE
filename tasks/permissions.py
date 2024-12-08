from rest_framework import permissions
from .models import Project, TableColumn, Task


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            return obj.user == request.user
        elif isinstance(obj, TableColumn):
            return obj.project.user == request.user
        elif isinstance(obj, Task):
            return obj.project.user == request.user
        return False
