from django.db import models
from app.models import Stock


class Pnl(models.Model):
    id = models.AutoField(primary_key=True)
    stock = models.ForeignKey(Stock, null=True, on_delete=models.SET_NULL, unique_for_date=True)
    pnl_live = models.FloatField()
    pnl_booked = models.FloatField()
    mkt_price = models.FloatField()
    open_position = models.FloatField()
    value = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return str(self.stock)
