from django.contrib import admin
from models import Target, Ping, Uptime

# Register your models here.
admin.site.register(Target)
admin.site.register(Ping)
admin.site.register(Uptime)
