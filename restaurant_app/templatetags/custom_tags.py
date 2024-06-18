from django import template

from restaurant_app.models.product import Product


register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='append_grams')
def append_grams(value, arg):
    if arg in ["Замороженные Пельмени", "Замороженные Хинкали"]:
        return f"{value} гр"
    return value

@register.filter
def get_product_name_heb(product_id):
    return Product.objects.get(id=product_id).product_name_heb

@register.filter
def get_product_name_rus(product_id):
    return Product.objects.get(id=product_id).product_name_rus

@register.filter
def total_price(order):
    return sum(item.product.product_price * item.quantity for item in order.order_items.all())

@register.filter
def pickup_total_price(cart):
    return sum(item.quantity * item.product.product_price for item in cart.cart_items.all())


@register.filter
def delivery_total_price(cart):
    return sum(item.quantity * item.product.product_price for item in cart.delivery_cart_items.all())

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def index(List, i):
    return List[int(i) - 1]

@register.filter
def translate_weekday(value):
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    russian_day_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    day_mapping = dict(zip(day_names, russian_day_names))
    return day_mapping.get(value, '')

@register.filter
def get_weekday_name(value):
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    try:
        return day_names[value - 2]
    except IndexError:
        return ""

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)