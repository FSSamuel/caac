from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import User
from embed_video.fields import EmbedVideoField
from django.core.validators import validate_email
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.conf import settings
import uuid






# Create your models here.

class Ministry(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    image = models.ImageField(upload_to='ministries/')
    description = RichTextField()  # Only keep one description field
    button_text = models.CharField(max_length=50, default="Learn More")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Ministries"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='events/')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    date = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, help_text='Font Awesome class (e.g., fas fa-music)')
    description = RichTextField()
    button_text = models.CharField(max_length=50, default="Register")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Events"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Leadership(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='leadership/')
    slug = models.SlugField(max_length=100, default='event-default')
    description = RichTextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Leadership"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class MinistryCardCategory(models.Model):
    """Categories for the ministry display cards"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Ministry Card Category In Ministries page"
        verbose_name_plural = "Ministry Card Categories In Ministries Page"
        ordering = ['order']

    def __str__(self):
        return self.name

class MinistryCard(models.Model):
    """Individual ministry program cards with images"""
    category = models.ForeignKey(MinistryCardCategory, on_delete=models.CASCADE, related_name='cards')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='ministry_cards/')
    age_group = models.CharField(max_length=100, blank=True)
    meeting_time = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    button_text = models.CharField(max_length=50, default="Learn More")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Ministry Card In Ministry page"
        ordering = ['order']
        
    def __str__(self):
        return f"{self.category.name}: {self.title}"





class Category(models.Model):
    name = models.CharField(_('Category Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    icon = models.CharField(_('Icon'), max_length=50, default='fas fa-comment')
    order = models.PositiveIntegerField(_('Display Order'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated At'), default=timezone.now)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    content = models.TextField(_('Content'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE,
        verbose_name=_('Author'),
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_DEFAULT,
        default=1,  
        verbose_name=_('Category')
    )
    is_pinned = models.BooleanField(_('Pinned'), default=False)
    created_at = models.DateTimeField(_('Created At'), default=timezone.now)
    updated_at = models.DateTimeField(_('Updated At'), default=timezone.now)
    view_count = models.PositiveIntegerField(_('Views'), default=0)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ['-is_pinned', '-created_at']

    def save(self, *args, **kwargs):
        if not self.category_id:
            default_category = Category.objects.filter(is_active=True).first()
            if default_category:
                self.category = default_category
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def get_short_content(self):
        return self.content[:150] + "..." if len(self.content) > 150 else self.content
    

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name=_('Post')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Author')
    )
    content = models.TextField(_('Content'))
    created_at = models.DateTimeField(_('Created At'), default=timezone.now)

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['created_at']

    def __str__(self):
        return _("Comment by %(username)s") % {'username': self.author.username}

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('User')
    )
    avatar = models.ImageField(
        _('Profile Picture'),
        upload_to='avatars/',
        null=True,
        blank=True
    )
    bio = models.TextField(_('Biography'), blank=True)
    location = models.CharField(_('Location'), max_length=100, blank=True)
    website = models.URLField(_('Website'), blank=True)
    join_date = models.DateTimeField(_('Join Date'), default=timezone.now)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return _("%(username)s's Profile") % {'username': self.user.username}

class BibleStudy(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    summary = models.TextField(_('Summary'))
    content = models.TextField(_('Content'))
    created_at = models.DateTimeField(_('Created At'), default=timezone.now)

    class Meta:
        verbose_name = _('Bible Study')
        verbose_name_plural = _('Bible Studies')
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    


class DiscussionCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-folder')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)  # Added for consistency
    
    class Meta:
        verbose_name = _('Discussion Category')
        verbose_name_plural = _('Discussion Categories')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Discussion(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    category = models.ForeignKey(
        'DiscussionCategory', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('Discussion Category')
    )
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('discussion_detail', kwargs={'pk': self.pk})
    
    def get_short_content(self):
        return self.content[:150] + '...' if len(self.content) > 150 else self.content





class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        ordering = ['created_at']

class Like(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('discussion', 'user')





# signals.py (if you have one)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()  





class Notification(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=50)  # e.g., 'like', 'comment', 'mention'

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def __str__(self):
        return f"{self.user.username} - {self.message}"

    def mark_as_read(self):
        self.is_read = True
        self.save()





class DonationFund(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name

class Donation(models.Model):
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fund = models.ForeignKey(DonationFund, on_delete=models.PROTECT)
    payment_method = models.CharField(max_length=20, choices=[
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('bank', 'Bank Transfer'),
    ])
    transaction_id = models.CharField(max_length=100, blank=True)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    billing_email = models.EmailField()
    billing_name = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"${self.amount} to {self.fund}"
    




class Sermon(models.Model):
    title = models.CharField(max_length=200)
    preacher = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    description = models.TextField()
    video = models.FileField(upload_to='sermons/video/', blank=True, null=True)
    audio = models.FileField(upload_to='sermons/audio', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='sermons/thumbnails/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} by {self.preacher}"

    class Meta:
        ordering = ['-date']








class Subscriber(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return self.email

    


class EmailTemplate(models.Model):
    subject = models.CharField(max_length=255)
    message = RichTextField()
    recipients = models.ManyToManyField(Subscriber)
    
    def __str__(self):
        return self.subject
    





@receiver(post_save, sender=User)  # Trigger when user signs up
def send_welcome_email(sender, instance, created, **kwargs):
    if created:  # Only for new users
        send_mail(
            'Welcome to Our Church!',
            'Thank you for joining Grace Community Church!',
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )


