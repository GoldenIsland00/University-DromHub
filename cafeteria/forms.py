from django import forms
from django.utils.translation import gettext_lazy as _


class MealOrderForm(forms.Form):
    """Dynamic form: one choice per day of the week."""
    def __init__(self, *args, menus=None, **kwargs):
        super().__init__(*args, **kwargs)
        if menus:
            for menu in menus:
                choices = [(item.pk, f"{item.name_fa} ({item.price:,} ت)") for item in menu.options.filter(is_active=True)]
                field_name = f'menu_{menu.pk}'
                self.fields[field_name] = forms.ChoiceField(
                    label=menu.get_weekday_display(),
                    choices=[('', '---')] + choices,
                    required=False,
                    widget=forms.Select(attrs={'class': 'form-control form-select'})
                )
