from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """دیکشنری[کلید] داخل قالب؛ در نبود کلید None برمی‌گرداند."""
    if not dictionary:
        return None
    return dictionary.get(key)
