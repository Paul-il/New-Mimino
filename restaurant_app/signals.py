from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth.models import User
from .models.tables import TipDistribution
from .models.orders import Order, OrderItem

@receiver(post_save, sender=TipDistribution)
@receiver(post_save, sender=Order)
@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=TipDistribution)
@receiver(post_delete, sender=Order)
@receiver(post_delete, sender=OrderItem)
def update_cache(sender, instance, **kwargs):
    user_id = None

    if isinstance(instance, TipDistribution):
        user_id = instance.user.id
    elif isinstance(instance, Order):
        user_id = instance.created_by.id
    elif isinstance(instance, OrderItem):
        if instance.order:
            user_id = instance.order.created_by.id
        elif instance.waiter_order:
            user_id = instance.waiter_order.created_by.id

    if user_id:
        cache_key = f'user_summary_{user_id}'
        cache.delete(cache_key)
