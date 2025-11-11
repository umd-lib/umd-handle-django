from django.contrib import admin

from .models import Handle, JWTToken

class HandleModelAdmin(admin.ModelAdmin):
    fields = [
        'prefix', 'suffix', 'url', 'repo', 'repo_id', 'description', 'notes',
        'created', 'modified',
    ]
    readonly_fields = ['created', 'modified']

admin.site.register(Handle, HandleModelAdmin)
