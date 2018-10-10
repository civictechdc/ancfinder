from models import *
from django.contrib import admin

class AuthRecordAdmin(admin.ModelAdmin):
        readonly_fields = ("uid", "provider")
        raw_id_fields = ('user',)
        search_fields = ["user__username", "user__email", "uid"]
        list_display = ["user", "provider", "uid"]

admin.site.register(AuthRecord, AuthRecordAdmin)

