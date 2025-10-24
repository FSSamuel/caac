from .models import Notification

def create_notification(user, message, notification_type, link=None):
    """Create a new notification for a user"""
    return Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        link=link
    )

def notify_user_about_comment(user, comment):
    """Example notification for new comments"""
    message = f"{comment.author.username} commented on your post"
    link = comment.get_absolute_url()  # Make sure your Comment model has this method
    create_notification(user, message, 'comment', link)

def notify_user_about_like(user, liked_object):
    """Example notification for new likes"""
    message = f"{liked_object.user.username} liked your {liked_object.__class__.__name__.lower()}"
    link = liked_object.get_absolute_url()
    create_notification(user, message, 'like', link)