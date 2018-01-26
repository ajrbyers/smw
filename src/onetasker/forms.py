from django import forms

from core import models


class Copyedit(forms.ModelForm):

    class Meta:
        model = models.CopyeditAssignment
        fields = ('note_from_copyeditor',)


class Typeset(forms.ModelForm):

    class Meta:
        model = models.TypesetAssignment
        fields = ('note_from_typesetter',)


class Index(forms.ModelForm):

    class Meta:
        model = models.IndexAssignment
        fields = ('note_from_indexer',)
