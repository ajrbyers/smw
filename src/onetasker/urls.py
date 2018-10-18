from django.conf.urls import url

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
    url(
        r'^$',
        dashboard,
        name='onetasker_dashboard'
    ),
    url(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)$',
        task_hub,
        name='onetasker_task_hub'
    ),
    url(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)/decline/$',
        task_hub_decline,
        name='onetasker_task_hub_decline'
    ),
    url(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)/'
        r'(?P<about>[-\w]+)$',
        task_hub,
        name='onetasker_task_about'
    ),
    url(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)/'
        r'type/(?P<type_to_handle>[-\w./]+)/upload/',
        upload,
        name='assignment_jfu_upload'
    ),
    url(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)/'
        r'type/(?P<type_to_handle>[-\w./]+)/upload-author/',
        upload_author,
        name='assignment_jfu_upload_author'
    ),
    url(
        r'^(?P<assignment_type>[-\w]+)/(?P<assignment_id>\d+)/'
        r'file/(?P<file_pk>\d+)/delete/$',
        upload_delete,
        name='assignment_jfu_delete'
    ),
]
