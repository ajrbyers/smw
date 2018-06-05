import random

from core import email
from core.setting_util import get_setting


def generate_password():
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pw_length = 8
    mypw = ""

    for i in range(pw_length):
        next_index = random.randrange(len(alphabet))
        mypw = mypw + alphabet[next_index]

    return mypw


def send_new_user_ack(email_text, new_user, code):
    from_email = get_setting('from_address', 'email')
    press_name = get_setting('press_name', 'general')
    principal_contact_name = get_setting('primary_contact_name', 'general')

    context = {
        'base_url': get_setting('base_url', 'general',),
        'user': new_user,
        'press_name': press_name,
        'principal_contact_name': principal_contact_name,
        'code': code,
    }

    email.send_email(
        get_setting(
            'new_user_subject',
            'email_subject',
            'New User : Profile Details'
        ),
        context,
        from_email,
        new_user.email,
        email_text,
        kind='general',
    )
