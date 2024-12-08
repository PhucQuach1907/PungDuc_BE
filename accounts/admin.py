from django.contrib import admin

from accounts.models import CustomUser


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_superuser',
                    'oauth_provider', 'oauth_id', 'created_at', 'updated_at')
    search_fields = ('email',)
    list_filter = ('oauth_provider', 'is_staff', 'is_active', 'is_superuser')
