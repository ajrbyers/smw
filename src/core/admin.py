from django.contrib import admin

import models as m


class AuthorAdmin(admin.ModelAdmin):

    list_display = (
        'author_email', 'first_name', 'last_name', 'orcid', 'institution'
    )
    search_fields = ('author_email', 'first_name', 'last_name')


class ProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'institution', 'date_confirmed')
    search_fields = ('orcid', 'institution', 'biography',)


class NoteAdmin(admin.ModelAdmin):

    list_display = ('text', 'date_last_updated', 'date_submitted')
    search_fields = ('text',)


class BookAdmin(admin.ModelAdmin):

    list_display = ('title', 'license')
    search_fields = ('title', 'doi', 'publication_date')
    save_as = True


class LicenseAdmin(admin.ModelAdmin):

    list_display = ('name', 'short_name', 'version', 'url')
    search_fields = ('name', 'short_name' 'version')


class TaskAdmin(admin.ModelAdmin):

    list_display = ('assignee', 'creator', 'text', 'workflow')
    list_filter = ('workflow', 'assignee')
    search_fields = ('text',)


class LogAdmin(admin.ModelAdmin):

    list_display = ('book', 'user', 'kind', 'date_logged')
    list_filter = ('kind', 'book')
    search_fields = ('message',)


class SettingAdmin(admin.ModelAdmin):

    list_display = ('name', 'group', 'types')
    list_filter = ('group', 'types')


class RoleAdmin(admin.ModelAdmin):

    list_display = ('name',)
    search_fields = ('name',)


class ReviewAssAdmin(admin.ModelAdmin):

    list_display = ('review_type', 'user', 'assigned', 'book', 'user')
    search_fields = ('user', 'book',)


class EditorialReviewAssAdmin(admin.ModelAdmin):

    list_display = ('management_editor', 'assigned', 'book')
    search_fields = ('management_editor', 'book',)


class FileAdmin(admin.ModelAdmin):

    list_display = (
        'original_filename', 'uuid_filename', 'kind', 'date_uploaded'
    )


class ReviewRoundAdmin(admin.ModelAdmin):

    list_display = ('book', 'round_number')


class ProposalFormAdmin(admin.ModelAdmin):

    list_display = ('name', 'ref')
    search_fields = ('name',)
    exclude = ()


class ProposalFormElementRelationshipAdmin(admin.ModelAdmin):

    list_display = ('form', 'element')


class ProposalFormElementAdmin(admin.ModelAdmin):

    list_display = ('name', 'field_type')


admin_list = [
    (m.Author, AuthorAdmin),
    (m.Note, NoteAdmin),
    (m.Profile, ProfileAdmin),
    (m.Book, BookAdmin),
    (m.License, LicenseAdmin),
    (m.Task, TaskAdmin),
    (m.File, FileAdmin),
    (m.FileVersion,),
    (m.Stage,),
    (m.Subject,),
    (m.Keyword,),
    (m.Series,),
    (m.Log, LogAdmin),
    (m.Setting, SettingAdmin),
    (m.SettingGroup,),
    (m.Role, RoleAdmin,),
    (m.ReviewAssignment, ReviewAssAdmin),
    (m.EditorialReviewAssignment, EditorialReviewAssAdmin),
    (m.Format,),
    (m.Chapter,),
    (m.ChapterFormat,),
    (m.ReviewRound, ReviewRoundAdmin),
    (m.ProposalForm, ProposalFormAdmin),
    (m.ProposalFormElement, ProposalFormElementAdmin),
    (m.ProposalFormElementsRelationship, ProposalFormElementRelationshipAdmin),
    (m.Contract,),
    (m.Retailer,),
    (m.Identifier,),
    (m.Language,),
    (m.CopyeditAssignment,),
    (m.TypesetAssignment,),
    (m.IndexAssignment,),
    (m.EmailLog,),
    (m.Message,),
    (m.APIConnector,),
    (m.PhysicalFormat,),
]

[admin.site.register(*t) for t in admin_list]
