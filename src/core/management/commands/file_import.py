from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from core import models

import sys
import json
import os
import shutil

data_file_path = sys.argv[2]
files_dir = sys.argv[3]
press_code = sys.argv[4]

class Command(BaseCommand):

    help = "Takes UPCDN data and creates JSON for RUA."

    def add_arguments(self, parser):
        parser.add_argument('data_file_path')
        parser.add_argument('files_dir')
        parser.add_argument('press_code')

    def handle(self, *args, **options):

        book_list = models.Book.objects.all()
        for book in book_list:
            print book.pub_id()

        with open(data_file_path) as data_file:
            formats = json.load(data_file)

        rua_dir = settings.BOOK_DIR
        if not os.path.exists(rua_dir):
            os.makedirs(rua_dir)

        for book in book_list:
            book_formats = formats[book.pub_id()]

            for format in book_formats:
                if not format.get('file_type') == 'HARDBACK' and not format.get('file_type') == 'PAPERBACK':

                    rua_book_folder = os.path.join(rua_dir, str(book.pk))
                    if not os.path.exists(rua_book_folder):
                        os.makedirs(rua_book_folder)

                    shutil.copyfile(os.path.join(files_dir, press_code, 'press_files', str(format.get('omp_book_id')), format.get('file_name')), os.path.join(rua_book_folder, format.get('file_name')))

                    owner = User.objects.get(email='tech@ubiquitypress.com')

                    new_file = models.File.objects.create(
                        original_filename=format.get('file_name'),
                        uuid_filename=format.get('file_name'),
                        stage_uploaded=1,
                        kind=format.get('file_type'),
                        label=format.get('file_type'),
                        owner=owner
                    )

                    models.Format.objects.create(
                        book=book,
                        file=new_file,
                        name=format.get('file_name'),
                        identifier=format.get('identifier'),
                        sequence=1,
                        file_type=format.get('file_type'),
                    )

                    models.Identifier.objects.create(
                        book=book,
                        identifier='isbn-10',
                        value=format.get('isbn'),
                        displayed=True,
                    )
