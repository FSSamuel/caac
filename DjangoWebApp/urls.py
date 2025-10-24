from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import custom_logout_view
from django.urls import path
from .views import (
    NotificationListView,          
    mark_all_notifications_as_read,  
    mark_notification_as_read,    
    get_unread_count,             
)
from django.urls import path
from .views import giving, giving_thank_you
from django.urls import path, include

from django.urls import path



urlpatterns = [
    path('', views.index, name='index'),
    
    path('about/', views.about, name='about'),
    path('sermons/', views.sermons, name='sermons'),
    path('ministries/', views.ministries, name='ministries'),
    path('event/', views.event, name='event'),
    path('bookings/', views.bookings, name='bookings'),
    path('contact/', views.contact, name='contact'),
    path('giving/', views.giving, name='giving'),
    path('forum/', views.forum, name='forum'),
    path('beliefs/', views.beliefs, name='beliefs'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('search/', views.forum_search, name='forum_search'),
    path('event_calendar/', views.event_calendar, name='event_calendar'),
    path('prayer-requests/', views.prayer_requests, name='prayer_requests'),
    path('bible-study/', views.bible_study_archive, name='bible_study_archive'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<int:category_id>/', views.category_posts, name='category_posts'),
    path('create/', views.create_post, name='create_post'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('search/', views.forum_search, name='forum_search'),
    path('members/', views.member_directory, name='member_directory'),
    path('discussion_list', views.discussion_list, name='discussion_list'),
    path('discussion/<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('discussion/new/', views.create_discussion, name='create_discussion'),
    path('discussion/<int:pk>/like/', views.like_discussion, name='like_discussion'),
    path('category/<int:category_id>/', views.category_discussions, name='category_discussions'),
    path('forum/', views.discussion_list, name='discussion_list'),
    path('new/', views.create_discussion, name='create_discussion'),
    path('<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('<int:pk>/like/', views.like_discussion, name='like_discussion'),
    path('category/<int:category_id>/', views.category_discussions, name='category_discussions'),
    path('discussion/<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('discussion/<int:pk>/like/', views.like_discussion, name='like_discussion'),
    path('discussion/<int:pk>/edit/', views.edit_discussion, name='edit_discussion'),
    path('add/', views.add_discussion, name='add_discussion'),
    path('prayer-requests/', views.prayer_requests, name='prayer_requests'),
    path('discussion/<int:pk>/delete/', views.delete_discussion, name='delete_discussion'),
    path('notifications/mark-all-as-read/', mark_all_notifications_as_read, name='mark_all_notifications_read'),
    path('notifications/', NotificationListView.as_view(), name='all_notifications'),
    path('notifications/mark-as-read/<int:pk>/', mark_notification_as_read, name='mark_notification_read'),
    path('notifications/unread-count/', get_unread_count, name='unread_notifications_count'),
    path('notifications/', NotificationListView.as_view(), name='all_notifications'),
    path('give/', giving, name='giving'),
    path('give/thank-you/', giving_thank_you, name='giving_thank_you'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscription_thankyou/', views.subscribe, name='subscription_thankyou'),
    #path('sermons/', views.sermons_page, name='sermons_page'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('congregations/', views.congregations, name='congregations'),
    path('next-steps/', views.next_steps, name='next_steps'),

   
    # Auth URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('register/', views.register, name='register'),

 
]





