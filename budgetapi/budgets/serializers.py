import decimal
from typing import cast

from budgets.models import Budget, Transaction, TransactionType
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = (
            'id',
            'balance',
        )
        read_only_fields = ('balance',)

    def create(self, validated_data: dict) -> Budget:
        creator = self.context['request'].user
        data = {**validated_data, 'creator': creator}
        budget = super().create(data)
        budget.members.add(creator)
        return cast(Budget, budget)


class BudgetAddMemberSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    def create(self, validated_data: dict) -> Budget:
        budget = self.context['budget']

        budget.members.add(validated_data['user'])

        return cast(Budget, budget)


class TransactionSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'creator', 'amount', 'title', 'created_at', 'type')


class TransactionSerializerMixin(serializers.ModelSerializer):
    def validate_amount(self, value: decimal.Decimal) -> decimal.Decimal:
        if value <= 0:
            raise serializers.ValidationError('Amount must be positive.')
        return value


class TransferSerializer(TransactionSerializerMixin):
    class Meta:
        model = Transaction
        fields = ('id', 'amount', 'title', 'created_at', 'type')
        read_only_fields = ('created_at', 'type')
        extra_kwargs = {'title': {'required': True}}

    @transaction.atomic
    def create(self, validated_data: dict) -> Transaction:
        budget = self.context['budget']
        budget.balance = F('balance') + validated_data['amount']
        budget.save()

        data = {
            **validated_data,
            'creator': self.context['request'].user,
            'budget': budget,
            'type': TransactionType.TRANSFER,
        }
        return cast(Transaction, super().create(data))


class WithdrawalSerializer(TransactionSerializerMixin):
    class Meta:
        model = Transaction
        fields = ('id', 'amount', 'title', 'created_at', 'type')
        read_only_fields = ('created_at', 'type', 'title')

    @transaction.atomic
    def create(self, validated_data: dict) -> Transaction:
        budget = Budget.objects.filter(pk=self.context['budget'].pk).select_for_update().get()

        amount = validated_data['amount']

        if amount > budget.balance:
            raise serializers.ValidationError('Not enough founds in budget.')

        budget.balance = F('balance') - amount
        budget.save()

        data = {
            **validated_data,
            'creator': self.context['request'].user,
            'budget': budget,
            'type': TransactionType.WITHDRAWAL,
            'title': 'Withdrawal',
        }
        return cast(Transaction, super().create(data))
