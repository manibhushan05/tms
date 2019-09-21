from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.models import User
from . import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
    model = models.Profile
    can_delete = False
    verbose_name_plural = 'profile'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    ordering = ['-id']
    list_display = ['id', 'username', 'get_name', 'get_phone', 'get_email', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['id', 'username', 'profile__name', 'profile__phone', 'profile__email']

    def get_name(self, instance):
        return instance.profile.name

    get_name.short_description = 'Name'

    def get_phone(self, instance):
        return instance.profile.phone

    get_phone.short_description = 'Phone'

    def get_email(self, instance):
        return instance.profile.email

    get_email.short_description = 'Email'


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'contact_person_name', 'phone', 'email', 'organization']
    ordering = ['name']
    search_fields = ['id', 'user__username', 'name', 'contact_person_name', 'alternate_phone', 'alternate_email',
                     'phone', 'email', 'organization']
    autocomplete_fields = ['city']


# Re-register UserAdmin
admin.site.register(models.Profile, ProfileAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(models.ServerErrorMessage)
