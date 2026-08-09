from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label=_('نام'), max_length=150, required=True)
    last_name = forms.CharField(label=_('نام خانوادگی'), max_length=150, required=True)
    email = forms.EmailField(label=_('ایمیل'), required=True)
    student_id = forms.CharField(label=_('شماره دانشجویی'), max_length=20, required=True)
    phone = forms.CharField(label=_('شماره موبایل'), max_length=15, required=True)
    gender = forms.ChoiceField(
        label=_('بخش خوابگاه'),
        choices=User.Gender.choices,
        required=True
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'student_id', 'phone', 'gender', 'password1', 'password2'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('نام کاربری یا ایمیل')
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('رمز عبور')
        })


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'avatar')
        labels = {
            'first_name': _('نام'),
            'last_name': _('نام خانوادگی'),
            'email': _('ایمیل'),
            'phone': _('شماره موبایل'),
            'avatar': _('تصویر پروفایل'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'avatar':
                field.widget.attrs.update({'class': 'form-control'})
