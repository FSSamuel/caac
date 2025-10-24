from .models import UserProfile
from . import models
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from django.core.cache import cache
from .forms import DiscussionForm
from .models import (
    Event, Ministry, Leadership, 
    Category, Post, Comment, 
    UserProfile, BibleStudy
)
from datetime import date
import logging

logger = logging.getLogger(__name__)
from django.http import JsonResponse
from .models import Discussion, Comment, Like, DiscussionCategory
from .forms import DiscussionForm, CommentForm
from django.db.models.functions import Greatest
from django.db.models import Max, Count
from django.db.models.functions import Greatest
from django.contrib.auth.models import User
from .models import UserProfile
from itertools import chain
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import Notification
from django.views.decorators.http import require_POST
from .models import Notification
from django.http import JsonResponse
from .models import Notification
from django.shortcuts import render
from .models import MinistryCardCategory
from .models import MinistryCardCategory
from django.conf import settings
from django.contrib import messages
from .forms import DonationForm
import stripe
from django.shortcuts import render
#from .models import Sermon, SermonSeries, Speaker
from django.core.paginator import Paginator
from .models import Sermon
from django.contrib import messages
from .models import Subscriber
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .forms import SubscriberForm
import uuid
import logging
from django.contrib import messages
from django.views.generic import ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import EmailMultiAlternatives


from django.urls import reverse_lazy





# Main Site Views
def index(request):
    ministries = Ministry.objects.all()
    events = Event.objects.all()
    return render(request, 'index.html', {
        'ministries': ministries,
        'events': events
    })



def admin(request):
    return render(request, 'admin.py')



def about(request):
    """About page view showing leadership"""
    leadership = Leadership.objects.all().order_by('order')
    return render(request, 'about.html', {'leadership': leadership})

def sermons(request):
    """Sermons page view"""
    sermons = Sermon.objects.all().order_by('-date')
    return render(request, 'sermons.html', {'sermons': sermons})




def ministries(request):
    """Ministries page view with all ministry cards"""
    categories = MinistryCardCategory.objects.all().prefetch_related(
        'cards'
    ).order_by('order')
    
    return render(request, 'ministries.html', {
        'categories': categories
    })

def event(request):
    """Events page view"""
    return render(request, 'event.html')


def contact(request):
    """Contact page view"""
    return render(request, 'contact.html')



def bookings(request):
    """Bookings page view"""
    return render(request, 'bookings.html')

def giving(request):
    """Giving page view"""
    return render(request, 'giving.html')

def beliefs(request):
    """Beliefs page view"""
    return render(request, 'beliefs.html')

def next_steps(request):
    return render(request, 'next_steps.html')

def ministry_cards_view(request):
    categories = MinistryCardCategory.objects.all().prefetch_related(
        'cards'
    ).order_by('order')
    
    return render(request, 'ministries/cards.html', {
        'categories': categories
    })

def congregations(request):
    return render(request, 'congregations.html')


# Authentication Views
def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('forum')
        messages.error(request, "Registration failed. Please correct the errors.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def custom_login(request):
    """Custom login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('forum')
        messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

@login_required
def custom_logout(request):
    """Custom logout view"""
    logout(request)
    return redirect('forum')



def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('forum')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

@login_required
def custom_logout_view(request):
    logout(request)
    return redirect('forum')




def forum(request):
    sort = request.GET.get('sort', 'recent')
    User = get_user_model()
    
    # Base queryset
    discussions = Discussion.objects.all()
    
    # Sorting logic
    if sort == 'newest':
        discussions = discussions.order_by('-created_at')
    elif sort == 'popular':
        discussions = discussions.annotate(
            like_count=Count('likes')
        ).order_by('-like_count', '-created_at')
    else:  # recent activity
        discussions = discussions.annotate(
            last_activity=Greatest('updated_at', Max('comments__created_at'))
        ).order_by('-is_pinned', '-last_activity', '-created_at')
    
    # Separate pinned and recent threads
    pinned_threads = discussions.filter(is_pinned=True).order_by('-created_at')
    recent_threads = discussions.filter(is_pinned=False)
    
    # Pagination
    paginator = Paginator(recent_threads, 10)
    page_number = request.GET.get('page')
    try:
        recent_threads = paginator.page(page_number)
    except PageNotAnInteger:
        recent_threads = paginator.page(1)
    except EmptyPage:
        recent_threads = paginator.page(paginator.num_pages)
    
    # Get active categories
    categories = DiscussionCategory.objects.filter(is_active=True)
    
    # Get active users and newest member
    active_users = User.objects.filter(
        last_login__gte=timezone.now() - timezone.timedelta(days=30)
    ).order_by('-last_login')[:12]
    
    newest_member = User.objects.order_by('-date_joined').first()
    
    context = {
        'pinned_threads': pinned_threads,
        'recent_threads': recent_threads,
        'categories': categories,
        'sort': sort,
        'total_threads': Discussion.objects.count(),
        'total_posts': Comment.objects.count() + Discussion.objects.count(),
        'total_members': User.objects.count(),
        'active_users': active_users,
        'newest_member': newest_member,
    }
    return render(request, 'forum.html', context)

  

def post_detail(request, post_id):
    """Post detail view with comments"""
    try:
        post_id = int(post_id)  # Ensure ID is numeric
        post = get_object_or_404(
            Post.objects.select_related('author', 'category'), 
            pk=post_id
        )
        post.view_count += 1
        post.save()
        
        comments = post.comment_set.select_related('author').order_by('created_at')
        
        if request.method == 'POST':
            if not request.user.is_authenticated:
                return redirect('login')
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect('post_detail', post_id=post.id)
        else:
            form = CommentForm()
        
        context = {
            'post': post,
            'comments': comments,
            'form': form,
        }
        return render(request, 'post_detail.html', context)
    except ValueError:
        raise Http404("Invalid post ID")

def category_posts(request, category_id):
    """View posts by category"""
    try:
        category_id = int(category_id)
        category = get_object_or_404(Category, pk=category_id)
        posts = Post.objects.filter(
            category=category
        ).select_related('author').order_by('-is_pinned', '-created_at')
        
        context = {
            'category': category,
            'posts': posts,
        }
        return render(request, 'category_posts.html', context)
    except ValueError:
        raise Http404("Invalid category ID")

@login_required
def create_post(request):
    """Create new post view"""
    initial = {}
    category_id = request.GET.get('category')
    
    if category_id:
        try:
            initial['category'] = int(category_id)
        except ValueError:
            messages.error(request, "Invalid category selection")
            return redirect('forum')
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(initial=initial)
    
    context = {
        'form': form,
    }
    return render(request, 'create_post.html', context)


# views.py
def user_profile(request, user_id):
    try:
        User = get_user_model()
        profile_user = get_object_or_404(User, pk=user_id)
        user_profile, created = UserProfile.objects.get_or_create(user=profile_user)
        
        # Get all activity and add type information
        posts = Post.objects.filter(author=profile_user).order_by('-created_at')
        discussions = Discussion.objects.filter(author=profile_user).order_by('-created_at')
        comments = Comment.objects.filter(author=profile_user).select_related('discussion').order_by('-created_at')

        # Prepare activity list with type indicators
        activity = []
        for post in posts:
            activity.append({'type': 'post', 'object': post})
        for discussion in discussions:
            activity.append({'type': 'discussion', 'object': discussion})
        for comment in comments:
            activity.append({'type': 'comment', 'object': comment})
        
        # Sort by creation date (newest first)
        activity.sort(key=lambda x: x['object'].created_at, reverse=True)
        activity = activity[:15]  # Limit to 15 most recent items

        context = {
            'profile_user': profile_user,
            'user_profile': user_profile,
            'activity': activity,
        }
        return render(request, 'user_profile.html', context)
        
    except ValueError:
        raise Http404("Invalid user ID")
   
    


def forum_search(request):
    """Forum search view"""
    query = request.GET.get('q', '').strip()
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).select_related('author', 'category')
    else:
        posts = []
    
    context = {
        'query': query,
        'posts': posts,
    }
    return render(request, 'search_results.html', context)

def prayer_requests(request):
    """Prayer requests view"""
    prayer_category, created = Category.objects.get_or_create(
        name="Prayer",
        defaults={
            'description': 'Prayer requests and intercessions',
            'icon': 'fas fa-praying-hands',
            'is_active': True
        }
    )
    
    prayer_posts = Post.objects.filter(
        category=prayer_category
    ).select_related('author').order_by('-created_at')
    
    context = {
        'prayer_posts': prayer_posts,
    }
    return render(request, 'prayer_requests.html', context)

# Bible Study Views
def bible_study_archive(request):
    """Bible study archive view"""
    studies = BibleStudy.objects.order_by('-created_at')
    return render(request, 'bible_study_archive.html', {'studies': studies})

def bible_study_detail(request, study_id):
    """Bible study detail view"""
    try:
        study_id = int(study_id)
        study = get_object_or_404(BibleStudy, pk=study_id)
        return render(request, 'bible_study_detail.html', {'study': study})
    except ValueError:
        raise Http404("Invalid study ID")

# Event Calendar View
def event_calendar(request):
    """Event calendar view"""
    try:
        today = date.today()
        upcoming_events = Event.objects.filter(date__gte=today).order_by('date')
        past_events = Event.objects.filter(date__lt=today).order_by('-date')
        
        context = {
            'today': today,
            'upcoming_events': upcoming_events,
            'past_events': past_events,
        }
        return render(request, 'event_calendar.html', context)
    except Exception as e:
        logger.error(f"Event calendar error: {str(e)}")
        raise Http404("Error loading event calendar")
    


def member_directory(request):
    User = get_user_model()
    members = User.objects.all().order_by('-date_joined')
    return render(request, 'member_directory.html', {'members': members})




def discussion_list(request):
    sort = request.GET.get('sort', 'recent')
    
    if sort == 'newest':
        discussions = Discussion.objects.all().order_by('-created_at')
    elif sort == 'popular':
        discussions = Discussion.objects.annotate(
            like_count=models.Count('likes')
        ).order_by('-like_count', '-created_at')
    else:  # recent activity
        discussions = Discussion.objects.annotate(
            last_activity=models.Max('comments__created_at')
        ).order_by('-is_pinned', '-last_activity', '-created_at')
    
    pinned_threads = Discussion.objects.filter(is_pinned=True).order_by('-created_at')
    recent_threads = discussions.filter(is_pinned=False)
    
    context = {
        'pinned_threads': pinned_threads,
        'recent_threads': recent_threads,
        'categories': Category.objects.filter(is_active=True),
    }
    return render(request, 'discussion_list.html', context)

def discussion_detail(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    comments = discussion.comments.all()
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.discussion = discussion
            comment.author = request.user
            comment.save()
            return redirect('discussion_detail', pk=discussion.pk)
    else:
        form = CommentForm()
    
    context = {
        'discussion': discussion,
        'comments': comments,
        'form': form,
    }
    return render(request, 'discussion_detail.html', context)

@login_required
def create_discussion(request):
    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.author = request.user
            discussion.save()
            messages.success(request, "Discussion created successfully!")
            return redirect('discussion_list')  # Redirect to forum home
    else:
        form = DiscussionForm()
    
    return render(request, 'create_discussion.html', {'form': form})


@login_required
def like_discussion(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    like, created = Like.objects.get_or_create(
        discussion=discussion,
        user=request.user
    )
    
    if not created:
        like.delete()
    
    return JsonResponse({
        'status': 'success',
        'action': 'liked' if created else 'unliked',
        'likes_count': discussion.likes.count()
    })




def create_discussion(request):
    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.author = request.user
            discussion.save()
            return redirect('discussion_detail', pk=discussion.pk)
    else:
        form = DiscussionForm()
    
    return render(request, 'create_discussion.html', {'form': form})



def category_discussions(request, category_id):
    """View discussions by category"""
    category = get_object_or_404(Category, pk=category_id)
    discussions = Discussion.objects.filter(
        category=category
    ).order_by('-is_pinned', '-created_at')
    
    context = {
        'category': category,
        'discussions': discussions,
    }
    return render(request, 'category_discussions.html', context)




@login_required
def edit_discussion(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk, author=request.user)
    if request.method == 'POST':
        form = DiscussionForm(request.POST, instance=discussion)
        if form.is_valid():
            form.save()
            return redirect('discussion_detail', pk=pk)
    else:
        form = DiscussionForm(instance=discussion)
    
    return render(request, 'edit_discussion.html', {
        'form': form,
        'discussion': discussion
    })




@login_required
def delete_discussion(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)
    if request.user == discussion.author or request.user.is_staff:
        discussion.delete()
        messages.success(request, "Discussion deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this discussion.")
    return redirect('forum')



@login_required
def add_discussion(request):
    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.author = request.user
            discussion.save()
            return redirect('forum')
    else:
        form = DiscussionForm()
    return render(request, 'add_discussion.html', {'form': form})







@login_required
def update_profile(request):
    if request.method == 'POST':
        profile = request.user.profile
        
        # Handle file upload
        if 'avatar' in request.FILES:
            # Delete old file if exists
            if profile.avatar:
                profile.avatar.delete()
            profile.avatar = request.FILES['avatar']
        
        # Update other fields
        profile.bio = request.POST.get('bio', profile.bio)
        profile.location = request.POST.get('location', profile.location)
        profile.website = request.POST.get('website', profile.website)
        profile.save()
        
        return redirect('user_profile', user_id=request.user.id)
    return redirect('home')








class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications_list.html'  
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

@require_POST
def mark_notification_as_read(request, pk):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)

def get_unread_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).count()
        return JsonResponse({'unread_count': count})
    return JsonResponse({'unread_count': 0})

def mark_all_notifications_as_read(request):
    if request.user.is_authenticated:
        Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).update(is_read=True)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        messages.success(request, "All notifications marked as read!")
    return redirect('all_notifications')





def giving(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            try:
                # Process payment with Stripe
                stripe.api_key = settings.STRIPE_SECRET_KEY
                
                # Create Stripe customer
                customer = stripe.Customer.create(
                    email=form.cleaned_data['billing_email'],
                    name=form.cleaned_data['billing_name'],
                )
                
                # Create payment intent
                amount = int(float(form.cleaned_data.get('custom_amount') or form.cleaned_data['amount']) * 100)
                payment_intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency='usd',
                    customer=customer.id,
                    description=f"Donation to {form.cleaned_data['fund']}",
                    metadata={
                        'fund': str(form.cleaned_data['fund'].id),
                        'recurring': str(form.cleaned_data['is_recurring'])
                    }
                )
                
                # Save to database (after successful payment you'd complete this)
                # donation = Donation.objects.create(...)
                
                return render(request, 'processing.html', {
                    'client_secret': payment_intent.client_secret,
                    'stripe_key': settings.STRIPE_PUBLIC_KEY,
                })
                
            except stripe.error.StripeError as e:
                messages.error(request, f"Payment error: {e.user_message}")
    else:
        form = DonationForm()
    
    return render(request, 'giving.html', {
        'form': form,
        'stripe_key': settings.STRIPE_PUBLIC_KEY,
    })



def giving_thank_you(request):
    # Retrieve donation details from session
    donation_details = request.session.pop('donation_details', None)
    
    if not donation_details:
        return redirect('giving')  # Redirect if no donation details
    
    return render(request, 'thank_you.html', {
        'amount': donation_details['amount'],
        'fund': donation_details['fund'],
        'email': donation_details['email']
    })





# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_payment_intent(request):
    if request.method == 'POST':
        try:
            amount = int(float(request.POST.get('amount')) * 100)  # Convert to cents
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='aud',
                metadata={
                    'fund_id': request.POST.get('fund_id'),
                    'is_recurring': request.POST.get('is_recurring', 'false')
                }
            )
            return JsonResponse({'client_secret': intent.client_secret})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def confirm_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_intent = stripe.PaymentIntent.retrieve(data['payment_intent_id'])
            
            # Save donation to database
            donation = Donation.objects.create(
                amount=data['amount'],
                fund_id=data['fund_id'],
                payment_method='card',
                is_recurring=data['is_recurring'],
                transaction_id=payment_intent.id,
                status='completed',
                donor=request.user if request.user.is_authenticated else None
            )
            
            # Send receipt email
            send_receipt_email(donation)
            
            return JsonResponse({
                'success': True,
                'message': 'Donation processed successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def process_paypal_donation(request):
    if request.method == 'POST':
        try:
            # Verify PayPal payment
            # Save donation to database
            # Send receipt
            
            return JsonResponse({
                'success': True,
                'message': 'PayPal donation processed successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def process_direct_debit(request):
    if request.method == 'POST':
        try:
            # Process direct debit (using Stripe or your bank's API)
            # Save to database with 'pending' status
            # Send confirmation
            
            return JsonResponse({
                'success': True,
                'message': 'Direct debit setup successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)




def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscriber = form.save()
            
            # Generate proper unsubscribe URL
            unsubscribe_url = request.build_absolute_uri(
                reverse('unsubscribe', kwargs={'subscriber_id': subscriber.id})
            )
            
            context = {
                'email': subscriber.email,
                'subscriber': subscriber,
                'unsubscribe_url': unsubscribe_url
            }
            
            # Send email with HTML content
            send_mail(
                'Thank You for Subscribing',
                'Plain text version of your email',
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                html_message=render_to_string('subscription_thankyou.html', context),
                fail_silently=False
            )
            
            return render(request, 'subscription_thankyou.html', context)
    
    form = SubscriberForm()
    return render(request, 'subscription_thankyou.html', {'form': form})



def unsubscribe(request):
    email = request.GET.get('email')
    if email:
        try:
            subscriber = Subscriber.objects.get(email=email)
            subscriber.is_active = False
            subscriber.save()
            return render(request, 'unsubscribe_success.html')
        except Subscriber.DoesNotExist:
            pass
    return render(request, 'unsubscribe_success.html')

















