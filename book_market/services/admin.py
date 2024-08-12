from django.contrib import admin
from services.models import Plan, Service, Subscription


# Register your models here.
admin.site.register(Service)
admin.site.register(Plan)
admin.site.register(Subscription)

