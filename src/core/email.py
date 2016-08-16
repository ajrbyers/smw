from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context, Template, RequestContext
from django.conf import settings
from setting_util import get_setting
from core import models
from core import log

from pprint import pprint

def filepath(book, attachment):
    return '%s/%s/%s' % (settings.BOOK_DIR, book.id, attachment.uuid_filename)
def filepath_proposal(proposal, attachment):
    return '%s/%s/%s' % (settings.PROPOSAL_DIR, proposal.id, attachment.uuid_filename)

def filepath_general(attachment):
    return '%s/%s' % (settings.EMAIL_DIR, attachment.uuid_filename)

def send_email(subject, context, from_email, to, html_template, bcc=None, cc=None, book=None, attachment=None, proposal=None, request=None, kind = None):

    html_template.replace('\n', '<br />')

    htmly = Template(html_template)
    con = Context(context)
    html_content = htmly.render(con)

    if not type(to) in [list,tuple]:
        to = [to]

    if request:
        reply_to = request.user.email
    else:
        reply_to = models.Setting.objects.get(group__name='email', name='from_address')

    msg = EmailMessage(subject, html_content, from_email, to, bcc=bcc, cc=cc, headers={'Reply-To': reply_to})

    if book:
        log.add_email_log_entry(book = book, subject = subject, from_address = from_email, to = to, bcc = bcc, cc = cc, content = html_content, attachment = attachment, kind = kind)
    if proposal:
        log.add_email_log_entry(proposal = proposal, subject = subject, from_address = from_email, to = to, bcc = bcc, cc = cc, content = html_content, attachment = attachment, kind = kind)

    msg.content_subtype = "html"

    if attachment:
        if book:
            msg.attach_file(filepath(book, attachment))
        elif proposal:
            msg.attach_file(filepath_proposal(proposal, attachment))
        else:
            msg.attach_file(filepath_general(attachment))

    msg.send()

def send_reset_email(user, email_text, reset_code):

    from_email = models.Setting.objects.get(group__name='email', name='from_address')
    base_url = models.Setting.objects.get(group__name='general', name='base_url')

    reset_url = 'http://%s/login/reset/code/%s/' % (base_url.value,reset_code)

    context = {
        'reset_code': reset_code,
        'reset_url':reset_url,
        'user': user,
    }

    send_email(get_setting('reset_code_subject','email_subject','[abp] Reset Code'), context, from_email.value, user.email, email_text, kind = 'general')

def get_email_content(request, setting_name, context):

    try:
        html_template = models.Setting.objects.get(group__name='email', name=setting_name).value
    except models.Setting.DoesNotExist:
        html_template = ''

    html_template.replace('\n', '<br />')

    htmly = Template(html_template)
    con = RequestContext(request)
    con.push(context)
    html_content = htmly.render(con)

    return html_content

