from front import models
from django.contrib import admin


@admin.register(models.Logging)
class LoggingAdmin(admin.ModelAdmin):
    list_display = ['date', 'action', 'result']


@admin.register(models.Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ['date', 'recipient', 'subject']


# Register your models here.
class UpperSettingAdmin(admin.ModelAdmin):
    list_display = ['endpoint']
    list_display_links = ['endpoint']


class SettingAdmin(admin.ModelAdmin):
    list_display = ['website', 'contact_phone', 'contact_mail', 'fake_cost']
    list_display_links = ['website']


class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'approved', 'registry_sent', 'date_registry', 'description']
    list_display_links = ['user']
    list_filter = ['date_registry', 'approved', 'registry_sent']
    search_fields = ['user__last_name', 'user__first_name', 'phone', 'description']
    readonly_fields = ['date_registry']

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['account', 'kind', 'custom_user', 'date_create']
    list_display_links = ['account', 'kind', 'custom_user']
    list_filter = ['kind', 'date_create', 'account', 'custom_user']
    search_fields = ['account__user__last_name', 'account__user__first_name', 'custom_user']
    readonly_fields = ['date_create']

class ReviewKindAdmin(admin.ModelAdmin):
    list_display = ['pk', 'kind']
    list_display_links = ['pk', 'kind']
    search_fields = ['kind']

class MarathonAdmin(admin.ModelAdmin):
    list_display = ['title', 'cost', 'date_start']
    list_display_links = ['title']
    list_filter = ['date_start', 'date_create']
    search_fields = ['title']

class LessonAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'marathon', 'date_publish']
    list_display_links = ['number', 'title']
    list_filter = ['marathon', 'date_publish']
    search_fields = ['title', 'marathon__title']

class VideoAdmin(admin.ModelAdmin):
    list_display = ['number', 'lesson', 'date_create']
    list_display_links = ['number', 'lesson']
    list_filter = ['lesson', 'date_create']
    search_fields = ['title', 'lesson__title']
    readonly_fields = ['date_create']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['date_pay', 'uuid', 'status', 'account', 'marathon', 'status_mail_invoice']
    list_display_links = ['date_pay', 'uuid']
    list_filter = ['date_pay', 'status', 'marathon', 'status_mail_invoice',]
    search_fields = ['account__user__last_name', 'account__phone', 'account__user__email', 'marathon__title', 'status']
    readonly_fields = ['date_pay', 'icon_tag']

admin.site.register(models.UpperSetting, UpperSettingAdmin)
admin.site.register(models.Setting, SettingAdmin)
admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Feedback, FeedbackAdmin)
admin.site.register(models.ReviewKind, ReviewKindAdmin)
admin.site.register(models.Marathon, MarathonAdmin)
admin.site.register(models.Lesson, LessonAdmin)
admin.site.register(models.Video, VideoAdmin)
admin.site.register(models.Payment, PaymentAdmin)
