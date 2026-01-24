from django.db import models
from django.utils import timezone
from accounts.models import User
from projects.models import Project


class ChatRoom(models.Model):
    """
    Model for chat rooms - can be project-based or personal (direct message)
    """
    ROOM_TYPE_CHOICES = [
        ('PROJECT', 'Project Chat'),
        ('PERSONAL', 'Personal Chat'),
    ]

    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    name = models.CharField(max_length=255, help_text="Room name (for project chats)")
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='chat_rooms',
        null=True,
        blank=True,
        help_text="Project this chat belongs to (for project chats)"
    )
    participants = models.ManyToManyField(
        User,
        related_name='chat_rooms',
        help_text="Users who can access this chat room"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_chat_rooms',
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'chat_rooms'
        verbose_name = 'Chat Room'
        verbose_name_plural = 'Chat Rooms'
        ordering = ['-last_message_at', '-created_at']
        unique_together = ['room_type', 'project']  # One chat room per project

    def __str__(self):
        if self.room_type == 'PROJECT' and self.project:
            return f"Project: {self.project.name}"
        elif self.room_type == 'PERSONAL':
            participants = self.participants.all()
            if participants.count() == 2:
                return f"Chat: {', '.join([p.get_full_name() or p.username for p in participants])}"
            return f"Personal Chat ({participants.count()} participants)"
        return self.name or f"Chat Room {self.id}"

    def get_display_name(self, user):
        """Get display name for the chat room from user's perspective"""
        if self.room_type == 'PROJECT' and self.project:
            return f"Project: {self.project.name}"
        elif self.room_type == 'PERSONAL':
            other_users = self.participants.exclude(id=user.id)
            if other_users.exists():
                other_user = other_users.first()
                return other_user.get_full_name() or other_user.username
            return "Personal Chat"
        return self.name

    def update_last_message_time(self):
        """Update last message timestamp"""
        self.last_message_at = timezone.now()
        self.save(update_fields=['last_message_at'])


class Message(models.Model):
    """
    Model for chat messages
    """
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.get_full_name() or self.sender.username}: {self.content[:50]}"

    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
