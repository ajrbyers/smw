from django.contrib import admin
from models import *


class RevisionAdmin(admin.ModelAdmin):
    list_display = ('book',)

admin_list = [
    (Revision, RevisionAdmin),
]

[admin.site.register(*t) for t in admin_list]
