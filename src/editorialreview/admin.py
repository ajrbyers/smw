from django.contrib import admin
from models import *

admin_list = [
    (EditorialReview,),
]

[admin.site.register(*t) for t in admin_list]
from django.contrib import admin
