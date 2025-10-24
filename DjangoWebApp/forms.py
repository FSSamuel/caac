from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post,Comment,Discussion
from .models import DonationFund
from .models import Subscriber
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import EmailTemplate
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.conf import settings






class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
    


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a title for your post'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Share your thoughts...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment...'
            }),
        }





class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content', 'category', 'is_pinned']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your comment...'}),
        }





class DonationForm(forms.Form):
    AMOUNT_CHOICES = [
        (50, 'AUD50'),
        (100, 'AUD100'),
        (250, 'AUD250'),
        (500, 'AUD500'),
        ('other', 'Other Amount'),
    ]
    
    amount = forms.ChoiceField(choices=AMOUNT_CHOICES, widget=forms.RadioSelect)
    custom_amount = forms.DecimalField(
        required=False,
        min_value=5,
        max_value=10000,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter amount'})
    )
    fund = forms.ModelChoiceField(
        queryset=DonationFund.objects.filter(is_active=True),
        empty_label=None,
        widget=forms.RadioSelect
    )
    payment_method = forms.ChoiceField(
        choices=[('card', 'Credit/Debit Card'), ('paypal', 'PayPal')],
        widget=forms.RadioSelect
    )
    is_recurring = forms.BooleanField(required=False, initial=False)
    billing_name = forms.CharField(max_length=100)
    billing_email = forms.EmailField()
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}))






class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']






class EmailTemplateAdminForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = '__all__'
        widgets = {
            'message': CKEditorWidget(),
        }









