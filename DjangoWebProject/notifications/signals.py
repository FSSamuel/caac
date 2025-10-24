from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from comments.models import Comment
from likes.models import Like

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.content_object.author != instance.author:
        Notification.objects.create(
            user=instance.content_object.author,
            message=f"{instance.author.username} commented on your post",
            notification_type='comment',
            link=instance.get_absolute_url()
        )

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created and instance.content_object.author != instance.user:
        Notification.objects.create(
            user=instance.content_object.author,
            message=f"{instance.user.username} liked your {instance.content_type.model}",
            notification_type='like',
            link=instance.content_object.get_absolute_url()
        )