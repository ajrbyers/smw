import mimetypes

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
        reply_to = get_setting('from_address', 'email')

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
        # Hide access key in email log.
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
        reply_to = get_setting('from_address', 'email')

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
    from_email = get_setting('from_address', 'email')
    base_url = get_setting('base_url', 'general')

    reset_url = 'http://{base_url}/login/reset/code/{reset_code}/'.format(
        base_url=base_url,
        reset_code=reset_code
    )
    context = {'reset_code': reset_code, 'reset_url': reset_url, 'user': user}

    send_email(
        get_setting('reset_code_subject', 'email_subject', '[abp] Reset Code'),
        context,
        from_email,
        user.email,
        email_text,
        kind='general',
    )


def send_prerendered_email(
        html_content,
        subject,
        from_email,
        to,
        bcc=None,
        cc=None,
        attachments=None,
        book=None,
        proposal=None,
):

    if not type(to) in (list, tuple):
        to = [to]

    from_email = from_email or get_setting(
        'from_address',
        'general',
        'noreply@rua.re'
    )

    msg = EmailMessage(
        subject,
        html_content,
        from_email,
        to,
        bcc=bcc,
        cc=cc,
        reply_to=[from_email],
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
        )

    msg.content_subtype = "html"

    if attachments:
        for attachment in attachments:
            filepath = filepath_general(attachment)
            with open(filepath, 'rb') as file:
                content = file.read()

            # TODO: drop ascii encoding when Django is upgraded
            # to support unicode filenames
            try:
                filename = attachment.original_filename.encode('ascii')
            except UnicodeEncodeError:
                filename = (
                    'utf-8',
                    '',
                    attachment.original_filename.encode('utf-8')
                )
            mimetype = mimetypes.guess_type(filepath)[0] or 'unknown'

            msg.attach(
                filename=filename,
                content=content,
                mimetype=mimetype,
            )

    msg.send()


def get_email_body(request, setting_name, context):
    """Renders an email body based on a template setting and context.

    Args:
        request(django.http.request.HttpRequest): request from the calling view.
        setting_name(str): name of the email setting used as a template.
        context(dict): context data to be substituted into the email body.

    Returns:
        str: the rendered email body.
    """
    html_template = get_setting(setting_name, 'email')
    html_template.replace('\n', '<br />')

    template_renderer = Template(html_template)
    con = RequestContext(request)
    con.push(context)
    html_content = template_renderer.render(con)

    return html_content


def get_email_subject(request, setting_name, context):
    """Renders an email subject based on a template setting and context.

    Args:
        request(django.http.request.HttpRequest): request from the calling view.
        setting_name(str): name of the email_subject setting used as a template.
        context(dict): context data to be substituted into the email subject.

    Returns:
        str: the rendered email subject.
    """
    subject_template = get_setting(setting_name, 'email_subject')

    template_renderer = Template(subject_template)
    con = RequestContext(request)
    con.push(context)
    rendered_email_subject = template_renderer.render(con)

    return rendered_email_subject


def get_email_greeting(recipients, adjective='Dear'):
    """Composes an email greeting to a list of Users.

    Args:
        recipients (list): ordered enumerable containing Users.
        adjective (str): the leading adjective to the greeting.

    Returns:
         str: an email greeting to one or more users.

    """
    recipient_forenames = [recipient.first_name for recipient in recipients]

    return '{adjective} {recipients}'.format(
        adjective=adjective,
        recipients=', '.join(
            filter(
                None,
                [', '.join(recipient_forenames[:-2])] +
                [' and '.join(recipient_forenames[-2:])]
            )
        )
    )
