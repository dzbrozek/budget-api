import decimal
from typing import List, Optional, cast

from budgets.models import Budget, Category, Transaction, TransactionType
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from rest_framework import serializers
from stempel import StempelStemmer


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

    @transaction.atomic
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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name')
        model = Category


class TransactionSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    category = CategorySerializer()

    class Meta:
        model = Transaction
        fields = ('id', 'creator', 'amount', 'title', 'created_at', 'type', 'category')


class TransactionSerializerMixin(serializers.ModelSerializer):
    def validate_amount(self, value: decimal.Decimal) -> decimal.Decimal:
        if value <= 0:
            raise serializers.ValidationError('Amount must be positive.')
        return value


stemmer = None


def text_stemming(text: str) -> List[str]:
    global stemmer

    if stemmer is None:
        stemmer = StempelStemmer.polimorf()

    stems = []
    for word in text.split():
        stems.append(stemmer.stem(word))

    return stems


def categorize_title(title: str) -> Optional[Category]:
    categories = Category.objects.all()
    for category in categories:
        category_tags = set(category.tags)
        title_tags = set(text_stemming(title))

        if category_tags & title_tags:
            return category
    return None


class TransferSerializer(TransactionSerializerMixin):
    creator = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'creator', 'amount', 'title', 'created_at', 'type', 'category')
        read_only_fields = ('created_at', 'type')
        extra_kwargs = {'title': {'required': True}}

    @transaction.atomic
    def create(self, validated_data: dict) -> Transaction:
        budget = self.context['budget']
        budget.balance = F('balance') + validated_data['amount']
        budget.save()
        category = categorize_title(validated_data['title'])

        data = {
            **validated_data,
            'creator': self.context['request'].user,
            'budget': budget,
            'category': category,
            'type': TransactionType.TRANSFER,
        }
        return cast(Transaction, super().create(data))


class WithdrawalSerializer(TransactionSerializerMixin):
    creator = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'creator', 'amount', 'title', 'created_at', 'type', 'category')
        read_only_fields = ('created_at', 'type', 'title')

    @transaction.atomic
    def create(self, validated_data: dict) -> Transaction:
        budget = Budget.objects.filter(pk=self.context['budget'].pk).select_for_update().get()

        amount = validated_data['amount']

        if amount > budget.balance:
            raise serializers.ValidationError('Not enough funds in budget.')

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
