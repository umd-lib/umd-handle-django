from django.contrib import admin

from .models import Handle

class HandleAdmin(admin.ModelAdmin):
    fields = [
        'prefix', 'suffix', 'url', 'repo', 'repo_id', 'description', 'notes',
        'created', 'modified',
    ]
    readonly_fields = ['created', 'modified']

    list_display = (
        'prefix', 'suffix', 'url', 'repo', 'repo_id', 'modified'
    )
    # Default order for admin list - modified descending
    ordering = ['-modified']

admin.site.register(Handle, HandleAdmin)
