from django.shortcuts import render
from django.db.models import Prefetch, Sum
from rest_framework.viewsets import ReadOnlyModelViewSet
from book_market.settings import PRICE_CACHE_NAME
from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer
from django.core.cache import cache


# Create your views here.
class SuscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email'))
    )
    serializer_class = SubscriptionSerializer

    def list(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(self, *args, **kwargs)
        
        price_cache = cache.get(PRICE_CACHE_NAME)
        if price_cache:
            total_price = price_cache
        else:
            total_price = queryset.aggregate(total=Sum('price')).get('total ')
            cache.set(PRICE_CACHE_NAME, total_price, 60 * 60)
        response_data = {'result': response.data}
        response_data['total_amount'] = total_price
        response.data = response_data
        return response
