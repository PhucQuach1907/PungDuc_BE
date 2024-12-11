from rest_framework import serializers

from accounts.serializers import UserProfileSerializer
from reports.models import Report


class ReportsSerializer(serializers.ModelSerializer):
    report_name = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id', 'start_time', 'end_time', 'report_name']

    def get_report_name(self, obj):
        return str(obj)


class ReportDetailSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Report
        fields = '__all__'
