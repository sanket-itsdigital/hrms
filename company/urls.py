from django.urls import path
from company.views import (
    company_index,
    # Announcements
    announcements_list, announcement_detail, announcement_create,
    announcement_update, announcement_delete,
    # Policies
    policies_list, policy_create, policy_update, policy_delete,
    # Holidays
    holidays_list, holiday_create, holiday_update, holiday_delete,
    recurring_holiday_create, recurring_holiday_delete,
    # Events
    events_list, event_detail, event_create, event_update, event_delete,
    event_join, event_leave,
    # Birthdays & Anniversaries
    birthdays_anniversaries, birthday_anniversary_edit,
)

app_name = 'company'

urlpatterns = [
    path('', company_index, name='index'),
    
    # Announcements
    path('announcements/', announcements_list, name='announcements_list'),
    path('announcements/<int:id>/', announcement_detail, name='announcement_detail'),
    path('announcements/create/', announcement_create, name='announcement_create'),
    path('announcements/<int:id>/edit/', announcement_update, name='announcement_update'),
    path('announcements/<int:id>/delete/', announcement_delete, name='announcement_delete'),
    
    # Policies
    path('policies/', policies_list, name='policies_list'),
    path('policies/create/', policy_create, name='policy_create'),
    path('policies/<int:id>/edit/', policy_update, name='policy_update'),
    path('policies/<int:id>/delete/', policy_delete, name='policy_delete'),
    
    # Holidays
    path('holidays/', holidays_list, name='holidays_list'),
    path('holidays/create/', holiday_create, name='holiday_create'),
    path('holidays/recurring/add/', recurring_holiday_create, name='recurring_holiday_create'),
    path('holidays/recurring/<int:id>/delete/', recurring_holiday_delete, name='recurring_holiday_delete'),
    path('holidays/<int:id>/edit/', holiday_update, name='holiday_update'),
    path('holidays/<int:id>/delete/', holiday_delete, name='holiday_delete'),
    
    # Events
    path('events/', events_list, name='events_list'),
    path('events/<int:id>/', event_detail, name='event_detail'),
    path('events/create/', event_create, name='event_create'),
    path('events/<int:id>/edit/', event_update, name='event_update'),
    path('events/<int:id>/delete/', event_delete, name='event_delete'),
    path('events/<int:id>/join/', event_join, name='event_join'),
    path('events/<int:id>/leave/', event_leave, name='event_leave'),
    
    # Birthdays & Anniversaries
    path('birthdays-anniversaries/', birthdays_anniversaries, name='birthdays_anniversaries'),
    path('birthdays-anniversaries/<int:user_id>/edit/', birthday_anniversary_edit, name='birthday_anniversary_edit'),
]
