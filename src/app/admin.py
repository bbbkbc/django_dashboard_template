from django.contrib import admin
from .models import Profile, Stock, TradeHistory, StockPrice
from import_export.admin import ImportExportModelAdmin


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number']


@admin.register(Stock)
class StockAdmin(ImportExportModelAdmin):
    pass


@admin.register(TradeHistory)
class TradeHistoryAdmin(ImportExportModelAdmin):
    pass


@admin.register(StockPrice)
class StockPrice(ImportExportModelAdmin):
    pass
