import random

from core.setting_util import get_setting
from core import email
from core import models


def generate_password():
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pw_length = 8
    mypw = ""

    for i in range(pw_length):
        next_index = random.randrange(len(alphabet))
        mypw = mypw + alphabet[next_index]

    return mypw


def send_new_user_ack(email_text, new_user, code):
    from_email = models.Setting.objects.get(group__name='email',
                                            name='from_address')

    try:
        press_name = models.Setting.objects.get(group__name='general',
                                                name='press_name').value
    except:
        press_name = None
    try:
        principal_contact_name = models.Setting.objects.get(
            group__name='general', name='primary_contact_name').value
    except:
        principal_contact_name = None

    context = {
        'base_url': models.Setting.objects.get(group__name='general',
                                               name='base_url').value,
        'user': new_user,
        'press_name': press_name,
        'principal_contact_name': principal_contact_name,
        'code': code,
    }

    email.send_email(get_setting('new_user_subject', 'email_subject',
                                 'New User : Profile Details'), context,
                     from_email.value, new_user.email, email_text,
                     kind='general')
