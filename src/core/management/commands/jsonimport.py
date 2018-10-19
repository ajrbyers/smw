from django.core.management.base import BaseCommand
from core import models
import json

file = 'ucp'

class Command(BaseCommand):

    help = 'Import books via JSON'

    def handle(self, *args, **options):
        if file is None:
            print('Please supply a file path')
        else:
            with open('/user/home/tech/rua_data/%s.json' % file) as data_file:
                book_list = json.load(data_file)
                for book in book_list:

                    book_dict = {
                        "book_type": book.get('book_type'),
                        "description": book.get('description'),
                        "pages": book.get('pages'),
                        "prefix": book.get('prefix'),
                        "publication_date": book.get('publication_date'),
                        "review_type": book.get('review_type'),
                        "slug": book.get('slug'),
                        "subtitle": book.get('subtitle'),
                        "title": book.get('title'),
                    }

                    new_book = models.Book.objects.create(**book_dict)

                    for author in book.get('author'):
                        new_author = models.Author.objects.create(**author)
                        new_book.author.add(new_author)

                    for keyword in book.get('keywords'):
                        new_keyword, created = models.Keyword.objects.get_or_create(**keyword)
                        new_book.keywords.add(new_keyword)

                    for language in book.get('languages'):
                        new_language, created = models.Language.objects.get_or_create(**language)
                        new_book.languages.add(new_language)

                    for subject in book.get('subject'):
                        new_subject, create = models.Subject.objects.get_or_create(**subject)
                        new_book.subject.add(new_subject)

                    models.Identifier.objects.create(
                        book=new_book,
                        identifier='doi',
                        value=book.get('doi'),
                        displayed=True,
                    )

                    models.Identifier.objects.create(
                        book=new_book,
                        identifier='pub_id',
                        value=book.get('pub_id'),
                        displayed=True,
                    )

                    stage = models.Stage.objects.create(current_stage="published")

                    new_book.stage = stage
                    new_book.save()

                    print(new_book.title)
