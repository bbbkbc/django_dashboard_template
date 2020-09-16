from import_export import resources
from .models import Stock, TradeHistory


class StockResource(resources.ModelResource):

    class Meta:
        model = Stock


class TradeHistoryResource(resources.ModelResource):

    class Meta:
        model = TradeHistory
        fields = ['id', 'date_time', 'name', 'site', 'num_of_share', 'stock_price', 'value']