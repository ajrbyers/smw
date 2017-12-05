from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm

from core import models as core_models
from editor import models
from revisions import models as revision_models


class EditorForm(ModelForm):

    class Meta:
        model = core_models.Book
        fields = ('book_editors',)

    def __init__(self, *args, **kwargs):
        super(EditorForm, self).__init__(*args, **kwargs)
        self.fields['book_editors'].queryset = User.objects.filter(
            profile__roles__slug='book-editor')
        self.fields['book_editors'].label_from_instance = (
            lambda obj: "%s %s" % (obj.first_name, obj.last_name)
        )


class Marc21Form(forms.Form):

    file_content = forms.CharField(widget=forms.Textarea, required=False)
    format_file = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        content = kwargs.pop('content', None)
        super(Marc21Form, self).__init__(*args, **kwargs)
        self.fields['file_content'].initial = content


class ChangeOwnerForm(ModelForm):

    class Meta:
        model = core_models.Book
        fields = ('owner',)


class RevisionForm(ModelForm):

    class Meta:
        model = revision_models.Revision
        fields = ('notes_from_editor', 'due')


class NoteForm(ModelForm):

    class Meta:
        model = core_models.Note
        fields = ('subject', 'text',)

    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        self.fields['text'].required = True
        self.fields['text'].label = "Content"


class FormatForm(forms.ModelForm):

    class Meta:
        model = core_models.Format
        exclude = ('book', 'file')

    format_file = forms.FileField(required=True)


class ChapterFormatForm(forms.ModelForm):

    class Meta:
        model = core_models.ChapterFormat
        exclude = ('book',)

    chapter_file = forms.FileField(required=True)


class ChapterForm(forms.ModelForm):

    class Meta:
        model = core_models.Chapter
        exclude = ('book', 'formats')


class ChapterAuthorForm(forms.ModelForm):

    class Meta:
        model = core_models.ChapterAuthor
        exclude = ('old_author_id',)


class PhysicalFormatForm(forms.ModelForm):

    class Meta:
        model = core_models.PhysicalFormat
        exclude = ('book',)


class UpdateChapterFormat(forms.Form):

    file = forms.FileField(required=False)
    identifier = forms.CharField(required=True)
    name = forms.CharField(required=True)


class UploadContract(forms.ModelForm):

    class Meta:
        model = core_models.Contract
        exclude = ('author_file',)


class AuthorContractSignoff(forms.ModelForm):

    class Meta:
        model = core_models.Contract
        fields = ('author_file',)


class EditMetadata(forms.ModelForm):

    class Meta:
        model = core_models.Book
        fields = (
            'prefix',
            'title',
            'subtitle',
            'series',
            'description',
            'license',
            'pages',
            'slug',
            'review_type',
            'languages',
            'publication_date',
            'expected_completion_date',
            'peer_review_override',
            'book_type',
            'table_contents_linked',
            'publisher_location',
            'publisher_name'
        )

        exclude = (
            'author',
            'editor',
            'book_editors',
            'press_editors',
            'production_editors',
            'reviewer_suggestions',
            'competing_interests',
            'owner',
            'read_only_users',
            'submission_date',
            'review_assignments',
            'editorial_review_assignments',
            'review_form',
        )

        widgets = {
            'languages': forms.CheckboxSelectMultiple(),
        }


class IdentifierForm(forms.ModelForm):

    class Meta:
        model = core_models.Identifier
        fields = (
            'identifier',
            'value',
            'displayed',
            'digital_format',
            'physical_format',
        )

    def __init__(self, *args, **kwargs):
        digital_format_choices = kwargs.pop('digital_format_choices', None)
        physical_format_choices = kwargs.pop('physical_format_choices', None)
        super(IdentifierForm, self).__init__(*args, **kwargs)
        if digital_format_choices and physical_format_choices:
            self.fields['digital_format'] = forms.ChoiceField(
                widget=forms.Select(), choices=digital_format_choices,
                required=False)
            self.fields['physical_format'] = forms.ChoiceField(
                widget=forms.Select(), choices=physical_format_choices,
                required=False)

    def clean(self):
        digital_format = self.cleaned_data.get('digital_format')
        physical_format = self.cleaned_data.get('physical_format')

        if digital_format and physical_format:
            raise forms.ValidationError(
                'You must select either a Digital Format, '
                'a Physical Format or Neither.'
            )


class CoverForm(forms.ModelForm):

    class Meta:
        model = core_models.Book
        fields = ('cover',)


class RetailerForm(forms.ModelForm):

    class Meta:
        model = core_models.Retailer
        fields = ('name', 'link', 'price', 'enabled')


class Typeset(forms.ModelForm):

    class Meta:
        model = core_models.TypesetAssignment
        fields = ('note',)


class TypesetDate(forms.ModelForm):

    class Meta:
        model = core_models.TypesetAssignment
        fields = ('due',)


class TypesetAuthorDate(forms.ModelForm):

    class Meta:
        model = core_models.TypesetAssignment
        fields = ('author_due',)


class TypesetAuthorInvite(forms.ModelForm):

    class Meta:
        model = core_models.TypesetAssignment
        fields = ('note_to_author', 'author_due')


class TypesetAuthor(forms.ModelForm):

    class Meta:
        model = core_models.TypesetAssignment
        fields = ('note_from_author',)


class TypesetTypesetterInvite(forms.ModelForm):

    class Meta:
        model = core_models.TypesetAssignment
        fields = ('note_to_typesetter',)


class TypesetTypesetter(forms.ModelForm):

    class Meta:
        model = core_models.TypesetAssignment
        fields = ('note_from_typesetter',)


class CoverImageReviewForm(forms.ModelForm):

    class Meta:
        model = models.CoverImageProof
        fields = ('note_to_author',)


class ChangeRevisionDueDateForm(forms.ModelForm):

    class Meta:
        model = revision_models.Revision
        fields = ('due',)
