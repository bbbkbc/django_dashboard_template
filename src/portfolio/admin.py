from django.contrib import admin
from .models import Pnl


@admin.register(Pnl)
class Pnl(admin.ModelAdmin):
    pass
