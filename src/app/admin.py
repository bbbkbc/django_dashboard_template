from django.contrib import admin
from .models import Profile, Stock, TradeHistory
from import_export.admin import ImportExportModelAdmin


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'phone_number', 'email']


@admin.register(Stock)
class StockAdmin(ImportExportModelAdmin):
    pass


@admin.register(TradeHistory)
class TradeHistoryAdmin(ImportExportModelAdmin):
    pass
