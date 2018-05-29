from author.logic import author_tasks
from core import logic, models as core_models
from core.cache import cache_result
from django.core.exceptions import DisallowedHost


@cache_result(300)
def press(request):
    return {'press': logic.press_settings()}


def task_count(request):
    return {'task_count': logic.task_count(request)}


def switch_account(request):
    if request.user.is_authenticated():
        if core_models.Profile.objects.filter(user=request.user):
            user_roles = [
                role.slug for role in request.user.profile.roles.all()
            ]
            if 'press-editor' in user_roles:
                return {'switch_account': True}
            return {'switch_account': False}
    return {'switch_account': False}


def review_assignment_count(request):
    return {'review_assignment_count': logic.review_assignment_count(request)}


def onetasker_task_count(request):
    if request.user.is_authenticated():
        onetasker_tasks = logic.onetasker_tasks(request.user)
        return {'onetasker_task_count': len(onetasker_tasks.get('active')), }
    return {'onetasker_task_count': 0}


def author_task_count(request):
    return {'author_task_count': len(author_tasks(request.user))}


def roles(request):
    if request.user.is_authenticated() and hasattr(request.user, 'profile'):
        return {
            'roles': [
                role.slug for role in request.user.profile.roles.all()
            ]
        }
    return {'roles': ''}


def domain(request):
    try:
        return {'domain': request.get_host()}
    except DisallowedHost:
        return None
