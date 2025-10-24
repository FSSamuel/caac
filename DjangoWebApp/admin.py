from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Ministry, Event, Leadership
from django.utils.html import format_html
from django.contrib import admin
from .models import MinistryCardCategory, MinistryCard
from django.db import models
from django import forms
from .models import Sermon
from django.contrib import admin
from .models import Subscriber, EmailTemplate
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from ckeditor.fields import RichTextFormField
from .models import EmailTemplate
from .forms import EmailTemplateAdminForm
from django.contrib import admin
from django.http import HttpResponse





# Register your models here.

admin.site.register(Ministry)

admin.site.register(Event)

admin.site.register(Leadership)




class MinistryCardInline(admin.TabularInline):
    model = MinistryCard
    extra = 1
    fields = ('title', 'image', 'age_group', 'meeting_time', 'description', 'button_text', 'order')
    readonly_fields = ('order',)
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 4, 'cols': 40})},
    }


    

@admin.register(MinistryCardCategory)
class MinistryCardCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    inlines = [MinistryCardInline]
    prepopulated_fields = {'slug': ('name',)}

@admin.register(MinistryCard)
class MinistryCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'age_group', 'meeting_time', 'order')
    list_filter = ('category',)
    list_editable = ('age_group', 'meeting_time', 'order')
    fieldsets = (
        (None, {
            'fields': ('category', 'title', 'image', 'order')
        }),
        ('Details', {
            'fields': ('age_group', 'meeting_time', 'description', 'button_text'),
            'classes': ('wide',),
        }),
    )




admin.site.register(Sermon)







class EmailTemplateAdmin(admin.ModelAdmin):
    form = EmailTemplateAdminForm
    list_display = ('subject',)
    filter_horizontal = ('recipients',)  
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        subject = obj.subject
        html_message = obj.message
        recipients = [subscriber.email for subscriber in obj.recipients.all()]
        
        if recipients:  
            send_mail(
                subject,
                "",  
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=False,
                html_message=html_message
            )

admin.site.register(EmailTemplate, EmailTemplateAdmin)

admin.site.register(Subscriber)




