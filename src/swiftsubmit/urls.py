from django.conf.urls import url

from .views import (
    author,
    editor,
    formats,
    index,
    stage,
)

urlpatterns = [
    url(
        r'^$',
        index,
        name='swiftsubmit_index'
    ),
    url(
        r'^book/(?P<book_id>\d+)/formats/$',
        formats,
        name='swiftsubmit_formats'
    ),
    url(
        r'^book/(?P<book_id>\d+)/authors/$',
        author,
        name='swiftsubmit_authors'
    ),
    url(
        r'^book/(?P<book_id>\d+)/editors/$',
        editor,
        name='swiftsubmit_editors'
    ),
    url(
        r'^book/(?P<book_id>\d+)/stage/$',
        stage,
        name='swiftsubmit_stage'
    ),
]
