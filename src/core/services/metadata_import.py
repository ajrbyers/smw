import csv
import ftplib

from core import models, email
from core.setting_util import get_setting


def _read_csv(path):
    """Read a CSV and return its rows, cleaning NUL bytes."""
    old_csv = open(path, 'rb')
    data = old_csv.read()
    old_csv.close()
    new_csv = open('new.csv', 'wb')
    new_csv.write(data.replace('\00', ''))
    new_csv.close()

    with open('new.csv', 'rb') as f:
        reader = csv.reader(f.read().splitlines())
        return reader


def add_metadata():
    ftp = ftplib.FTP(
        get_setting(
            setting_name='metadata_ftp_url',
            setting_group_name='general',
            default='ftp.siliconchips-services.com',
        )
    )
    ftp.login(
        get_setting(
            setting_name='metadata_ftp_username',
            setting_group_name='general',
            default='ubiquitypress',
        ),
        get_setting(
            setting_name='metadata_ftp_password',
            setting_group_name='general',
            default='1234@UP!SC?',
        )
    )
    ftp.cwd(
        get_setting(
            setting_name='metadata_ftp_folder',
            setting_group_name='general',
            default='/rua-metadata-test',
        )
    )
    files = []

    try:
        files = ftp.nlst()
    except ftplib.error_perm, resp:
        if str(resp) == '550 No files found':
            print 'No files in this directory'
        else:
            raise

    for f in files:
        if '.csv' in f:
            ftp.retrbinary('RETR ' + f, open(f, 'wb').write)
            # ftp.delete(f)
            ftp.close()

            _csv = _read_csv(f)
            headers = next(_csv)
            isbn_index = headers.index('ISBN13')
            bisac_index = headers.index('Bisac Code(s)')
            description_index = headers.index('Long Description')
            data = [row for row in _csv]
            isbns_processed = []

            for row in data:
                isbn = row[isbn_index]
                bisacs = row[bisac_index]
                description = row[description_index]
                identifier = models.Identifier.objects.filter(value=isbn).first()

                if identifier and isbn not in isbns_processed:
                    book = identifier.book

                    for subj in book.subject.all():
                        book.subject.remove(subj)

                    for bisac in bisacs.split():
                        bisac_lookup = [
                            row for row in _read_csv('bisac.csv') if bisac in row
                        ]
                        new_subject, created = models.Subject.objects.get_or_create(
                            name=bisac_lookup[0][1]
                        )

                        book.subject.add(new_subject)
                    book.description = description

                    book.save()

                    email_context = {
                        'book': book,
                    }

                    for editor in book.all_editors():
                        email.send_email(
                            subject='Metadata updated',
                            context=email_context,
                            from_email='noreply@rua.re',
                            to=editor.email,
                            html_template='Test'
                        )

                isbns_processed.append(isbn)
