from budgets.models import Budget, Transaction
from django.contrib import admin


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'balance', 'created_at')
    search_fields = ('id',)
    raw_id_fields = ('creator', 'members')
    list_filter = ('created_at',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'budget', 'amount', 'title', 'type', 'created_at')
    search_fields = ('id', 'title')
    raw_id_fields = ('creator', 'budget')
    list_filter = ('created_at', 'type')
