from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    order = dictionary.get(key)
    if order:
        return order.meal_item.name_fa
    return None
