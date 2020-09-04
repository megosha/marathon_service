from django.contrib import admin

from front import models
# Register your models here.

class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'registry_sent', 'registry_date','description']
    list_display_links = ['user']
    list_filter = ['registry_date']
    search_fields = ['user', 'phone', 'description']
    readonly_fields = ['registry_date']



admin.site.register(models.Account, AccountAdmin)