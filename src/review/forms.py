from django import forms

from review import models


def render_choices(choices):
    c_split = choices.split('|')
    return [(choice.capitalize(), choice) for choice in c_split]


class GeneratedForm(forms.Form):

    def __init__(self, *args, **kwargs):
        form_obj = kwargs.pop('form', None)
        super(GeneratedForm, self).__init__(*args, **kwargs)
        relations = models.FormElementsRelationship.objects.filter(
            form=form_obj
        ).order_by('order')

        for relation in relations:
            if relation.element.field_type == 'text':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.TextInput(attrs={'div_class': relation.width}),
                    required=relation.element.required,
                )
            elif relation.element.field_type == 'textarea':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.Textarea,
                    required=relation.element.required,
                )
            elif relation.element.field_type == 'date':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.DateInput(
                        attrs={
                            'class': 'datepicker',
                            'div_class': relation.width
                        }
                    ),
                    required=relation.element.required)
            elif relation.element.field_type == 'upload':
                self.fields[relation.element.name] = forms.FileField(
                    required=relation.element.required,
                )
            elif relation.element.field_type == 'select':
                if relation.element.name == 'Series':
                    choices = series_list
                else:
                    choices = render_choices(relation.element.choices)
                self.fields[relation.element.name] = forms.ChoiceField(
                    widget=forms.Select(attrs={'div_class': relation.width}),
                    choices=choices,
                    required=relation.element.required,
                )
            elif relation.element.field_type == 'email':
                self.fields[relation.element.name] = forms.EmailField(
                    widget=forms.TextInput(attrs={'div_class': relation.width}),
                    required=relation.element.required,
                )
            elif relation.element.field_type == 'check':
                self.fields[relation.element.name] = forms.BooleanField(
                    widget=forms.CheckboxInput(attrs={'is_checkbox': True}),
                    required=relation.element.required,
                )
            self.fields[relation.element.name].help_text = relation.help_text
            self.fields[relation.element.name].label = relation.element.name
