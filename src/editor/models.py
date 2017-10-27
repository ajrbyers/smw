from django.db import models
from django.contrib.auth.models import User


class CoverImageProof(models.Model):
    book = models.ForeignKey('core.Book')
    editor = models.ForeignKey(User, verbose_name='editor')

    assigned = models.DateField(auto_now_add=True)
    note_to_author = models.TextField(
        help_text='Provide some notes on the cover for the author.')

    completed = models.DateField(blank=True, null=True)
    note_to_editor = models.TextField(
        help_text='Provide some feedback to the Editor on the cover image.')
