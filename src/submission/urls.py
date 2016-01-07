from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

	url(r'^book/new/stage/1/$', 'submission.views.start_submission', name='submission_start'),
	url(r'^book/(?P<book_id>\d+)/stage/1/$', 'submission.views.start_submission', name='edit_start'),
	url(r'^book/(?P<book_id>\d+)/stage/2/$', 'submission.views.submission_two', name='submission_two'),
	url(r'^book/(?P<book_id>\d+)/stage/3/$', 'submission.views.submission_three', name='submission_three'),
	url(r'^book/(?P<book_id>\d+)/stage/4/$', 'submission.views.submission_three_additional', name='submission_three_additional'),
	url(r'^book/(?P<book_id>\d+)/stage/5/$', 'submission.views.submission_four', name='submission_four'),
	url(r'^book/(?P<book_id>\d+)/stage/5/author/new/$', 'submission.views.author', name='author'),
	url(r'^book/(?P<book_id>\d+)/stage/5/author/(?P<author_id>\d+)/$', 'submission.views.author', name='author_edit'),
	url(r'^book/(?P<book_id>\d+)/stage/5/editor/new/$', 'submission.views.editor', name='editor'),
	url(r'^book/(?P<book_id>\d+)/stage/5/editor/(?P<editor_id>\d+)/$', 'submission.views.editor', name='editor_edit'),
	url(r'^book/(?P<book_id>\d+)/stage/6/$', 'submission.views.submission_five', name='submission_five'),
	url(r'^book/(?P<book_id>\d+)/stage/3/(?P<file_type>[-\w./]+)/$', 'submission.views.submission_additional_files', name='submission_additional_files'),

	# Ajax url
	url(r'^book/(?P<book_id>\d+)/order/(?P<type_to_handle>[-\w./]+)/$', 'submission.views.file_order', name='file_order'),
	url(r'^book/(?P<book_id>\d+)/type/(?P<type_to_handle>[-\w./]+)/upload/', 'submission.views.upload', name = 'jfu_upload' ),
	url(r'^book/(?P<book_id>\d+)/file/(?P<file_pk>\d+)/delete/$', 'submission.views.upload_delete', name = 'jfu_delete' ),



	url(r'^proposal/$', 'submission.views.start_proposal', name='proposal_start'),
	url(r'^proposal/(?P<proposal_id>\d+)/view/$', 'submission.views.proposal_view', name='proposal_view_submitted'),
	url(r'^proposal/(?P<proposal_id>\d+)/revisions/$', 'submission.views.proposal_revisions', name='proposal_revisions'),




)
