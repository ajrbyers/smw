import uuid

from django import forms
from django.contrib.auth.models import User

from django_summernote.widgets import SummernoteWidget

from core import models, logic
from setting_util import get_setting
from submission import models as submission_models


class UploadMiscFile(forms.Form):

    label = forms.CharField(required=True)
    file_type = forms.ChoiceField(
        required=True, choices=(
            ('marketing', 'Marketing'),
            ('agreements', 'Agreements'),
            ('other', 'Other')
        )
    )


class UploadFile(forms.Form):

    label = forms.CharField(required=True)


class UserCreationForm(forms.ModelForm):
    """ Creates a user, with no privileges, from the given username and pw. """

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
    }
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification."
    )
    email = forms.CharField(max_length=100, required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        username = self.cleaned_data.get("username")
        if (
            email and
            User.objects.filter(email=email).exclude(username=username).count()
        ):
            raise forms.ValidationError(u'Email address already registered')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        user.save()

        # Add a profile for this new user and create a new activation code.
        profile = models.Profile(user=user, activation_code=uuid.uuid4())
        profile.terms_and_conditions = True
        profile.save()

        email_text = get_setting('new_user_email', 'email')
        logic.send_new_user_ack(email_text, user, profile)

        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class FullUserProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        username = self.cleaned_data.get("username")
        if (
            email and
            User.objects.filter(email=email).exclude(username=username).count()
        ):
            raise forms.ValidationError(u'Email address already registered')
        return email


class RegistrationProfileForm(forms.ModelForm):

    class Meta:
        model = models.Profile
        fields = (
            "salutation", "middle_name", "orcid", "institution", "department",
            "country", "twitter", "facebook", "linkedin", "impactstory",
            "github", "website"
        )


class ProfileForm(forms.ModelForm):

    class Meta:
        model = models.Profile
        fields = (
            "salutation", "middle_name", "biography", "interest", "orcid",
            "institution", "department", "country", "twitter", "facebook",
            "linkedin", "impactstory", "github", "profile_image", "signature",
            "website"
        )


class FullProfileForm(forms.ModelForm):

    class Meta:
        model = models.Profile
        fields = (
            "salutation", "middle_name", "biography", "orcid", "institution",
            "department", "interest", "country", "twitter", "facebook",
            "linkedin", "impactstory", "github", "profile_image",
            "signature", "website", "roles"
        )


class TaskForm(forms.ModelForm):

    class Meta:
        model = models.Task
        fields = ("text", "workflow")
        exclude = ("due",)


class RecommendationForm(forms.ModelForm):

    class Meta:
        model = models.ReviewAssignment
        fields = ("recommendation", "competing_interests")

    def __init__(self, *args, **kwargs):
        ci_required = kwargs.pop('ci_required', None)
        super(RecommendationForm, self).__init__(*args, **kwargs)

        if ci_required == 'on':
            self.fields['competing_interests'] = forms.CharField(
                widget=forms.Textarea,
                required=True,
            )


class MessageForm(forms.ModelForm):

    class Meta:
        model = models.Message
        fields = ('message',)


class Copyedit(forms.ModelForm):

    class Meta:
        model = models.CopyeditAssignment
        fields = ('note',)


class CopyeditAuthorInvite(forms.ModelForm):

    class Meta:
        model = models.CopyeditAssignment
        fields = ('note_to_author',)


class CopyeditAuthor(forms.ModelForm):

    class Meta:
        model = models.CopyeditAssignment
        fields = ('note_from_author',)


class Typeset(forms.ModelForm):

    class Meta:
        model = models.TypesetAssignment
        fields = ('note',)


class TypesetAuthorInvite(forms.ModelForm):

    class Meta:
        model = models.TypesetAssignment
        fields = ('note_to_author',)


class TypesetAuthor(forms.ModelForm):

    class Meta:
        model = models.TypesetAssignment
        fields = ('note_from_author',)


class TypesetTypesetterInvite(forms.ModelForm):

    class Meta:
        model = models.TypesetAssignment
        fields = ('note_to_typesetter',)


class TypesetTypesetter(forms.ModelForm):

    class Meta:
        model = models.TypesetAssignment
        fields = ('note_from_typesetter',)


class FormatForm(forms.ModelForm):

    format_file = forms.FileField(required=True)

    class Meta:
        model = models.Format
        exclude = ('book', 'file')


class FormatFormInitial(forms.ModelForm):

    class Meta:
        model = models.Format
        exclude = ('book', 'file')


class ChapterForm(forms.ModelForm):

    class Meta:
        model = models.Chapter
        exclude = ('book', 'formats')


class ChapterFormatForm(forms.ModelForm):

    chapter_file = forms.FileField(required=True)

    class Meta:
        model = models.ChapterFormat
        exclude = ('book', 'file', 'chapter')


class ChapterFormInitial(forms.ModelForm):

    class Meta:
        model = models.Chapter
        exclude = ('book', 'formats')


class UpdateChapterFormat(forms.Form):

    file = forms.FileField(required=True)
    file_label = forms.CharField(required=False)
    name = forms.CharField(required=True)


class UploadContract(forms.ModelForm):

    class Meta:
        model = models.Contract
        exclude = ('author_file',)


class AuthorContractSignoff(forms.ModelForm):

    class Meta:
        model = models.Contract
        fields = ('author_file',)


class EditMetadata(forms.ModelForm):

    class Meta:
        model = models.Book
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
            'publication_date'
        )

        widgets = {'languages': forms.CheckboxSelectMultiple()}


class IdentifierForm(forms.ModelForm):

    class Meta:
        model = models.Identifier
        fields = ('identifier', 'value', 'displayed')


class CoverForm(forms.ModelForm):

    class Meta:
        model = models.Book
        fields = ('cover',)


class RetailerForm(forms.ModelForm):

    class Meta:
        model = models.Retailer
        fields = ('name', 'link', 'price', 'enabled')


class ChangeReviewDueDateForm(forms.ModelForm):

    class Meta:
        model = submission_models.ProposalReview
        fields = ('due',)


class CustomEmailForm(forms.Form):
    email_subject = forms.CharField()
    email_body = forms.CharField(widget=SummernoteWidget())
    attachments = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={'multiple': True}
         )
    )
