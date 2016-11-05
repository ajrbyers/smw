from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

urlpatterns = patterns('',

                       # Core Site
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^submission/', include('submission.urls')),
                       url(r'^manager/', include('manager.urls')),
                       url(r'^review/', include('review.urls')),
                       url(r'^api/', include('api.urls')),
                       url(r'^author/', include('author.urls')),
                       url(r'^editor/', include('editor.urls')),
                       url(r'^tasks/', include('onetasker.urls')),
                       url(r'^swiftsubmit/', include('swiftsubmit.urls')),
                       url(r'^editorial_review/', include('editorialreview.urls')),

                       # 3rd Party Apps
                       url(r'^summernote/', include('django_summernote.urls')),
                       url(r'^accounts/', include('allauth.urls')),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

                       # Public pages
                       url(r'^$', 'core.views.index', name='index'),
                       url(r'^contact/$', 'core.views.contact', name='contact'),
                       url(r'^page/(?P<page_name>[-\w]+)/$', 'core.views.page', name='page'),


                       # Login/Register
                       url(r'^login/$', 'core.views.login', name='login'),
                       url(r'^login/orcid/$', 'core.views.login_orcid', name='orcid-login'),
                       url(r'^logout/$', 'core.views.logout', name='logout'),
                       url(r'^switch/account/$', 'core.views.switch_account', name='switch-account'),

                       url(r'^switch/account/(?P<account_id>\d+)/$', 'core.views.switch_account_user', name='switch-account-user'),
                       url(r'^register/$', 'core.views.register', name='register'),
                       url(r'^login/activate/(?P<code>[-\w./]+)/$', 'core.views.activate', name='activate'),

                       # Unauthenticated password reset
                       url(r'^login/reset/$', 'core.views.unauth_reset', name='unauth_reset'),
                       url(r'^login/reset/code/(?P<uuid>[\w-]+)/$', 'core.views.unauth_reset_code', name='unauth_reset_code'),
                       url(r'^login/reset/password/(?P<uuid>[\w-]+)/$', 'core.views.unauth_reset_password', name='unauth_reset_password'),

                       # User profile
                       url(r'^user/profile/$', 'core.views.view_profile', name='view_profile'),
                       url(r'^user/view/(?P<user_id>[-\w]+)/$', 'core.views.view_profile_readonly', name='view_profile_readonly'),
                       url(r'^user/review-history/(?P<user_id>[-\w]+)/$', 'core.views.view_review_history', name='view_review_history'),
                       url(r'^user/profile/update/$', 'core.views.update_profile', name='update_profile'),
                       url(r'^user/profile/resetpassword/$', 'core.views.reset_password', name='reset_password'),
                       url(r'^user/task/new/$', 'core.views.task_new', name='task_new'),
                       url(r'^user/task/(?P<task_id>[-\w./]+)/complete/$', 'core.views.task_complete', name='task_complete'),

                       # Message AJAX
                       url(r'^book/(?P<submission_id>\d+)/message/new/$', 'core.views.new_message', name='new_message'),
                       url(r'^book/(?P<submission_id>\d+)/messages/$', 'core.views.get_messages', name='get_messages'),


                       # User submission
                       url(r'^user/submission/(?P<submission_id>\d+)/$', 'core.views.user_submission', name='user_submission'),
                       url(r'^user/proposal/(?P<proposal_id>\d+)/$', 'core.views.user_proposal', name='user_proposal'),

                       url(r'overview/$', 'core.views.overview', name='overview'),
                       url(r'overview/inprogress/$', 'core.views.overview_inprogress', name='overview_inprogress'),
                       url(r'overview/proposals/$', 'core.views.proposal_overview', name='proposal_overview'),

                       # Email
                       url(r'^email/(?P<group>[-\w]+)/submission/(?P<submission_id>\d+)/$', 'core.views.email_users', name='email_users'),
                       url(r'^email/(?P<group>[-\w]+)/submission/(?P<submission_id>\d+)/user/(?P<user_id>\d+)/$', 'core.views.email_users', name='email_user'),
                       url(r'^email/proposal/(?P<proposal_id>\d+)/user/(?P<user_id>\d+)/$', 'core.views.email_users_proposal', name='email_user_proposal'),
                       url(r'^email/primary-contact/$', 'core.views.email_primary_contact', name='email_primary_contact'),

                       url(r'^email/get/user/proposal/(?P<proposal_id>\d+)/$', 'core.views.get_proposal_users', name='get_proposal_users'),
                       url(r'^email/get/authors/submission/(?P<submission_id>\d+)/$', 'core.views.get_authors', name='get_authors'),
                       url(r'^email/get/editors/submission/(?P<submission_id>\d+)/$', 'core.views.get_editors', name='get_editors'),
                       url(r'^email/get/users/$', 'core.views.get_all_users', name='get_all_users'),
                       url(r'^email/get/onetaskers/submission/(?P<submission_id>\d+)/$', 'core.views.get_onetaskers', name='get_onetaskers'),
                       url(r'^email/get/all/submission/(?P<submission_id>\d+)/$', 'core.views.get_all', name='get_all'),
                       url(r'^email/general/$', 'core.views.email_general', name='email_general'),
                       url(r'^email/general/user/(?P<user_id>\d+)/$', 'core.views.email_general', name='email_general_user_id'),

                       # Files
                       url(r'^files/submission/(?P<submission_id>\d+)/get/marc21/(?P<type>[-\w]+)/$', 'core.views.serve_marc21_file', name='serve_marc21_file'),
                       url(r'^files/proposal/(?P<proposal_id>\d+)/file/(?P<file_id>\d+)/download/$', 'core.views.serve_proposal_file_id', name='serve_proposal_file_id'),

                       url(r'^files/user/submission/(?P<submission_id>\d+)/file/(?P<file_id>\d+)/download/review/(?P<review_id>\d+)/access-key/(?P<access_key>[-\w+]+)/$', 'core.views.serve_file_one_click', name='serve_file_one_click'),
                       url(r'^files/user/submission/(?P<submission_id>\d+)/file/(?P<file_id>\d+)/download/$', 'core.views.serve_file', name='serve_file'),
                       url(r'^files/user/submission/(?P<submission_id>\d+)/files/download/$', 'core.views.serve_all_files', name='serve_all_files'),
                       url(r'^files/user/submission/(?P<submission_id>\d+)/review-files/(?P<review_type>[-\w]+)/download/review/(?P<review_id>\d+)/access-key/(?P<access_key>[-\w+]+)/$', 'core.views.serve_all_review_files_one_click', name='serve_all_review_files_one_click'),
                       url(r'^files/user/submission/(?P<submission_id>\d+)/review-files/(?P<review_type>[-\w]+)/download/$', 'core.views.serve_all_review_files', name='serve_all_review_files'),
                       url(r'^files/submission/(?P<submission_id>\d+)/file/upload/additional/$', 'core.views.upload_additional', name='upload_additional'),
                       url(r'^files/submission/(?P<submission_id>\d+)/file/upload/manuscript/$', 'core.views.upload_manuscript', name='upload_manuscript'),
                       url(r'^files/submission/(?P<submission_id>\d+)/file/(?P<revision_id>\d+)/download_versioned_file/$', 'core.views.serve_versioned_file', name='serve_versioned_file'),
                       url(r'^files/submission/(?P<submission_id>\d+)/file/(?P<file_id>\d+)/delete/returner/(?P<returner>[-\w]+)/$', 'core.views.delete_file', name='delete_file'),
                       url(r'^files/submission/(?P<submission_id>\d+)/file/(?P<file_id>\d+)/view/$', 'core.views.view_file', name='view_file'),
                       url(r'^files/submission/(?P<submission_id>\d+)/file/(?P<file_id>\d+)/update/returner/(?P<returner>[-\w]+)/$', 'core.views.update_file', name='update_file'),
                       url(r'^files/submission/(?P<submission_id>\d+)/file/(?P<file_id>\d+)/versions/$', 'core.views.versions_file', name='versions_file'),

                       # log
                       url(r'^log/submission/(?P<submission_id>\d+)/', 'core.views.view_log', name='view_log'),
                       url(r'^log/proposal/(?P<proposal_id>\d+)/', 'core.views.view_proposal_log', name='view_proposal_log'),

                       # redirect to correct dashboard
                       url(r'^dashboard/$', 'core.views.dashboard', name='user_dashboard'),
                       url(r'^misc_files/(?P<submission_id>\d+)/upload/$', 'core.views.upload_misc_file', name='upload_misc_file'),

                       # Proposals
                       url(r'^proposals/$', 'core.views.proposal', name='proposals'),
                       url(r'^proposals/filter/(?P<user_id>\d+)/$', 'core.views.proposal', name='proposals_filtered'),
                       url(r'^proposals/unassigned/$', 'core.views.assign_proposal', name='proposal_assign'),
                       url(r'^proposals/unassigned/(?P<proposal_id>\d+)/edit/$', 'core.views.proposal_assign_edit', name='proposal_assign_edit'),

                       url(r'^proposals/assign/(?P<proposal_id>\d+)/$', 'core.views.proposal_assign_view', name='proposal_assign_view_submitted'),
                       url(r'^proposals/assign/(?P<proposal_id>\d+)/(?P<user_id>\d+)/$', 'core.views.proposal_assign_user', name='proposal_assign_user'),

                       url(r'^proposals/history/$', 'core.views.proposal_history', name='proposals_history'),
                       url(r'^proposals/(?P<proposal_id>\d+)/$', 'core.views.view_proposal', name='view_proposal'),
                       url(r'^proposals/(?P<proposal_id>\d+)/add/editor/$', 'core.views.proposal_add_editors', name='proposal_add_editors'),
                       url(r'^proposals/(?P<proposal_id>\d+)/update/editor/$', 'core.views.proposal_add_editors', name='proposal_update_editors'),

                       url(r'^proposals/(?P<proposal_id>\d+)/review/start/$', 'core.views.start_proposal_review', name='start_proposal_review'),
                       url(r'^proposals/(?P<proposal_id>\d+)/review/add/$', 'core.views.add_proposal_reviewers', name='add_proposal_reviewers'),
                       url(r'^proposals/(?P<proposal_id>\d+)/assignment/decision/(?P<assignment_id>\d+)/access_key/(?P<access_key>[-\w+]+)/$', 'core.views.view_proposal_review_decision', name='view_proposal_review_decision_access_key'),
                       url(r'^proposals/(?P<proposal_id>\d+)/assignment/decision/(?P<assignment_id>\d+)/$', 'core.views.view_proposal_review_decision', name='view_proposal_review_decision'),
                       url(r'^proposals/(?P<proposal_id>\d+)/assignment/(?P<assignment_id>\d+)/access_key/(?P<access_key>[-\w+]+)/$', 'core.views.view_proposal_review', name='view_proposal_review_access_key'),
                       url(r'^proposals/(?P<proposal_id>\d+)/assignment/(?P<assignment_id>\d+)/$', 'core.views.view_proposal_review', name='view_proposal_review'),
                       url(r'^proposals/(?P<proposal_id>\d+)/assignment/(?P<assignment_id>\d+)/hide/$', 'core.views.hide_review', name='hide_proposal_review'),
                       url(r'^proposals/(?P<proposal_id>\d+)/assignment/(?P<assignment_id>\d+)/completed/$', 'core.views.view_completed_proposal_review', name='view_completed_proposal_review'),
                       url(r'^proposals/(?P<proposal_id>\d+)/remove/assignment/(?P<review_id>\d+)/$', 'core.views.remove_proposal_review', name='remove_proposal_review'),
                       url(r'^proposals/(?P<proposal_id>\d+)/withdraw/assignment/(?P<review_id>\d+)/$', 'core.views.withdraw_proposal_review', name='withdraw_proposal_review'),
                       url(r'^proposals/(?P<proposal_id>\d+)/assignment/(?P<assignment_id>\d+)/reopen/$', 'core.views.reopen_proposal_review', name='reopen_proposal_review'),
                       url(r'^proposals/(?P<proposal_id>\d+)/assignment/(?P<assignment_id>\d+)/due/$', 'core.views.change_review_due_date', name='change_review_due_date'),
                       url(r'^proposals/(?P<proposal_id>\d+)/accept/$', 'core.views.accept_proposal', name='accept_proposal'),
                       url(r'^proposals/(?P<proposal_id>\d+)/revisions/$', 'core.views.request_proposal_revisions', name='request_proposal_revisions'),
                       url(r'^proposals/(?P<proposal_id>\d+)/decline/$', 'core.views.decline_proposal', name='decline_proposal'),
                       url(r'^proposals/review-submitted/$', 'core.views.proposal_review_submitted', name='proposal_review_submitted'),
                       url(r'^proposals/review-declined/$', 'core.views.proposal_review_declined', name='proposal_review_declined'),
                       # Contract
                       url(r'^proposals/(?P<proposal_id>\d+)/manage/contract/$', 'core.views.contract_manager', name='proposal_contract_manager'),
                       url(r'^proposals/(?P<proposal_id>\d+)/manage/contract/(?P<contract_id>\d+)/$', 'core.views.contract_manager', name='proposal_contract_manager_edit'),

                       # OAI - /oai?verb=ListRecords&metadataPrefix=oai_dc
                       url(r'^oai/$', 'core.views.oai', name='oai'),

                       )

handler403 = 'core.views.permission_denied'

# Allow Django to serve static content only in debug/dev mode
if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
                            url(r'^404/$', TemplateView.as_view(template_name='404.html')),
                            url(r'^500/$', TemplateView.as_view(template_name='500.html')),
                            )
