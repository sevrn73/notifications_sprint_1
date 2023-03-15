import ast

from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from notification.forms import NotificationGroupForm, NotificationForm
from notification.models import (
    Notification,
    NotificationGroup,
    NotificationGroupUser,
    NotificationType,
    MessageTag,
    Template,
)


class NotificationTypeInline(admin.TabularInline):
    model = NotificationType.tags.through
    exclude = ('id',)
    extra = 0


@admin.register(MessageTag)
class MessageTagAdmin(admin.ModelAdmin):
    """Message tags admin."""


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    """ Notifications types admin."""
    list_display = ['title']
    inlines = [NotificationTypeInline]


@admin.register(Template)
class TemplateAdmin(SummernoteModelAdmin):
    """Template admin."""
    summernote_fields = ('code',)
    list_display = ['title', 'subject', 'notification_type']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin."""
    list_display = ['id', 'send_status', 'send_date']
    add_form = NotificationForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj:
            return self.add_form
        form = super().get_form(request, obj, change, **kwargs)
        return form


@admin.register(NotificationGroupUser)
class NotificationGroupUserAdmin(admin.ModelAdmin):
    """Group users Admin."""

    list_display = ['user', 'notification_group']


@admin.register(NotificationGroup)
class NotificationGroupAdmin(admin.ModelAdmin):
    """Group users for notifications admin."""

    add_form = NotificationGroupForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj:
            return self.add_form
        form = super().get_form(request, obj, change, **kwargs)
        return form

    def save_form(self, request, form, change):
        group = super(NotificationGroupAdmin, self).save_form(request, form, change)
        users_ids = ast.literal_eval(form.cleaned_data.get('users_ids_to_group'))
        group_users = [
            NotificationGroupUser(
                user=user_id,
                notification_group_id=group.pk,
            )
            for user_id in users_ids
        ]
        NotificationGroupUser.objects.bulk_create(group_users)
        return group
