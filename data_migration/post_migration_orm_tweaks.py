"""This script is intended to copied and pasted into a Django shell.
In the interests of cleanliness, this code should be idempotent.
Running it more than once should have the same effect as running it once.
"""

# Amend the paths of book covers
from core.models import Book
books = Book.objects.all()
for book in books:
    if book.cover and 'files/media' not in book.cover.name:
        book.cover = f'files/media/{book.cover.name}'
        book.save()

