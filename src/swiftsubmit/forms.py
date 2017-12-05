from django import forms

from core import models


class StageForm(forms.ModelForm):

    class Meta:
        model = models.Stage
        exclude = ('declined',)
