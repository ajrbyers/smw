from django import forms
from django.forms import ModelForm

from core import models as core_models
from submission import models


class ProposalStart(forms.ModelForm):

    class Meta:
        model = models.Proposal
        fields = ('review_form',)

    def __init__(self, *args, **kwargs):
        super(ProposalStart, self).__init__(*args, **kwargs)
        self.fields['review_form'].required = True


class NoteForm(ModelForm):

    class Meta:
        model = models.ProposalNote
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        self.fields['text'].required = True
        self.fields['text'].label = "Content"


class SubmitBookStageOne(forms.ModelForm):

    class Meta:
        model = core_models.Book
        fields = (
            'book_type', 'cover_letter', 'series', 'license', 'review_type',
            'reviewer_suggestions', 'competing_interests'
        )

    book_type = forms.CharField(
        required=True,
        widget=forms.Select(choices=core_models.book_type_choices())
    )

    def __init__(self, *args, **kwargs):
        ci_required = kwargs.pop('ci_required', None)
        review_type_required = kwargs.pop('review_type_required', None)
        super(SubmitBookStageOne, self).__init__(*args, **kwargs)
        if ci_required == 'on':
            self.fields['competing_interests'] = forms.CharField(
                widget=forms.Textarea, required=True)
        if not review_type_required == 'on':
            self.fields['review_type'] = forms.CharField(
                required=False,
                widget=forms.Select(
                    choices=core_models.book_review_type_choices()
                )
            )
        else:
            self.fields['review_type'] = forms.CharField(
                required=True,
                widget=forms.Select(
                    choices=core_models.book_review_type_choices()
                )
            )

        self.fields['license'].empty_label = None
        self.fields['reviewer_suggestions'].label = "Suggested Reviewers"


class SubmissionChecklist(forms.Form):

    def __init__(self, *args, **kwargs):
        checklist_items = kwargs.pop('checklist_items', None)
        book = kwargs.pop('book', None)
        super(SubmissionChecklist, self).__init__(*args, **kwargs)

        if checklist_items:
            for item in checklist_items:
                self.fields[item.text] = forms.BooleanField(
                    required=item.required)
                self.fields[item.text].label = item.text


class SubmitBookStageTwo(forms.ModelForm):

    class Meta:
        model = core_models.Book
        fields = ('prefix', 'title', 'subtitle', 'description')

    title = forms.CharField(required=True)
    description = forms.CharField(required=True, widget=forms.Textarea)


class SubmitBook(forms.ModelForm):

    class Meta:
        model = core_models.Book
        fields = (
            'title', 'subtitle', 'description', 'subject', 'license',
            'cover_letter', 'series'
        )


class AuthorForm(forms.ModelForm):

    class Meta:
        model = core_models.Author
        exclude = ('sequence',)


class EditorForm(forms.ModelForm):

    class Meta:
        model = core_models.Editor
        exclude = ('sequence',)


class CreateSubmissionChecklistItem(forms.ModelForm):

    class Meta:
        model = models.SubmissionChecklistItem
        exclude = ()
