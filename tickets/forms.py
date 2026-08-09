from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Ticket, TicketReply


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('subject', 'category', 'priority', 'description', 'attachment')
        labels = {
            'subject': _('موضوع'),
            'category': _('دسته‌بندی'),
            'priority': _('اولویت'),
            'description': _('توضیحات'),
            'attachment': _('پیوست (اختیاری)'),
        }
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control form-select'}),
            'priority': forms.Select(attrs={'class': 'form-control form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class TicketReplyForm(forms.ModelForm):
    class Meta:
        model = TicketReply
        fields = ('message',)
        labels = {'message': _('پیام')}
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('پاسخ خود را بنویسید...')
            }),
        }
