from django.db import models
from django.conf import settings


class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.IntegerField(null=True)

    def __str__(self):
        return f'Profile for user {self.user.username}'


class Stock(models.Model):
    id = models.AutoField(primary_key=True)
    symbol = models.CharField(max_length=30, unique=True)
    ticker = models.CharField(max_length=3, unique=True)
    industry = models.CharField(max_length=30)
    rating = models.CharField(max_length=4, default='None')
    index = models.CharField(max_length=30)
    summary = models.TextField(default='additional info about company')

    def __str__(self):
        return self.symbol


class TradeHistory(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    stock = models.ForeignKey(Stock, null=True, on_delete=models.SET_NULL)
    date_time = models.DateTimeField()
    name = models.CharField(max_length=30)
    site = models.CharField(max_length=1)
    num_of_share = models.IntegerField()
    stock_price = models.FloatField()
    value = models.FloatField()

    def __str__(self):
        return self.name


class StockPrice(models.Model):
    id = models.AutoField(primary_key=True)
    stock = models.ForeignKey(Stock, null=True, on_delete=models.SET_NULL)
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.IntegerField()

    def __str__(self):
        return str(self.stock)
