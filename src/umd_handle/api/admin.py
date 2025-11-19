from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.db.models import Value
from django.db.models.functions import Concat
from django.utils.html import format_html

from .models import Handle

# Customize the site header, title, and admin index page title
admin.site.site_header = "UMD Handle Service"
admin.site.site_title = "UMD Handle Service"
admin.site.index_title = "UMD Handle Service Admin Portal"

# Unregister User and Group, because authentication/authorization is controlled
# the Grouper, so there is no need to show these entries in the admin interface
admin.site.unregister(User)
admin.site.unregister(Group)


class HandleAdmin(admin.ModelAdmin):
    fields = [
        'prefix', 'suffix', 'url', 'repo', 'repo_id', 'description', 'notes',
        'created', 'modified',
    ]
    readonly_fields = ('suffix', 'created', 'modified')

    list_display = (
        'combined_handle', 'url_link', 'repo', 'repo_id', 'modified'
    )
    # Default order for admin list - modified descending
    ordering = ['-modified']

    search_fields = [
        'prefix', 'suffix', 'url', 'repo', 'repo_id', 'description', 'notes'
    ]

    list_filter = ('repo', 'created', 'modified')

    @admin.display(description='URL', ordering='url')
    def url_link(self, obj):
        return format_html('<a href="{url}">{url}</a>', url=obj.url)

    @admin.display(description='Handle', ordering=Concat('prefix', Value(' '), 'suffix'))
    def combined_handle(self, obj):
        return str(obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            # Editing an existing handle
            return ('prefix',) + self.readonly_fields
        else:
            # Creating a new handle
            return self.readonly_fields

admin.site.register(Handle, HandleAdmin)
