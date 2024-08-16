from django.dispatch import receiver
from django.db.models.signals import post_delete
from book_market.settings import PRICE_CACHE_NAME
from services.models import Subscription
from django.core.cache import cache


@receiver(post_delete, sender=None)
def delete_cache_total_sum(*args, **kwargs):
    cache.delete(PRICE_CACHE_NAME)
