from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context, Template, RequestContext

from core import log, models
from setting_util import get_setting


def filepath(book, attachment):
    return '{dir}/{id}/{uuid}'.format(
        dir=settings.BOOK_DIR,
        id=book.id,
        uuid=attachment.uuid_filename,
    )


def filepath_proposal(proposal, attachment):
    return '{proposal}/{id}/{uuid}'.format(
        proposal=settings.PROPOSAL_DIR,
        id=proposal.id,
        uuid=attachment.uuid_filename,
    )


def filepath_general(attachment):
    return '{dir}/{uuid}'.format(
        dir=settings.EMAIL_DIR,
        uuid=attachment.uuid_filename,
    )


def send_email(
        subject,
        context,
        from_email,
        to,
        html_template,
        bcc=None,
        cc=None,
        book=None,
        attachment=None,
        proposal=None,
        request=None,
        kind=None,
        access_key=None,
):
    html_template.replace('\n', '<br />')
    htmly = Template(html_template)
    con = Context(context)
    html_content = htmly.render(con)

    if not type(to) in [list, tuple]:
        to = [to]

    if request:
        reply_to = request.user.email
    else:
        reply_to = models.Setting.objects.get(
            group__name='email',
            name='from_address',
        ).value

    msg = EmailMessage(
        subject,
        html_content,
        from_email,
        to,
        bcc=bcc,
        cc=cc,
        headers={'Reply-To': reply_to}
    )

    if access_key:
        # Hide access key in email log
        html_content = html_content.replace(str(access_key), '')

        if book:
            log.add_email_log_entry(
                book=book,
                subject=subject,
                from_address=from_email,
                to=to,
                bcc=bcc,
                cc=cc,
                content=html_content,
                attachment=attachment,
                kind=kind,
            )

        if proposal:
            log.add_email_log_entry(
                proposal=proposal,
                subject=subject,
                from_address=from_email,
                to=to,
                bcc=bcc,
                cc=cc,
                content=html_content,
                attachment=attachment,
                kind=kind,
            )
    else:
        if book:
            log.add_email_log_entry(
                book=book,
                subject=subject,
                from_address=from_email,
                to=to,
                bcc=bcc,
                cc=cc,
                content=html_content,
                attachment=attachment,
                kind=kind,
            )

        if proposal:
            log.add_email_log_entry(
                proposal=proposal,
                subject=subject,
                from_address=from_email,
                to=to,
                bcc=bcc,
                cc=cc,
                content=html_content,
                attachment=attachment,
                kind=kind,
            )

    msg.content_subtype = "html"

    if attachment:
        if book:
            msg.attach_file(filepath(book, attachment))
        elif proposal:
            msg.attach_file(filepath_proposal(proposal, attachment))
        else:
            msg.attach_file(filepath_general(attachment))

    msg.send()


def send_email_multiple(
        subject,
        context,
        from_email,
        to,
        html_template,
        bcc=None,
        cc=None,
        book=None,
        attachments=None,
        proposal=None,
        request=None,
        kind=None,
):
    html_template.replace('\n', '<br />')
    htmly = Template(html_template)
    con = Context(context)
    html_content = htmly.render(con)

    if not type(to) in [list, tuple]:
        to = [to]

    if request:
        reply_to = request.user.email
    else:
        reply_to = models.Setting.objects.get(
            group__name='email',
            name='from_address',
        )

    msg = EmailMessage(
        subject,
        html_content,
        from_email,
        to,
        bcc=bcc,
        cc=cc,
        headers={'Reply-To': reply_to}
    )

    if book:
        log.add_email_log_entry_multiple(
            book=book,
            subject=subject,
            from_address=from_email,
            to=to,
            bcc=bcc,
            cc=cc,
            content=html_content,
            attachments=attachments,
            kind=kind,
        )
    if proposal:
        log.add_email_log_entry_multiple(
            proposal=proposal,
            subject=subject,
            from_address=from_email,
            to=to,
            bcc=bcc,
            cc=cc,
            content=html_content,
            attachments=attachments,
            kind=kind,
        )

    msg.content_subtype = "html"

    if attachments:
        for attachment in attachments:
            if book:
                msg.attach_file(filepath(book, attachment))
            elif proposal:
                msg.attach_file(filepath_proposal(proposal, attachment))
            else:
                msg.attach_file(filepath_general(attachment))

    msg.send()


def send_reset_email(user, email_text, reset_code):
    from_email = models.Setting.objects.get(
        group__name='email',
        name='from_address',
    )
    base_url = models.Setting.objects.get(
        group__name='general',
        name='base_url',
    )

    reset_url = 'http://%s/login/reset/code/%s/' % (base_url.value, reset_code)
    context = {'reset_code': reset_code, 'reset_url': reset_url, 'user': user}

    send_email(
        get_setting('reset_code_subject', 'email_subject', '[abp] Reset Code'),
        context,
        from_email.value,
        user.email,
        email_text,
        kind='general',
    )


def send_prerendered_email(
        request,
        html_template,
        subject,
        to,
        bcc=None,
        cc=None,
        attachments=None,
        book=None,
        proposal=None,
):
    html_content = html_template

    if not type(to) in [list, tuple]:
        to = [to]

    if request:
        reply_to = request.user.email
    else:
        reply_to = models.Setting.objects.get(
            group__name='email',
            name='from_address',
        )

    from_email = get_setting('from_address', 'general', 'noreply@rua.re')
    msg = EmailMessage(
        subject,
        html_content,
        from_email,
        to,
        bcc=bcc,
        cc=cc,
        headers={'Reply-To': reply_to},
    )

    if book:
        log.add_email_log_entry_multiple(
            book=book,
            subject=subject,
            from_address=reply_to,
            to=to,
            bcc=bcc,
            cc=cc,
            content=html_content,
            attachments=attachments if attachments else None,
        )

    if proposal:
        log.add_email_log_entry_multiple(
            proposal=proposal,
            subject=subject,
            from_address=reply_to,
            to=to,
            bcc=bcc,
            cc=cc,
            content=html_content,
            attachments=attachments if attachments else None,
        )

    msg.content_subtype = "html"

    if attachments:
        for attachment in attachments:
            if attachment:
                msg.attach_file(filepath_general(attachment))

    msg.send()


def get_email_content(request, setting_name, context):
    try:
        html_template = models.Setting.objects.get(
            group__name='email',
            name=setting_name,
        ).value
    except models.Setting.DoesNotExist:
        html_template = ''

    html_template.replace('\n', '<br />')
    htmly = Template(html_template)
    con = RequestContext(request)
    con.push(context)
    html_content = htmly.render(con)

    return html_content
