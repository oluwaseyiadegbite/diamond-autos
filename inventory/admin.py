from django.contrib import admin

from .models import Expense, Vehicle


class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("registration", "make", "model", "status", "archived")
    search_fields = ("registration", "make", "model")
    inlines = [ExpenseInline]
