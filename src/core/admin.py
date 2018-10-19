from django.contrib import admin

from core import models


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
    (models.Author, AuthorAdmin),
    (models.Note, NoteAdmin),
    (models.Profile, ProfileAdmin),
    (models.Book, BookAdmin),
    (models.License, LicenseAdmin),
    (models.Task, TaskAdmin),
    (models.File, FileAdmin),
    (models.FileVersion,),
    (models.Stage,),
    (models.Subject,),
    (models.Keyword,),
    (models.Series,),
    (models.Log, LogAdmin),
    (models.Setting, SettingAdmin),
    (models.SettingGroup,),
    (models.Role, RoleAdmin,),
    (models.ReviewAssignment, ReviewAssAdmin),
    (models.EditorialReviewAssignment, EditorialReviewAssAdmin),
    (models.Format,),
    (models.Chapter,),
    (models.ChapterFormat,),
    (models.ReviewRound, ReviewRoundAdmin),
    (models.ProposalForm, ProposalFormAdmin),
    (models.ProposalFormElement, ProposalFormElementAdmin),
    (
        models.ProposalFormElementsRelationship,
        ProposalFormElementRelationshipAdmin
    ),
    (models.Contract,),
    (models.Retailer,),
    (models.Identifier,),
    (models.Language,),
    (models.CopyeditAssignment,),
    (models.TypesetAssignment,),
    (models.IndexAssignment,),
    (models.EmailLog,),
    (models.Message,),
    (models.APIConnector,),
    (models.PhysicalFormat,),
]

[admin.site.register(*t) for t in admin_list]
