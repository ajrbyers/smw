from django.contrib import admin
from models import Form, FormElement, FormResult, FormElementsRelationship


class FormAdmin(admin.ModelAdmin):
    list_display = ('name', 'ref')
    search_fields = ('name',)


class FormElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'field_type')


class FormElementsRelationshipAdmin(admin.ModelAdmin):
    list_display = ('form', 'element')


class FormResultAdmin(admin.ModelAdmin):
    list_display = ('form', 'date')


admin_list = [
    (Form, FormAdmin),
    (FormElement, FormElementAdmin),
    (FormResult, FormResultAdmin),
    (FormElementsRelationship, FormElementsRelationshipAdmin),
]

[admin.site.register(*t) for t in admin_list]
