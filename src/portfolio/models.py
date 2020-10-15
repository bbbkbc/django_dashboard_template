from django.db import models
from app.models import Stock, Profile


class Pnl(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    stock = models.ForeignKey(Stock, null=True, on_delete=models.SET_NULL, unique_for_date=True)
    pnl_live = models.FloatField()
    pnl_booked = models.FloatField()
    mkt_price = models.FloatField()
    position_value_at_open = models.FloatField()
    position_value_at_now = models.FloatField()
    num_of_share_live = models.IntegerField()
    num_of_share_realized = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return str(self.stock)
