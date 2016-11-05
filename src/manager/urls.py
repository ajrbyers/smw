from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

urlpatterns = patterns('',

                       # New Submissions
                       url(r'^$', 'manager.views.index', name='manager_index'),
                       url(r'^about/$', 'manager.views.about', name='manager_about'),

                       # Group Management
                       url(r'^groups/$', 'manager.views.groups', name='manager_groups'),
                       url(r'^groups/order/$', 'manager.views.groups_order', name='manager_groups_order'),
                       url(r'^groups/add/$', 'manager.views.group', name='manager_group_add'),
                       url(r'^groups/(?P<group_id>\d+)/edit/$', 'manager.views.group', name='manager_group_edit'),
                       url(r'^groups/(?P<group_id>\d+)/delete/$', 'manager.views.group_delete', name='manager_group_delete'),
                       url(r'^groups/(?P<group_id>\d+)/members/$', 'manager.views.group_members', name='manager_group_members'),
                       url(r'^groups/(?P<group_id>\d+)/members/user/(?P<user_id>\d+)/assign/$', 'manager.views.group_members_assign', name='group_members_assign'),
                       url(r'^groups/(?P<group_id>\d+)/members/order$', 'manager.views.group_members_order', name='group_members_order'),
                       url(r'^groups/(?P<group_id>\d+)/members/(?P<member_id>\d+)/delete$', 'manager.views.manager_membership_delete', name='manager_membership_delete'),

                       # Role Management
                       url(r'^roles/$', 'manager.views.roles', name='manager_roles'),
                       url(r'^roles/(?P<slug>[-\w.]+)/$', 'manager.views.role', name='manager_role'),
                       url(r'^roles/(?P<slug>[-\w.]+)/user/(?P<user_id>\d+)/(?P<action>[-\w.]+)/$', 'manager.views.role_action', name='manager_role_action'),

                       # Settings Management
                       url(r'^settings/$', 'manager.views.settings_index', name='settings_index'),
                       url(r'^settings/group/(?P<setting_group>[-\w.]+)/setting/(?P<setting_name>[-\w.]+)/$', 'manager.views.edit_setting', name='edit_setting'),

                       # Submission checklist
                       url(r'^submission/checklist/$', 'manager.views.submission_checklist', name='submission_checklist'),
                       url(r'^submission/checklist/edit/(?P<item_id>\d+)/$', 'manager.views.edit_submission_checklist', name='edit_submission_checklist'),
                       url(r'^submission/checklist/delete/(?P<item_id>\d+)/$', 'manager.views.delete_submission_checklist', name='delete_submission_checklist'),
                       url(r'^submission/checklist/order/$', 'manager.views.checklist_order', name='checklist_order'),

                       # Series Management
                       url(r'^series/$', 'manager.views.series', name='series'),
                       url(r'^series/add/$', 'manager.views.series_add', name='series_add'),
                       url(r'^series/delete/(?P<series_id>\d+)/$', 'manager.views.series_delete', name='series_delete'),
                       url(r'^series/(?P<series_id>\d+)/send/$', 'manager.views.send_series', name='series_send_series'),

                       url(r'^series/(?P<series_id>\d+)/edit/$', 'manager.views.series_edit', name='series_edit'),
                       url(r'^series/submission/(?P<submission_id>\d+)/series/add/(?P<series_id>\d+)/$', 'manager.views.series_submission_add', name='series_submission_add'),
                       url(r'^series/submission/(?P<submission_id>\d+)/series/remove/$', 'manager.views.series_submission_remove', name='series_submission_remove'),


                       # Cache
                       url(r'^cache/flush/$', 'manager.views.flush_cache', name='manager_flush_cache'),

                       # Users
                       url(r'^user/$', 'manager.views.users', name='manager_users'),
                       url(r'^user/inactive/$', 'manager.views.inactive_users', name='manager_inactive_users'),
                       url(r'^user/inactive/(?P<user_id>\d+)/activate/$', 'manager.views.activate_user', name='manager_activate_user'),
                       url(r'^user/add/$', 'manager.views.add_user', name='add_user'),
                       url(r'^user/(?P<user_id>\d+)/edit/$', 'manager.views.user_edit', name='user_edit'),
                       url(r'^user/(?P<user_id>\d+)/edit/select_merge/$', 'manager.views.select_merge', name='select_merge'),
                       url(r'^user/(?P<user_id>\d+)/edit/merge_users/(?P<secondary_user_id>\d+)/$', 'manager.views.merge_users', name='merge_users'),

                       # Key help
                       url(r'^key_help/$', 'manager.views.key_help', name='manager_key_help'),


                       # Forms
                       url(r'^forms/add/(?P<form_type>[-\w.]+)/$', 'manager.views.add_new_form', name='manager_add_new_form'),

                       url(r'^forms/proposal/$', 'manager.views.proposal_forms', name='manager_proposal_forms'),
                       url(r'^forms/proposal/(?P<form_id>\d+)/$', 'manager.views.edit_proposal_form', name='manager_edit_proposal_form'),
                       url(r'^forms/proposal/(?P<form_id>\d+)/switch/(?P<field_1_id>\d+)/(?P<field_2_id>\d+)$', 'manager.views.reorder_proposal_form', name='manager_reorder_proposal_form'),
                       url(r'^forms/proposal/(?P<form_id>\d+)/element/(?P<relation_id>\d+)/$', 'manager.views.edit_proposal_form', name='manager_edit_proposal_form_element'),
                       url(r'^forms/proposal/(?P<form_id>\d+)/element/(?P<relation_id>\d+)/delete/$', 'manager.views.delete_proposal_form_element', name='manager_delete_proposal_form_element'),
                       url(r'^forms/proposal/(?P<form_id>\d+)/preview/$', 'manager.views.preview_proposal_form', name='manager_preview_proposal_form'),

                       url(r'^forms/review/$', 'manager.views.review_forms', name='manager_review_forms'),
                       url(r'^forms/review/(?P<form_id>\d+)/$', 'manager.views.edit_review_form', name='manager_edit_review_form'),
                       url(r'^forms/review/(?P<form_id>\d+)/element/(?P<relation_id>\d+)/$', 'manager.views.edit_review_form', name='manager_edit_review_form_element'),
                       url(r'^forms/review/(?P<form_id>\d+)/switch/(?P<field_1_id>\d+)/(?P<field_2_id>\d+)$', 'manager.views.reorder_review_form', name='manager_reorder_review_form'),
                       url(r'^forms/review/(?P<form_id>\d+)/element/(?P<relation_id>\d+)/delete/$', 'manager.views.delete_review_form_element', name='manager_delete_review_form_element'),
                       url(r'^forms/review/(?P<form_id>\d+)/preview/$', 'manager.views.preview_review_form', name='manager_preview_review_form'),




                       )
