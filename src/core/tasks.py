from __future__ import absolute_import
import csv
import ftplib
from io import StringIO
import os
from django.conf import settings

from celery import task

from core import models, email
from services import ServiceHandler, JuraUpdateService
from core.setting_util import get_setting


def _read_csv(path):
    """Read a CSV and return its rows, cleaning NUL bytes."""

    with open(path, 'rb') as raw_csv:
        data = raw_csv.read().replace('\00', '')
    if path != 'bisac.csv':
        os.remove(path)

    _buffer = StringIO.StringIO(data)
    reader = csv.reader(
        _buffer.read().splitlines()
    )
    return reader


@task(name='add-metadata')
def add_metadata():
    """Adds book metadata from CSVs on an FTP site.

    Accesses a specified FTP dir, copies CSVs to the local dir then deletes them
    from FTP, reads the CSV and matches ISBN13s to Rua books and updates their
    metadata with the matching CSV column values, and sends a notification
    email.
    """
    if settings.FTP_METADATA_FEATURE:
        service = ServiceHandler(service=JuraUpdateService)

        ftp = ftplib.FTP(getattr(settings, 'FTP_URL', None))
        ftp.login(
            getattr(settings, 'FTP_USERNAME', None),
            getattr(settings, 'FTP_PASSWORD', None)
        )
        ftp.cwd(getattr(settings, 'FTP_FOLDER', None))
        files = []

        try:
            files = ftp.nlst()
        except ftplib.error_perm as resp:
            if str(resp) == '550 No files found':
                print('No files in this directory')
            else:
                raise

        for _file in files:
            if '.csv' in _file:
                ftp.retrbinary(
                    'RETR {}'.format(_file),
                    open(_file, 'wb').write
                )
                ftp.delete(_file)
                ftp.close()

                _csv = _read_csv(_file)
                headers = next(_csv)
                isbn_index = headers.index('ISBN13')
                bisac_index = headers.index('Bisac Code(s)')
                description_index = headers.index('Long Description')
                isbns_processed = []

                for row in _csv:
                    isbn = row[isbn_index]
                    if '-' not in isbn:  # Add hyphens to ISBNs: match UCP Rua.
                        isbn = '-'.join(
                            [
                                isbn[:3],
                                isbn[3],
                                isbn[4:7],
                                isbn[7:12],
                                isbn[12]
                            ]
                        )
                    bisacs = row[bisac_index]
                    description = row[description_index]
                    identifier = models.Identifier.objects.filter(
                        value=isbn
                    ).first()

                    if identifier and isbn not in isbns_processed:
                        book = identifier.book

                        for subj in book.subject.all():
                            book.subject.remove(subj)

                        for bisac in bisacs.split():
                            bisac_lookup = [
                                row for row
                                in _read_csv('bisac.csv') if bisac in row
                            ]
                            new_subject, _ = (
                                models.Subject.objects.get_or_create(
                                    name=bisac_lookup[0][1]
                                )
                            )

                            book.subject.add(new_subject)

                        book.description = description
                        book.save()

                        for editor in book.get_all_editors():
                            email_context = {
                                'book': book,
                                'editor': editor,
                                'new_subjects': ','.join(
                                    [
                                        str(subj.name).encode('utf-8')
                                        for subj in book.subject.all()
                                    ]
                                )
                            }
                            email_text = get_setting('metadata_update', 'email')
                            email.send_email(
                                subject='Metadata updated',
                                context=email_context,
                                from_email='noreply@rua.re',
                                to=editor.email,
                                html_template=email_text
                            )
                        service.send(book.pk)

                    isbns_processed.append(isbn)
