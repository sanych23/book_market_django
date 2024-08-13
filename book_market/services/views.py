from django.shortcuts import render
from django.db.models import Prefetch, Sum
from rest_framework.viewsets import ReadOnlyModelViewSet
from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


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
        response_data = {'result': response.data}
        response_data['total_amount'] = queryset.aggregate(total=Sum('price')).get('total ')
        response.data = response_data
        return response
