from django.urls import path
from chat.views import (
    chat_list,
    chat_room,
    create_project_chat,
    create_personal_chat,
    send_message,
    get_messages,
)
from chat.views import add_user_to_room

app_name = "chat"

urlpatterns = [
    path("", chat_list, name="list"),
    path("room/<int:room_id>/", chat_room, name="room"),
    path(
        "project/<int:project_id>/create/",
        create_project_chat,
        name="create_project_chat",
    ),
    path("personal/create/", create_personal_chat, name="create_personal"),
    path("room/<int:room_id>/send/", send_message, name="send_message"),
    path("room/<int:room_id>/add_user/", add_user_to_room, name="add_user"),
    path("room/<int:room_id>/messages/", get_messages, name="get_messages"),
]
