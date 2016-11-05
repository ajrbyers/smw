from django import forms
from django.forms import ModelForm
from core import models as core_models
from revisions import models as revision_models
from editor import models as editor_models

class UploadContract(forms.ModelForm):

    class Meta:
        model = core_models.Contract
        exclude = ('author_file',)

class AuthorContractSignoff(forms.ModelForm):

    class Meta:
        model = core_models.Contract
        fields = ('author_file',)


class AuthorRevisionForm(ModelForm):

    class Meta:
        model = revision_models.Revision
        fields = ('cover_letter',)

class CoverImageReviewForm(forms.ModelForm):

    class Meta:
        model = editor_models.CoverImageProof
        fields = ('note_to_editor',)
