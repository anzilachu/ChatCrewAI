from django.contrib import admin
from .models import ChatHistory, RoleplayChatHistory, Profile, FanChatHistory
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class RoleplayChatHistoryInline(admin.TabularInline):
    model = RoleplayChatHistory
    extra = 0
    fields = ('character_name', 'opponent_name', 'message', 'character_image_url', 'opponent_image_url', 'timestamp')
    readonly_fields = ('timestamp',)

class ChatHistoryInline(admin.TabularInline):
    model = ChatHistory
    extra = 0
    fields = ('show_name', 'character_name', 'message', 'timestamp')
    readonly_fields = ('show_name', 'character_name', 'message', 'timestamp')

class FanChatHistoryInline(admin.TabularInline):
    model = FanChatHistory
    extra = 0
    fields = ('show_name', 'message', 'is_user_message', 'timestamp')
    readonly_fields = ('show_name', 'message', 'is_user_message', 'timestamp')

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            try:
                obj.profile
            except Profile.DoesNotExist:
                Profile.objects.create(user=obj)
        return form

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(FanChatHistory)
