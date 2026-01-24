from django.contrib import admin
from chat.models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'room_type', 'name', 'project', 'created_by', 'created_at', 'last_message_at']
    list_filter = ['room_type', 'created_at']
    search_fields = ['name', 'project__name']
    filter_horizontal = ['participants']
    readonly_fields = ['created_at', 'updated_at', 'last_message_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'sender', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at', 'room__room_type']
    search_fields = ['content', 'sender__username', 'sender__email']
    readonly_fields = ['created_at', 'updated_at', 'read_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
