from django.contrib import admin
from models import Group, GroupMembership


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_type', 'active', 'sequence')
    list_filter = ('active',)
    search_fields = ('name',)


class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'added', 'sequence')


admin_list = [
    (Group, GroupAdmin),
    (GroupMembership, GroupMembershipAdmin),
]

[admin.site.register(*t) for t in admin_list]
