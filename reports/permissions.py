from rest_framework import permissions

from reports.models import Report


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Report):
            return obj.user == request.user
        return False
