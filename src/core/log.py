from core import models


def add_log_entry(book, user, kind, message, short_name):
    new_log_entry = models.Log(
        book=book,
        user=user,
        kind=kind,
        message=message,
        short_name=short_name,
    )
    new_log_entry.save()

    return new_log_entry


def add_proposal_log_entry(proposal, user, kind, message, short_name):
    new_log_entry = models.Log(
        proposal=proposal,
        user=user,
        kind=kind,
        message=message,
        short_name=short_name,
    )
    new_log_entry.save()

    return new_log_entry


def list_to_text(email_list):
    emails = ""
    last = len(email_list) - 1

    for index, email in enumerate(email_list):
        emails = emails + email
        if not index == last:
            emails = emails + ", "

    return emails


def add_email_log_entry(
        subject,
        from_address,
        to,
        bcc,
        cc,
        content,
        attachment=None,
        proposal=None,
        book=None,
        kind=None,
):
    if proposal:
        log_dict = {
            'proposal': proposal,
            'kind': kind if kind else 'general',
            'subject': subject,
            'from_address': from_address,
            'to': list_to_text(to) if to else '',
            'cc': list_to_text(cc) if cc else '',
            'bcc': list_to_text(bcc) if bcc else '',
            'content': content,
        }
    else:
        log_dict = {
            'book': book,
            'kind': kind if kind else 'general',
            'subject': subject,
            'from_address': from_address,
            'to': list_to_text(to) if to else '',
            'cc': list_to_text(cc) if cc else '',
            'bcc': list_to_text(bcc) if bcc else '',
            'content': content,
        }

    new_log_entry = models.EmailLog(**log_dict)
    new_log_entry.save()

    if attachment:
        new_log_entry.attachment.add(attachment)
    new_log_entry.save()

    return new_log_entry


# Temporary function while all email forms are tweaked
# to handle multiple attachments
def add_email_log_entry_multiple(
        subject,
        from_address,
        to,
        bcc,
        cc,
        content,
        attachments=None,
        proposal=None,
        book=None,
        kind=None,
):
    if proposal:
        log_dict = {
            'proposal': proposal,
            'kind': kind if kind else 'general',
            'subject': subject,
            'from_address': from_address,
            'to': list_to_text(to) if to else '',
            'cc': list_to_text(cc) if cc else '',
            'bcc': list_to_text(bcc) if bcc else '',
            'content': content,
        }
    else:
        log_dict = {
            'book': book,
            'kind': kind if kind else 'general',
            'subject': subject,
            'from_address': from_address,
            'to': list_to_text(to) if to else '',
            'cc': list_to_text(cc) if cc else '',
            'bcc': list_to_text(bcc) if bcc else '',
            'content': content,
        }

    new_log_entry = models.EmailLog(**log_dict)
    new_log_entry.save()

    if attachments:
        for attachment in attachments:
            if attachment:
                new_log_entry.attachment.add(attachment)

    new_log_entry.save()

    return new_log_entry
