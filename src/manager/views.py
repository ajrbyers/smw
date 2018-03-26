import json
import os
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_text
from django.views.decorators.csrf import csrf_exempt

import requests

from core import models as core_models, forms as core_forms
from core.decorators import is_press_editor
from manager import forms, logic, models
from review import models as review_models
from submission import forms as submission_forms, models as submission_models


@is_press_editor
def index(request):
    template = 'manager/index.html'
    context = {}

    return render(request, template, context)


@is_press_editor
def about(request):
    template = 'manager/about.html'
    context = {}

    return render(request, template, context)


@is_press_editor
def groups(request):
    template = 'manager/groups.html'
    context = {'groups': models.Group.objects.all()}

    return render(request, template, context)


@is_press_editor
def group(request, group_id=None):
    form = forms.GroupForm()

    if group_id:
        _group = get_object_or_404(models.Group, pk=group_id)
        form = forms.GroupForm(instance=_group)
    else:
        _group = None

    if request.method == 'POST':
        if group_id:
            form = forms.GroupForm(request.POST, instance=_group)
        else:
            form = forms.GroupForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('manager_groups')

    template = 'manager/group.html'
    context = {'form': form, 'group': _group}

    return render(request, template, context)


@is_press_editor
def group_delete(request, group_id):
    _group = get_object_or_404(models.Group, pk=group_id)
    _group.delete()

    return redirect('manager_groups')


@is_press_editor
def group_members(request, group_id):
    _group = get_object_or_404(models.Group, pk=group_id)
    members = models.GroupMembership.objects.filter(group=_group)
    _users = User.objects.all().order_by('last_name')
    template = 'manager/members.html'
    context = {'group': _group, 'members': members, 'users': _users}

    return render(request, template, context)


@is_press_editor
def group_members_assign(request, group_id, user_id):
    _group = get_object_or_404(models.Group, pk=group_id)
    user = get_object_or_404(User, pk=user_id)

    if not models.GroupMembership.objects.filter(user=user, group=_group):
        member = models.GroupMembership(user=user, group=_group, sequence=9999)
        member.save()
    else:
        messages.add_message(
            request,
            messages.WARNING,
            'This user is already a member of {}'.format(_group.name)
        )

    return redirect(
        reverse('manager_group_members', kwargs={'group_id': _group.id})
    )


@is_press_editor
def manager_membership_delete(request, group_id, member_id):
    _group = get_object_or_404(models.Group, pk=group_id)
    membership = get_object_or_404(models.GroupMembership, pk=member_id)
    membership.delete()

    return redirect(
        reverse('manager_group_members', kwargs={'group_id': _group.id})
    )


@is_press_editor
@csrf_exempt
def roles(request):
    template = 'manager/roles.html'
    context = {'roles': core_models.Role.objects.all()}

    return render(request, template, context)


@is_press_editor
def role(request, slug):
    _role = get_object_or_404(core_models.Role, slug=slug)
    users_with_role = User.objects.filter(profile__roles__slug=slug)
    _users = User.objects.all().order_by(
        'last_name'
    ).exclude(
        profile__roles__slug=slug
    )

    template = 'manager/role.html'
    context = {
        'role': _role,
        'users': _users,
        'users_with_role': users_with_role,
    }

    return render(request, template, context)


@is_press_editor
def role_action(request, slug, user_id, action):
    user = get_object_or_404(User, pk=user_id)
    _role = get_object_or_404(core_models.Role, slug=slug)

    if action == 'add':
        user.profile.roles.add(_role)
    elif action == 'remove':
        user.profile.roles.remove(_role)

    user.save()

    return redirect(reverse('manager_role', kwargs={'slug': _role.slug}))


@is_press_editor
def flush_cache(request):
    cache._cache.flush_all()
    messages.add_message(
        request,
        messages.SUCCESS,
        'Memcached has been flushed.',
    )

    return redirect(reverse('manager_index'))


@is_press_editor
def settings_index(request):
    template = 'manager/settings/index.html'
    context = {
        'settings': [
            {
                gr.name:
                core_models.Setting.objects.filter(group=gr).order_by('name')
            }
            for gr in core_models.SettingGroup.objects.all().order_by('name')
        ],
    }

    return render(request, template, context)


@is_press_editor
def edit_setting(request, setting_group, setting_name):
    _group = get_object_or_404(core_models.SettingGroup, name=setting_group)
    setting = get_object_or_404(
        core_models.Setting,
        group=_group,
        name=setting_name,
    )
    edit_form = forms.EditKey(key_type=setting.types, value=setting.value)

    if request.POST and 'delete' in request.POST:
        setting.value = ''
        setting.save()

        return redirect(reverse('settings_index'))

    if request.POST:
        value = smart_text(request.POST.get('value'))

        if setting.types == 'boolean' and value != 'on':
            value = ''

        if request.FILES:
            value = handle_file(request, request.FILES['value'])

        setting.value = value
        setting.save()
        cache._cache.flush_all()

        return redirect(reverse('settings_index'))

    template = 'manager/settings/edit_setting.html'
    context = {
        'setting': setting,
        'group': _group,
        'edit_form': edit_form,
    }

    return render(request, template, context)


def edit_submission_checklist(request, item_id):
    item = get_object_or_404(
        submission_models.SubmissionChecklistItem,
        pk=item_id,
    )
    checkitem_form = submission_forms.CreateSubmissionChecklistItem(
        instance=item,
    )

    if request.POST:
        checkitem_form = submission_forms.CreateSubmissionChecklistItem(
            request.POST,
            instance=item,
        )
        if checkitem_form.is_valid():
            checkitem_form.save()
            return redirect(reverse('submission_checklist'))

    template = 'manager/submission/checklist.html'
    context = {
        'checkitem_form': checkitem_form,
        'editing': True,
        'item': item,
        'checklist_items':
        submission_models.SubmissionChecklistItem.objects.all()
    }

    return render(request, template, context)


def delete_submission_checklist(request, item_id):
    item = get_object_or_404(
        submission_models.SubmissionChecklistItem,
        pk=item_id,
    )
    item.delete()

    return redirect(reverse('submission_checklist'))


def submission_checklist(request):
    checkitem_form = submission_forms.CreateSubmissionChecklistItem()

    if request.POST:
        checkitem_form = submission_forms.CreateSubmissionChecklistItem(
            request.POST)
        if checkitem_form.is_valid():
            checkitem_form.save()
            return redirect(reverse('submission_checklist'))

    template = 'manager/submission/checklist.html'
    context = {
        'checkitem_form': checkitem_form,
        'checklist_items':
        submission_models.SubmissionChecklistItem.objects.all()
    }

    return render(request, template, context)


@is_press_editor
def series(request):
    send_enabled = False

    if request.user.is_staff:
        send_enabled = True

    template = 'manager/series/index.html'
    context = {
        'all_series': core_models.Series.objects.all(),
        'send_enabled': send_enabled,
    }

    return render(request, template, context)


@is_press_editor
def send_series(request, series_id):
    if request.user.is_staff:
        credentials = get_object_or_404(core_models.APIConnector, slug="jura")
        _series = get_object_or_404(core_models.Series, pk=series_id)
        requests.post(
            "http://localhost:8080/api/series/",
            auth=(credentials.username, credentials.password),
            data={
                'press_code': 'up',
                'omp_series_id': _series.pk,
                'title': _series.name,
                'slug': slugify(_series.name),
                'editor': _series.editor.profile.full_name,
                'editor_email': _series.editor.email,
                'description': _series.description
            }
        )

        return redirect(reverse('series'))


@is_press_editor
def users(request):
    template = 'manager/users/index.html'
    context = {
        'users': User.objects.all(),
        'password': request.GET.get('password', None),
        'username': request.GET.get('username', None),
    }

    return render(request, template, context)


@is_press_editor
def series_edit(request, series_id):
    books = core_models.Book.objects.all()
    _series = core_models.Series.objects.get(pk=series_id)
    series_form = forms.SeriesForm(instance=_series)

    if request.method == 'POST':
        series_form = forms.SeriesForm(request.POST, instance=_series)
        if series_form.is_valid():
            _series = series_form.save()
            return redirect(reverse('series'))

    template = 'manager/series/edit.html'
    context = {
        'series': _series,
        'books': books,
        'series_form': series_form,
        'active': 'update',
    }

    return render(request, template, context)


@is_press_editor
def series_submission_add(request, submission_id, series_id):
    book = get_object_or_404(core_models.Book, pk=submission_id)
    _series = get_object_or_404(core_models.Series, pk=series_id)
    book.series = _series
    book.save()

    return redirect(reverse('series_edit', kwargs={'series_id': series_id}))


@is_press_editor
def series_submission_remove(request, submission_id):
    book = get_object_or_404(core_models.Book, pk=submission_id)
    book.series = None
    book.save()

    return redirect(reverse('series'))


@is_press_editor
def series_add(request):
    series_form = forms.SeriesForm()

    if request.method == 'POST':
        series_form = forms.SeriesForm(request.POST)
        if series_form.is_valid():
            series_form.save()
            return redirect(reverse('series'))

    template = 'manager/series/edit.html'
    context = {'series_form': series_form, 'active': 'add'}

    return render(request, template, context)


@is_press_editor
def series_delete(request, series_id):
    _series = get_object_or_404(core_models.Series, pk=series_id)
    books = core_models.Book.objects.filter(series=_series)

    if request.method == 'POST':
        for book in books:
            book.series = None
            book.save()

        _series.delete()

        return redirect(reverse('series'))

    template = 'manager/series/delete.html'
    context = {'series': _series, 'books': books}

    return render(request, template, context)


@is_press_editor
def add_user(request):
    user_form = core_forms.FullUserProfileForm()
    profile_form = core_forms.FullProfileForm()
    # To keep displaying interests if registration page is reloaded.
    display_interests = []

    if request.method == 'POST':
        user_form = core_forms.FullUserProfileForm(request.POST)
        profile_form = core_forms.FullProfileForm(request.POST, request.FILES)
        display_interests = request.POST.get('interests').split(',')
        if profile_form.is_valid() and user_form.is_valid():
            user = user_form.save()
            new_pass = None
            user.is_active = True

            if 'new_password' in request.POST:
                new_pass = logic.generate_password()
                user.set_password(new_pass)
                user.is_active = True
                user.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'New user %s, password set to %s.' % (
                        user.username,
                        new_pass,
                    )
                )

            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            _roles = request.POST.getlist('roles')

            for _role in _roles:
                role_object = core_models.Role.objects.get(pk=_role)
                profile.roles.add(role_object)

            interests = []

            if 'interests' in request.POST:
                interests = request.POST.get('interests').split(',')

            for interest in interests:
                new_interest, c = core_models.Interest.objects.get_or_create(
                    name=interest,
                )
                profile.interest.add(new_interest)

            profile.save()

            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect(
                    "%s?username=%s&password=%s" % (
                        reverse('manager_users'),
                        user.username,
                        new_pass
                    )
                )

    template = 'manager/users/add.html'
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'display_interests': display_interests,
        'active': 'add',
        'return': request.GET.get('return', False)
    }

    return render(request, template, context)


@is_press_editor
def user_edit(request, user_id):
    user = User.objects.get(pk=user_id)
    user_form = core_forms.UserProfileForm(instance=user)
    profile_form = core_forms.FullProfileForm(instance=user.profile)

    if request.method == 'POST':
        user_form = core_forms.UserProfileForm(request.POST, instance=user)
        profile_form = core_forms.FullProfileForm(
            request.POST,
            request.FILES,
            instance=user.profile,
        )
        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile = profile_form.save()

            for interest in profile.interest.all():
                profile.interest.remove(interest)

            interests = request.POST.get('interests')

            if interests:
                for interest in interests.split(','):
                    new_interest, c = (
                        core_models.Interest.objects.get_or_create(
                            name=interest
                        )
                    )
                    profile.interest.add(new_interest)
            profile.save()

            return redirect(reverse('manager_users'))

    template = 'manager/users/edit.html'
    context = {
        'user': user,
        'profile_form': profile_form,
        'user_form': user_form,
        'active': 'update',
    }

    return render(request, template, context)


@is_press_editor
def select_merge(request, user_id):
    user = User.objects.get(pk=user_id)
    secondary_users = User.objects.exclude(pk=user_id)

    template = 'manager/users/select_merge.html'
    context = {
        'user': user,
        'secondary_users': secondary_users
    }

    return render(request, template, context)


@is_press_editor
def merge_users(request, user_id, secondary_user_id):
    primary_user = User.objects.get(pk=user_id)
    secondary_user = User.objects.get(pk=secondary_user_id)
    related_objects = secondary_user._meta.get_all_related_objects()

    blank_profile_local_fields = set(
        [
            field.attname for field in primary_user.profile._meta.local_fields
            if getattr(primary_user.profile, field.attname) in [None, '']
        ]
    )

    filled_up = set()

    for field_name in blank_profile_local_fields:
        val = getattr(secondary_user.profile, field_name)
        if val not in [None, '']:
            setattr(primary_user.profile, field_name, val)
            filled_up.add(field_name)

    blank_profile_local_fields -= filled_up
    secondary_user.profile.delete()

    for _object in related_objects:
        old_values = {_object.field.attname: secondary_user_id}
        new_values = {_object.field.attname: user_id}
        model = _object.field.model
        model.objects.filter(Q(**old_values)).update(**new_values)

    secondary_user.delete()
    primary_user.profile.save()
    primary_user.save()

    return redirect(reverse('select_merge', kwargs={'user_id': user_id}))


@is_press_editor
def inactive_users(request):
    _users = User.objects.filter(is_active=False)

    template = 'manager/users/inactive.html'
    context = {'users': _users}

    return render(request, template, context)


@is_press_editor
def activate_user(request, user_id):
    user = get_object_or_404(models.User, pk=user_id, is_active=False)
    user.is_active = True

    if not user.profile.roles.filter(slug='reader').exists():
        user.profile.roles.add(core_models.Role.objects.get(slug="reader"))

    if not user.profile.roles.filter(slug='author').exists():
        user.profile.roles.add(core_models.Role.objects.get(slug="author"))

    user.profile.save()
    user.save()

    return redirect(reverse('manager_inactive_users'))


@is_press_editor
def key_help(request):
    with open(
        '%s%s' % (settings.BASE_DIR, '/core/fixtures/key_help.json')
    ) as data_file:
        data = json.load(data_file)

    template = "manager/keys.html"
    context = {
        'data': data,
        'data_render': smart_text(json.dumps(data, indent=4))
    }

    return render(request, template, context)


@is_press_editor
def add_new_form(request, form_type):
    form = forms.ReviewForm()
    if form_type == 'proposal':
        form = forms.ProposalForms()

    if request.POST:
        form = forms.ReviewForm(request.POST)
        if form_type == 'proposal':
            form = forms.ProposalForms(request.POST)

        if form.is_valid:
            form.save()

        return redirect(reverse('manager_{}_forms'.format(form_type)))

    template = 'manager/add_new_form.html'
    context = {'form': form, 'form_type': form_type}

    return render(request, template, context)


@is_press_editor
def proposal_forms(request):
    template = 'manager/proposal/forms.html'
    context = {'proposal_forms': core_models.ProposalForm.objects.all()}

    return render(request, template, context)


@is_press_editor
def reorder_form(request, form_type, form_id, field_1_id, field_2_id):
    """Swap two given form elements in a given form."""
    form_model = review_models.Form
    element_model = review_models.FormElementsRelationship
    if form_type == 'proposal':
        form_model = core_models.ProposalForm
        element_model = core_models.ProposalFormElementsRelationship

    get_object_or_404(form_model, pk=form_id)

    field_1 = get_object_or_404(element_model, pk=field_1_id)
    field_2 = get_object_or_404(element_model, pk=field_2_id)

    order_1 = field_1.order
    order_2 = field_2.order
    field_1.order = order_2
    field_2.order = order_1
    field_1.save()
    field_2.save()

    return redirect(
        reverse(
            'manager_edit_form',
            kwargs={
                'form_type': form_type,
                'form_id': form_id
            }
        )
    )


def form_order_field_list(form_type, form_id):
    """Return list of dicts detailing form elements and their positions."""
    form = get_object_or_404(review_models.Form, pk=form_id)
    relations = review_models.FormElementsRelationship.objects.filter(
        form=form
    ).order_by(
        'order'
    )
    if form_type == 'proposal':
        form = get_object_or_404(core_models.ProposalForm, pk=form_id)
        relations = core_models.ProposalFormElementsRelationship.objects.filter(
            form=form
        ).order_by(
            'order'
        )
    fields = []

    if relations > 0:
        for t, relation in enumerate(relations):
            above = -1
            below = -1
            if t < relations.count() - 1:
                below = relations[t + 1].pk
            if relations.count() > 1 and t == 0:
                above = -1
            elif relations.count() >= 1 and t > 0:
                above = relations[t - 1].pk

            fields.append(
                {
                    'field': relation,
                    'above': above,
                    'below': below
                }
            )

    return fields


@is_press_editor
def edit_form(request, form_type, form_id, relation_id=None):
    """Edit a review or proposal form."""
    proposal_form = form_type == 'proposal'
    elements_model = review_models.FormElementsRelationship
    if proposal_form:
        elements_model = core_models.ProposalFormElementsRelationship

    element_form_args = []
    element_form_kwargs = {}
    relation_form_args = []
    relation_form_kwargs = {}

    if request.POST:
        element_form_args.append(request.POST)
        relation_form_args.append(request.POST)

    if relation_id:
        relation = get_object_or_404(elements_model, pk=relation_id)
        element_form_kwargs['instance'] = relation.element
        relation_form_kwargs['instance'] = relation

    form = get_object_or_404(review_models.Form, pk=form_id)
    element_form = forms.FormElement(
        *element_form_args,
        **element_form_kwargs
    )
    relation_form = forms.FormElementsRelationship(
        *relation_form_args,
        **relation_form_kwargs
    )

    if proposal_form:
        form = get_object_or_404(core_models.ProposalForm, pk=form_id)
        element_form = forms.ProposalElement(
            *element_form_args,
            **element_form_kwargs
        )
        relation_form = forms.ProposalElementRelationship(
            *relation_form_args,
            **relation_form_kwargs
        )

    if element_form.is_valid() and relation_form.is_valid():
        new_element = element_form.save()
        new_relation = relation_form.save(commit=False)
        new_relation.form = form
        new_relation.element = new_element
        new_relation.save()

        if proposal_form:
            form.proposal_fields.add(new_relation)
        else:
            form.form_fields.add(new_relation)

        return redirect(
            reverse(
                'manager_edit_form',
                kwargs={
                    'form_type': form_type,
                    'form_id': form_id
                }
            )
        )

    template = 'manager/{}/edit_form.html'.format(form_type)
    context = {
        'form': form,
        'fields': form_order_field_list(form_type, form_id),
        'element_form': element_form,
        'relation_form': relation_form,
    }

    return render(request, template, context)


@is_press_editor
def preview_proposal_form(request, form_id):
    form = get_object_or_404(core_models.ProposalForm, pk=form_id)

    preview_form = forms.GeneratedForm(
        form=core_models.ProposalForm.objects.get(pk=form_id)
    )
    fields = core_models.ProposalFormElementsRelationship.objects.filter(
        form=form,
    )
    default_fields = forms.DefaultForm()

    template = 'manager/proposal/preview_form.html'
    context = {
        'form': form,
        'preview_form': preview_form,
        'fields': fields,
        'default_fields': default_fields,
    }
    return render(request, template, context)


@is_press_editor
def delete_form_element(request, form_type, form_id, relation_id):
    """Delete the given form element from the given form."""
    form_model = review_models.Form
    element_model = review_models.FormElementsRelationship
    if form_type == 'proposal':
        form_model = core_models.ProposalForm
        element_model = core_models.ProposalFormElementsRelationship

    get_object_or_404(form_model, pk=form_id)
    relation = get_object_or_404(
        element_model,
        pk=relation_id,
    )

    relation.element.delete()
    relation.delete()

    return redirect(
        reverse(
            'manager_edit_form',
            kwargs={
                'form_type': form_type,
                'form_id': form_id
            }
        )
    )


@is_press_editor
def review_forms(request):
    template = 'manager/review/forms.html'
    context = {'review_forms': review_models.Form.objects.all()}

    return render(request, template, context)


@is_press_editor
def preview_review_form(request, form_id):
    form = get_object_or_404(review_models.Form, pk=form_id)

    preview_form = forms.GeneratedReviewForm(
        form=review_models.Form.objects.get(pk=form_id)
    )
    fields = review_models.FormElementsRelationship.objects.filter(form=form)

    template = 'manager/review/preview_form.html'
    context = {
        'form': form,
        'preview_form': preview_form,
        'fields': fields,
    }

    return render(request, template, context)


@is_press_editor
def handle_file(request, file):
    original_filename = smart_text(
        file._get_name()
    ).replace(
        ',', '_'
    ).replace(
        ';', '_'
    )
    filename = str(uuid4()) + '.' + str(os.path.splitext(original_filename)[1])
    folder_structure = os.path.join(settings.BASE_DIR, 'media', 'settings')

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)

    path = os.path.join(folder_structure, str(filename))
    fd = open(path, 'wb')

    for chunk in file.chunks():
        fd.write(chunk)

    fd.close()

    return filename


# AJAX Handler

@is_press_editor
@csrf_exempt
def groups_order(request):
    groups = models.Group.objects.all()

    if request.POST:
        ids = request.POST.getlist('%s[]' % 'group')
        ids = [int(_id) for _id in ids]
        for group in groups:
            group.sequence = ids.index(group.id)  # Get the index.
            group.save()

        response = 'Thanks'
    else:
        response = 'Nothing to process, post required'

    return HttpResponse(response)


@is_press_editor
@csrf_exempt
def group_members_order(request, group_id):
    group = get_object_or_404(models.Group, pk=group_id)
    memberships = models.GroupMembership.objects.filter(group=group)

    if request.POST:
        ids = request.POST.getlist('%s[]' % 'member')
        ids = [int(_id) for _id in ids]
        for membership in memberships:
            membership.sequence = ids.index(membership.id)  # Get the index.
            membership.save()

        response = 'Thanks'
    else:
        response = 'Nothing to process, post required'

    return HttpResponse(response)


@is_press_editor
@csrf_exempt
def checklist_order(request):
    checklist_items = submission_models.SubmissionChecklistItem.objects.all()

    if request.POST:
        ids = request.POST.getlist('%s[]' % 'check')
        ids = [int(_id) for _id in ids]

        for item in checklist_items:
            item.sequence = ids.index(item.id)
            item.save()

        response = 'Thanks'
    else:
        response = 'Nothing to process, POST required.'

    return HttpResponse(response)
