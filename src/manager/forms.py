from django import forms
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_text

from django_summernote.widgets import SummernoteWidget

from core import models as core_models
from manager import models
from review import models as review_models


class GroupForm(forms.ModelForm):

    class Meta:
        model = models.Group
        exclude = ()


class SeriesForm(forms.ModelForm):

    class Meta:
        model = core_models.Series
        exclude = ()


class FormElement(forms.ModelForm):

    class Meta:
        model = review_models.FormElement
        exclude = ('form',)


class FormElementsRelationship(forms.ModelForm):

    class Meta:
        model = review_models.FormElementsRelationship
        exclude = ('form', 'element')


class ProposalForms(forms.ModelForm):

    class Meta:
        model = core_models.ProposalForm
        exclude = ('proposal_fields',)

    def __init__(self, *args, **kwargs):
        super(ProposalForms, self).__init__(*args, **kwargs)
        self.fields['intro_text'].label = "Introduction text"


class ProposalElement(forms.ModelForm):

    class Meta:
        model = core_models.ProposalFormElement
        exclude = ('form',)


class ProposalElementRelationship(forms.ModelForm):

    class Meta:
        model = core_models.ProposalFormElementsRelationship
        exclude = ('form', 'element')


class ReviewForm(forms.ModelForm):

    class Meta:
        model = review_models.Form
        exclude = ('form_fields',)

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['intro_text'].label = "Introduction text"


class EditKey(forms.Form):

    def __init__(self, *args, **kwargs):
        key_type = smart_text(kwargs.pop('key_type', None))
        value = kwargs.pop('value', None)
        super(EditKey, self).__init__(*args, **kwargs)

        if key_type == 'rich_text':
            self.fields['value'].widget = SummernoteWidget()
        elif key_type == 'boolean':
            self.fields['value'].widget = forms.CheckboxInput()
        elif key_type == 'integer':
            self.fields['value'].widget = forms.TextInput(
                attrs={'type': 'number'})
        elif key_type == 'file' or key_type == 'journalthumb':
            self.fields['value'].widget = forms.FileInput()
        elif key_type == 'text':
            self.fields['value'].widget = forms.Textarea()
        else:
            self.fields['value'].widget.attrs['size'] = '100%'

        self.fields['value'].initial = value

    value = forms.CharField(label='')


class ProposalForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['selection'].choices = [
            (proposal_form.pk, proposal_form)
            for proposal_form in core_models.ProposalForm.objects.all()
        ]

    selection = forms.ChoiceField(widget=forms.Select)


class DefaultReviewForm(forms.Form):

    name = forms.CharField(
        widget=forms.TextInput,
        required=True,
    )
    ref = forms.CharField(
        widget=forms.TextInput,
        required=True,
    )
    intro_text = forms.CharField(
        widget=forms.Textarea,
        required=True,
    )
    completion_text = forms.CharField(
        widget=forms.Textarea,
        required=True,
    )


class DefaultForm(forms.Form):

    title = forms.CharField(
        widget=forms.TextInput,
        required=True,
        label='Book Title',
    )
    subtitle = forms.CharField(
        widget=forms.TextInput,
        required=False,
    )
    author = forms.CharField(
        widget=forms.TextInput,
        required=True,
        label='Submitting Author/Editor',
    )


class DefaultNotRequiredForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput,
        required=False,
        label='Book Title',
    )
    subtitle = forms.CharField(
        widget=forms.TextInput,
        required=False,
    )
    author = forms.CharField(
        widget=forms.TextInput,
        required=False,
        label='Submitting Author/Editor',
    )


def render_choices(choices):
    c_split = choices.split('|')
    return [(choice.capitalize(), choice) for choice in c_split]


class GeneratedForm(forms.Form):

    def __init__(self, *args, **kwargs):

        form_obj = kwargs.pop('form', None)
        super(GeneratedForm, self).__init__(*args, **kwargs)
        relations = core_models.ProposalFormElementsRelationship.objects.filter(
            form__id=form_obj.id).order_by('order')
        for relation in relations:

            if relation.element.field_type == 'text':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.TextInput(attrs={'div_class': relation.width}),
                    required=relation.element.required)
            elif relation.element.field_type == 'textarea':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.Textarea(attrs={'div_class': relation.width}),
                    required=relation.element.required)
            elif relation.element.field_type == 'date':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.DateInput(attrs={'class': 'datepicker',
                                                  'div_class': relation.width}),
                    required=relation.element.required)
            elif relation.element.field_type == 'upload':
                self.fields[relation.element.name] = forms.FileField(
                    widget=forms.FileInput(attrs={'div_class': relation.width}),
                    required=relation.element.required)
            elif relation.element.field_type == 'select':
                if relation.element.name == 'Series':
                    choices = series_list
                else:
                    choices = render_choices(relation.element.choices)
                self.fields[relation.element.name] = forms.ChoiceField(
                    widget=forms.Select(attrs={'div_class': relation.width}),
                    choices=choices, required=relation.element.required)
            elif relation.element.field_type == 'email':
                self.fields[relation.element.name] = forms.EmailField(
                    widget=forms.TextInput(attrs={'div_class': relation.width}),
                    required=relation.element.required)
            elif relation.element.field_type == 'check':
                self.fields[relation.element.name] = forms.BooleanField(
                    widget=forms.CheckboxInput(attrs={'is_checkbox': True,
                                                      'div_class': relation.width}),
                    required=relation.element.required)
            self.fields[relation.element.name].help_text = relation.help_text
            self.fields[relation.element.name].label = relation.element.name


class GeneratedNotRequiredForm(forms.Form):
    def __init__(self, *args, **kwargs):

        form_obj = kwargs.pop('form', None)
        super(GeneratedNotRequiredForm, self).__init__(*args, **kwargs)
        relations = core_models.ProposalFormElementsRelationship.objects.filter(
            form__id=form_obj.id).order_by('order')
        for relation in relations:

            if relation.element.field_type == 'text':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.TextInput(attrs={'div_class': relation.width}),
                    required=False)
            elif relation.element.field_type == 'textarea':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.Textarea(attrs={'div_class': relation.width}),
                    required=False)
            elif relation.element.field_type == 'date':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.DateInput(attrs={'class': 'datepicker',
                                                  'div_class': relation.width}),
                    required=False)
            elif relation.element.field_type == 'upload':
                self.fields[relation.element.name] = forms.FileField(
                    widget=forms.FileInput(attrs={'div_class': relation.width}),
                    required=False)
            elif relation.element.field_type == 'select':
                if relation.element.name == 'Series':
                    choices = series_list
                else:
                    choices = render_choices(relation.element.choices)
                self.fields[relation.element.name] = forms.ChoiceField(
                    widget=forms.Select(attrs={'div_class': relation.width}),
                    choices=choices, required=False)
            elif relation.element.field_type == 'email':
                self.fields[relation.element.name] = forms.EmailField(
                    widget=forms.TextInput(attrs={'div_class': relation.width}),
                    required=False)
            elif relation.element.field_type == 'check':
                self.fields[relation.element.name] = forms.BooleanField(
                    widget=forms.CheckboxInput(attrs={'is_checkbox': True,
                                                      'div_class': relation.width}),
                    required=False)
            self.fields[relation.element.name].help_text = relation.help_text
            self.fields[relation.element.name].label = relation.element.name


class GeneratedReviewForm(forms.Form):
    def __init__(self, *args, **kwargs):

        form_obj = kwargs.pop('form', None)
        super(GeneratedReviewForm, self).__init__(*args, **kwargs)
        relations = review_models.FormElementsRelationship.objects.filter(
            form=form_obj).order_by('order')
        for relation in relations:

            if relation.element.field_type == 'text':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.TextInput(attrs={'div_class': relation.width}),
                    required=relation.element.required)
            elif relation.element.field_type == 'textarea':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.Textarea(attrs={'div_class': relation.width}),
                    required=relation.element.required)
            elif relation.element.field_type == 'date':
                self.fields[relation.element.name] = forms.CharField(
                    widget=forms.DateInput(attrs={'class': 'datepicker',
                                                  'id': slugify(
                                                      relation.element.name),
                                                  'div_class': relation.width}),
                    required=relation.element.required)
            elif relation.element.field_type == 'upload':
                self.fields[relation.element.name] = forms.FileField(
                    widget=forms.FileInput(attrs={'div_class': relation.width}),
                    required=relation.element.required)
            elif relation.element.field_type == 'select':
                if relation.element.name == 'Series':
                    choices = series_list
                else:
                    choices = render_choices(relation.element.choices)
                self.fields[relation.element.name] = forms.ChoiceField(
                    widget=forms.Select(attrs={'div_class': relation.width}),
                    choices=choices, required=relation.element.required)
            elif relation.element.field_type == 'email':
                self.fields[relation.element.name] = forms.EmailField(
                    widget=forms.TextInput(attrs={'div_class': relation.width}),
                    required=relation.element.required)
            elif relation.element.field_type == 'check':
                self.fields[relation.element.name] = forms.BooleanField(
                    widget=forms.CheckboxInput(attrs={'is_checkbox': True,
                                                      'div_class': relation.width}),
                    required=relation.element.required)
            self.fields[relation.element.name].help_text = relation.help_text
            self.fields[relation.element.name].label = relation.element.name
