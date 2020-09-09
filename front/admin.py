from django.contrib import admin

from front import models


# Register your models here.
class UpperSettingAdmin(admin.ModelAdmin):
    list_display = ['endpoint']
    list_display_links = ['endpoint']


class SettingAdmin(admin.ModelAdmin):
    list_display = ['website', 'contact_phone', 'contact_mail']
    list_display_links = ['website']


class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'approved', 'registry_sent', 'date_registry', 'description']
    list_display_links = ['user']
    list_filter = ['date_registry']
    search_fields = ['user', 'phone', 'description']
    readonly_fields = ['date_registry']

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['account', 'custom_user', 'date_create']
    list_display_links = ['account', 'custom_user']
    list_filter = ['date_create', 'account', 'custom_user']
    search_fields = ['account', 'custom_user']
    readonly_fields = ['date_create']

class MarathonAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_start']
    list_display_links = ['title']
    list_filter = ['date_start', 'date_create']
    search_fields = ['title']

class LessonAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'marathon', 'cost', 'date_publish']
    list_display_links = ['number', 'title']
    list_filter = ['marathon', 'date_publish']
    search_fields = ['title', 'marathon']

class VideoAdmin(admin.ModelAdmin):
    list_display = ['number', 'lesson', 'date_publish', 'date_create']
    list_display_links = ['number', 'lesson']
    list_filter = ['lesson', 'date_publish', 'date_create']
    search_fields = ['title', 'lesson']
    readonly_fields = ['date_create']


admin.site.register(models.UpperSetting, UpperSettingAdmin)
admin.site.register(models.Setting, SettingAdmin)
admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Feedback, FeedbackAdmin)
admin.site.register(models.Marathon, MarathonAdmin)
admin.site.register(models.Lesson, LessonAdmin)
admin.site.register(models.Video, VideoAdmin)
