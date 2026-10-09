from decimal import Decimal

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from cafeteria.models import MealItem


def _style(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            continue
        field.widget.attrs.setdefault('class', 'form-control')


class MealItemForm(forms.ModelForm):
    class Meta:
        model = MealItem
        fields = ('name_fa', 'name_en', 'price', 'description', 'is_active')
        widgets = {'description': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)


class UserCreateForm(forms.ModelForm):
    """ساخت کاربر جدید با نقش دلخواه توسط مدیریت."""
    password1 = forms.CharField(label=_('رمز عبور'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('تکرار رمز عبور'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone',
                  'role', 'gender', 'student_id')

    def __init__(self, *args, acting_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.acting_user = acting_user
        _style(self)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['gender'].required = False
        self.fields['gender'].help_text = _('برای دانشجو و گارد (محدودسازی به بخش برادران/خواهران) استفاده می‌شود')
        self.fields['student_id'].required = False
        # فقط مدیر سیستم می‌تواند مدیر سیستم دیگری بسازد
        if not (acting_user and acting_user.is_admin_user):
            self.fields['role'].choices = [
                c for c in User.Role.choices if c[0] != User.Role.ADMIN
            ]

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        if role == User.Role.STUDENT:
            if not cleaned.get('student_id'):
                self.add_error('student_id', _('برای دانشجو شماره دانشجویی الزامی است.'))
            if not cleaned.get('gender'):
                self.add_error('gender', _('برای دانشجو بخش خوابگاه الزامی است.'))
        if role == User.Role.ADMIN and not (self.acting_user and self.acting_user.is_admin_user):
            self.add_error('role', _('شما اجازه ساخت مدیر سیستم را ندارید.'))
        p1, p2 = cleaned.get('password1'), cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', _('دو رمز عبور یکسان نیستند.'))
        elif p1:
            try:
                validate_password(p1)
            except forms.ValidationError as e:
                self.add_error('password1', e)
        return cleaned

    def clean_student_id(self):
        return self.cleaned_data.get('student_id') or None  # unique + null

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'role',
                  'gender', 'student_id', 'is_active')

    def __init__(self, *args, acting_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.acting_user = acting_user
        _style(self)
        self.fields['gender'].required = False
        self.fields['student_id'].required = False
        if not (acting_user and acting_user.is_admin_user):
            self.fields['role'].choices = [
                c for c in User.Role.choices if c[0] != User.Role.ADMIN
            ]

    def clean_student_id(self):
        return self.cleaned_data.get('student_id') or None

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('role') == User.Role.STUDENT and not cleaned.get('student_id'):
            self.add_error('student_id', _('برای دانشجو شماره دانشجویی الزامی است.'))
        return cleaned


class SetPasswordForm(forms.Form):
    password1 = forms.CharField(label=_('رمز جدید'), widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label=_('تکرار رمز'), widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = user

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get('password1'), cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', _('دو رمز عبور یکسان نیستند.'))
        elif p1:
            validate_password(p1, self.target)
        return cleaned


class WalletChargeForm(forms.Form):
    amount = forms.DecimalField(
        label=_('مبلغ (تومان)'), min_value=Decimal('1000'), max_digits=12, decimal_places=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 1000}),
    )
    description = forms.CharField(
        label=_('توضیحات'), max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
