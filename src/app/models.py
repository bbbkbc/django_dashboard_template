from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'Profile for user {self.user.username}'


class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    ticker = models.CharField(max_length=3)
    industry = models.CharField(max_length=30)
    rating = models.CharField(max_length=4, default='NONE')
    index = models.CharField(max_length=30)
    summary = models.TextField(default='additional info about company')

    def __str__(self):
        return self.name


class TradeHistory(models.Model):
    date_time = models.DateTimeField()
    name = models.CharField(max_length=30)
    site = models.CharField(max_length=1)
    num_of_share = models.IntegerField()
    stock_price = models.FloatField()
    value = models.FloatField()