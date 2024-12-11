from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from reports.models import Report
from reports.permissions import IsOwner
from reports.serializers import ReportsSerializer, ReportDetailSerializer
from tasks.utils import PaginationAPIResponse, APIResponse, Pagination


# Create your views here.
class GetAllWeeklyReport(generics.ListAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportsSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(serializer.data)

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user, type=1)


class GetAllMonthlyReport(generics.ListAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportsSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(serializer.data)

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user, type=2)


class GetDetailReport(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportDetailSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Report.objects.filter(id=self.kwargs['pk'])
