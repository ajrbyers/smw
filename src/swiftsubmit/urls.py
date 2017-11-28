from django.conf.urls import patterns
from django.conf.urls import url


urlpatterns = patterns(
    '',
    url(
        r'^$',
        'swiftsubmit.views.index',
        name='swiftsubmit_index'
    ),
    url(
        r'^book/(?P<book_id>\d+)/formats/$',
        'swiftsubmit.views.formats',
        name='swiftsubmit_formats'
    ),
    url(
        r'^book/(?P<book_id>\d+)/authors/$',
        'swiftsubmit.views.author',
        name='swiftsubmit_authors'
    ),
    url(
        r'^book/(?P<book_id>\d+)/editors/$',
        'swiftsubmit.views.editor',
        name='swiftsubmit_editors'
    ),
    url(
        r'^book/(?P<book_id>\d+)/stage/$',
        'swiftsubmit.views.stage',
        name='swiftsubmit_stage'
    ),
)
