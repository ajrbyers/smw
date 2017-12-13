from django import forms

from editorialreview import models


class EditorialReviewForm(forms.ModelForm):

    class Meta:
        model = models.EditorialReview
        fields = ('due',)

    def __init__(self, *args, **kwargs):
        super(EditorialReviewForm, self).__init__(*args, **kwargs)
        self.fields['due'].required = True


class RecommendationForm(forms.ModelForm):

    class Meta:
        model = models.EditorialReview
        fields = ("recommendation", "competing_interests")

    def __init__(self, *args, **kwargs):
        ci_required = kwargs.pop('ci_required', None)
        super(RecommendationForm, self).__init__(*args, **kwargs)

        if ci_required == 'on':
            self.fields['competing_interests'] = forms.CharField(
                widget=forms.Textarea, required=True)
        self.fields['recommendation'].required = True
