from django.contrib import admin
from .models import Profile, Stock, TradeHistory
from import_export import resources
from import_export.admin import ImportExportModelAdmin


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth']


@admin.register(Stock)
class StockAdmin(ImportExportModelAdmin):
    pass


@admin.register(TradeHistory)
class TradeAdmin(ImportExportModelAdmin):
    pass


class StockResource(resources.ModelResource):

    class Meta:
        model = Stock


class TradeHistoryResource(resources.ModelResource):

    class Meta:
        model = TradeHistory
