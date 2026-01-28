from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max, Count
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from chat.models import ChatRoom, Message
from chat.forms import MessageForm, PersonalChatForm
from projects.models import Project, ProjectAssignment
from accounts.models import User


def get_display_name(room, user):
    """Helper function to get display name for chat room"""
    return room.get_display_name(user)


@login_required
def chat_list(request):
    """List all chat rooms (project and personal) for the current user"""
    user = request.user

    # Get all chat rooms user is part of
    chat_rooms = (
        ChatRoom.objects.filter(participants=user)
        .annotate(
            last_message_time=Max("messages__created_at"),
            unread_count=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=user),
            ),
        )
        .order_by("-last_message_time", "-created_at")
    )

    # Separate project and personal chats
    project_chats = chat_rooms.filter(room_type="PROJECT")
    personal_chats = chat_rooms.filter(room_type="PERSONAL")

    # Add display names to personal chats
    for room in personal_chats:
        room.display_name = room.get_display_name(user)

    # Get available projects for creating new project chats
    if user.is_ceo:
        available_projects = Project.objects.filter(organization=user.organization)
    elif user.is_pm:
        available_projects = Project.objects.filter(
            organization=user.organization, project_manager=user
        )
    elif user.is_dev or user.is_uiux:
        available_projects = Project.objects.filter(
            organization=user.organization,
            assignments__user=user,
            assignments__is_active=True,
        ).distinct()
    else:
        available_projects = Project.objects.none()

    # Filter out projects that already have chat rooms
    projects_with_chat = ChatRoom.objects.filter(
        room_type="PROJECT", project__in=available_projects
    ).values_list("project_id", flat=True)

    available_projects = available_projects.exclude(id__in=projects_with_chat)

    context = {
        "project_chats": project_chats,
        "personal_chats": personal_chats,
        "available_projects": available_projects,
        "user": user,
    }

    return render(request, "chat/list.html", context)


@login_required
def chat_room(request, room_id):
    """View a specific chat room"""
    user = request.user
    room = get_object_or_404(ChatRoom, id=room_id)

    # Check if user is a participant
    if not room.participants.filter(id=user.id).exists():
        messages.error(request, "You do not have access to this chat room.")
        return redirect("chat:list")

    # Get messages with pagination
    messages_list = (
        Message.objects.filter(room=room)
        .select_related("sender")
        .order_by("created_at")
    )
    paginator = Paginator(messages_list, 50)  # 50 messages per page
    page_number = request.GET.get("page", paginator.num_pages)  # Default to last page
    page_obj = paginator.get_page(page_number)

    # Get last message ID for JavaScript
    last_message_id = 0
    if messages_list.exists():
        last_message = messages_list.last()
        last_message_id = last_message.id

    # Mark messages as read (except own messages)
    Message.objects.filter(room=room, is_read=False).exclude(sender=user).update(
        is_read=True, read_at=timezone.now()
    )

    # Form for sending new messages
    form = MessageForm()

    # Get display name
    display_name = room.get_display_name(user)

    context = {
        "room": room,
        "messages": page_obj,
        "form": form,
        "user": user,
        "display_name": display_name,
        "last_message_id": last_message_id,
    }
    # Provide available users for admin to add to the room
    # Exclude current participants and inactive users
    available_users = User.objects.filter(is_active=True)
    if user.organization:
        available_users = available_users.filter(organization=user.organization)
    available_users = available_users.exclude(
        id__in=room.participants.values_list("id", flat=True)
    ).order_by("first_name", "last_name", "username")
    context["available_users"] = available_users

    return render(request, "chat/room.html", context)


@login_required
@require_http_methods(["POST"])
def add_user_to_room(request, room_id):
    """Admin-only: add a user to the chat room participants."""
    actor = request.user
    room = get_object_or_404(ChatRoom, id=room_id)

    # Only allow superusers or CEO to add users (adjust as needed)
    if not (actor.is_superuser or getattr(actor, "is_ceo", False)):
        return JsonResponse({"error": "Permission denied."}, status=403)

    user_id = request.POST.get("user_id") or request.POST.get("user")
    if not user_id:
        return JsonResponse({"error": "Missing user_id."}, status=400)

    try:
        user_to_add = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    if room.participants.filter(id=user_to_add.id).exists():
        return JsonResponse({"error": "User already in room."}, status=400)

    room.participants.add(user_to_add)
    return JsonResponse(
        {
            "success": True,
            "user": {
                "id": user_to_add.id,
                "name": user_to_add.get_full_name() or user_to_add.username,
            },
        }
    )


@login_required
def create_project_chat(request, project_id):
    """Create a chat room for a project"""
    user = request.user
    project = get_object_or_404(Project, id=project_id)

    # Check if user has access to this project
    has_access = False
    if user.is_ceo:
        has_access = True
    elif user.is_pm and project.project_manager == user:
        has_access = True
    elif (user.is_dev or user.is_uiux) and ProjectAssignment.objects.filter(
        project=project, user=user, is_active=True
    ).exists():
        has_access = True

    if not has_access:
        messages.error(
            request, "You do not have access to create a chat for this project."
        )
        return redirect("chat:list")

    # Check if chat room already exists
    chat_room, created = ChatRoom.objects.get_or_create(
        room_type="PROJECT",
        project=project,
        defaults={"name": f"{project.name} Chat", "created_by": user},
    )

    # Add all project participants to the chat room
    # Get project manager
    if project.project_manager:
        chat_room.participants.add(project.project_manager)

    # Get assigned team members
    assigned_users = ProjectAssignment.objects.filter(
        project=project, is_active=True
    ).values_list("user", flat=True)
    chat_room.participants.add(*assigned_users)

    # Add creator if not already added
    chat_room.participants.add(user)

    if created:
        messages.success(request, f'Chat room created for project "{project.name}"!')
    else:
        messages.info(
            request, f'Chat room already exists for project "{project.name}"!'
        )

    return redirect("chat:room", room_id=chat_room.id)


@login_required
def create_personal_chat(request):
    """Create or get a personal chat room with another user"""
    user = request.user

    if request.method == "POST":
        form = PersonalChatForm(request.POST, user=user)
        if form.is_valid():
            other_user = form.cleaned_data["user"]

            # Check if a personal chat already exists between these two users
            existing_room = (
                ChatRoom.objects.filter(room_type="PERSONAL", participants=user)
                .filter(participants=other_user)
                .distinct()
            )

            # Filter to get room with exactly these two participants
            for room in existing_room:
                if room.participants.count() == 2:
                    return redirect("chat:room", room_id=room.id)

            # Create new personal chat room
            chat_room = ChatRoom.objects.create(room_type="PERSONAL", created_by=user)
            chat_room.participants.add(user, other_user)

            messages.success(
                request,
                f"Started chat with {other_user.get_full_name() or other_user.username}!",
            )
            return redirect("chat:room", room_id=chat_room.id)
    else:
        form = PersonalChatForm(user=user)

    context = {"form": form, "user": user}

    return render(request, "chat/create_personal.html", context)


@login_required
@require_http_methods(["POST"])
def send_message(request, room_id):
    """Send a message via AJAX"""
    user = request.user
    room = get_object_or_404(ChatRoom, id=room_id)

    # Check if user is a participant
    if not room.participants.filter(id=user.id).exists():
        return JsonResponse(
            {"error": "You do not have access to this chat room."}, status=403
        )

    form = MessageForm(request.POST)
    if form.is_valid():
        message = form.save(commit=False)
        message.room = room
        message.sender = user
        message.save()

        # Update room's last message time
        room.update_last_message_time()

        # Return message data
        return JsonResponse(
            {
                "success": True,
                "message": {
                    "id": message.id,
                    "content": message.content,
                    "sender": user.get_full_name() or user.username,
                    "sender_id": user.id,
                    "created_at": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "formatted_time": message.created_at.strftime("%I:%M %p"),
                },
            }
        )

    return JsonResponse({"error": "Invalid message."}, status=400)


@login_required
def get_messages(request, room_id):
    """Get messages for a chat room via AJAX"""
    user = request.user
    room = get_object_or_404(ChatRoom, id=room_id)

    # Check if user is a participant
    if not room.participants.filter(id=user.id).exists():
        return JsonResponse(
            {"error": "You do not have access to this chat room."}, status=403
        )

    # Get last message ID if provided (for pagination)
    last_message_id = request.GET.get("last_message_id")

    if last_message_id:
        messages_list = (
            Message.objects.filter(room=room, id__gt=last_message_id)
            .select_related("sender")
            .order_by("created_at")
        )
    else:
        # Get last 50 messages
        messages_list = (
            Message.objects.filter(room=room)
            .select_related("sender")
            .order_by("-created_at")[:50]
        )
        messages_list = reversed(list(messages_list))

    messages_data = []
    for msg in messages_list:
        messages_data.append(
            {
                "id": msg.id,
                "content": msg.content,
                "sender": msg.sender.get_full_name() or msg.sender.username,
                "sender_id": msg.sender.id,
                "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "formatted_time": msg.created_at.strftime("%I:%M %p"),
                "is_own": msg.sender.id == user.id,
            }
        )

    # Mark messages as read (except own messages)
    Message.objects.filter(room=room, is_read=False).exclude(sender=user).update(
        is_read=True, read_at=timezone.now()
    )

    return JsonResponse({"messages": messages_data, "room_id": room.id})
