from django.contrib import admin

from .models import CoverImageProof


admin_list = [
    (CoverImageProof,),
]

[admin.site.register(*t) for t in admin_list]
