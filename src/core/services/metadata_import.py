import csv
import ftplib

from core import models


def _read_csv(path):
    # Clean NULL bytes
    old_csv = open(path, 'rb')
    data = old_csv.read()
    old_csv.close()
    new_csv = open('new.csv', 'wb')
    new_csv.write(data.replace('\00', ''))
    new_csv.close()

    with open('new.csv', 'rb') as f:
        reader = csv.reader(f.read().splitlines())
        return reader


def write_data():
    ftp = ftplib.FTP('ftp.siliconchips-services.com')
    ftp.login('ubiquitypress', '1234@UP!SC?')
    ftp.cwd('/rua-metadata-test')
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

            for row in data:
                isbn = row[isbn_index]
                bisac = row[bisac_index]
                description = row[description_index]

                identifier = models.Identifier.objects.filter(value=isbn).first()

                if identifier:
                    book = identifier.book
                    bisac_lookup = [
                        row for row in _read_csv('bisac.csv') if bisac in row
                    ]
                    subject, created = models.Subject.objects.get_or_create(
                        name=bisac_lookup[0][1]
                    )

                    book.subject.add(subject)
                    book.description = description

                    book.save()
                    print book.subject, book.description