from django.urls import re_path

from .views import (
    author,
    editor,
    formats,
    index,
    stage,
)

urlpatterns = [
    re_path(
        r'^$',
        index,
        name='swiftsubmit_index'
    ),
    re_path(
        r'^book/(?P<book_id>\d+)/formats/$',
        formats,
        name='swiftsubmit_formats'
    ),
    re_path(
        r'^book/(?P<book_id>\d+)/authors/$',
        author,
        name='swiftsubmit_authors'
    ),
    re_path(
        r'^book/(?P<book_id>\d+)/editors/$',
        editor,
        name='swiftsubmit_editors'
    ),
    re_path(
        r'^book/(?P<book_id>\d+)/stage/$',
        stage,
        name='swiftsubmit_stage'
    ),
]
