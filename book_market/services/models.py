from django.db import models
from django.core.validators import MaxValueValidator
from clients.models import Client
from services.tasks import set_price


# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price
    
    def save(self, *args, **kwargs):
        if self.full_price != self.__full_price:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)

        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} - {self.full_price} u.e."


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full',),
        ('student', 'Student',),
        ('discount', 'Discount',),
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent
    
    def save(self, *args, **kwargs):
        if self.discount_percent != self.__discount_percent:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)

        return super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.plan_type} ({self.discount_percent}%) "


class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)

    # def save(self, *args, save_model=True, **kwargs):
    #     if save_model:
    #         set_price.delay(self.id)
    #     return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.client.user.username} - {self.service.name} ({self.plan.plan_type})"
