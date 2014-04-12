from django.contrib import admin

from punchcard import models

admin.site.register(models.Entry)
admin.site.register(models.Category)
