from django.urls import re_path

from .views import (
    dashboard,
    task_hub,
    task_hub_decline,
    upload,
    upload_author,
    upload_delete,
)

urlpatterns = [
    # Review
    re_path(
        r'^$',
        dashboard,
        name='onetasker_dashboard'
    ),
    re_path(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)$',
        task_hub,
        name='onetasker_task_hub'
    ),
    re_path(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)/decline/$',
        task_hub_decline,
        name='onetasker_task_hub_decline'
    ),
    re_path(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)/'
        r'(?P<about>[-\w]+)$',
        task_hub,
        name='onetasker_task_about'
    ),
    re_path(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)/'
        r'type/(?P<type_to_handle>[-\w./]+)/upload/',
        upload,
        name='assignment_jfu_upload'
    ),
    re_path(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)/'
        r'type/(?P<type_to_handle>[-\w./]+)/upload-author/',
        upload_author,
        name='assignment_jfu_upload_author'
    ),
    re_path(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)/'
        r'file/(?P<file_pk>\d+)/delete/$',
        upload_delete,
        name='assignment_jfu_delete'
    ),
]
