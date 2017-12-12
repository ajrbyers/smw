import csv

from core import models


def read_csv(path):
    # Clean NULL bytes
    old_csv = open(path, 'rb')
    data = old_csv.read()
    old_csv.close()
    new_csv = open('new.csv', 'wb')
    new_csv.write(data.replace('\00', ''))
    new_csv.close()

    with open('new.csv', 'rb') as f:
        reader = csv.reader(f.read().splitlines())
        next(reader, None)
        data = [row for row in reader]

        return data

def write_data(path):
    csv = read_csv(path)

    for row in csv:
        isbn = row[1]

        isbns = models.Identifier.objects.filter(value=isbn)
        print isbns

write_data('/Users/stuartjennings/ucp.csv')
