from django import forms

from manager.forms import build_generated_form
from review.models import FormElementsRelationship


def render_choices(choices):
    c_split = choices.split('|')
    return [(choice.capitalize(), choice) for choice in c_split]


class GeneratedForm(forms.Form):

    def __init__(self, *args, **kwargs):
        form_obj = kwargs.pop('form', None)
        super(GeneratedForm, self).__init__(*args, **kwargs)
        relations = FormElementsRelationship.objects.filter(
            form=form_obj
        ).order_by('order')

        build_generated_form(self, relations)
