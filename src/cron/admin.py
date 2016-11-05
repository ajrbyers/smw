from django.contrib import admin
from models import CronTask

class CronTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'schedule', 'enabled')
    search_fields = ('name',)


admin_list = [
    (CronTask, CronTaskAdmin),
]

[admin.site.register(*t) for t in admin_list]
