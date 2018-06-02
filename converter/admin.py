from django.contrib import admin
from .models import DriveJob


class DriveJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'drive_shareable_link', 'quality', 'result_link')
    search_fields = ('drive_shareable_link', 'result_link', 'quality')
    readonly_fields = ('result_link', 'scheduled_job_id')
    list_filter = ('quality',)


admin.site.register(DriveJob, DriveJobAdmin)
