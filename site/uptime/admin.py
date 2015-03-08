from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Target)
admin.site.register(models.Ping)
admin.site.register(models.Uptime)
