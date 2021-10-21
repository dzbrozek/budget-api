from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Budget(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    members = models.ManyToManyField(User, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Budget: {self.pk}'


class Category(models.Model):
    name = models.CharField(max_length=100)
    tags = ArrayField(models.CharField(max_length=100))

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self) -> str:
        return f'Category: {self.pk}'


class TransactionType(models.TextChoices):
    TRANSFER = 'TRANSFER', 'Transfer'
    WITHDRAWAL = 'WITHDRAWAL', 'Withdrawal'


class Transaction(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, help_text='Budget balance after transaction')

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gt=Decimal('0')), name='transaction_amount_positive'),
        ]

    def __str__(self) -> str:
        return f'Transaction: {self.pk}'
