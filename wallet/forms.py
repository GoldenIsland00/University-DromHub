from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


class ChargeForm(forms.Form):
    amount = forms.DecimalField(
        label=_('مبلغ (تومان)'),
        min_value=Decimal('10000'),
        max_digits=12,
        decimal_places=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('حداقل ۱۰,۰۰۰ تومان'),
            'step': 10000
        })
    )
