import decimal

from budgets.factories import BudgetFactory, CategoryFactory, UserFactory
from budgets.models import TransactionType
from budgets.serializers import (
    BudgetAddMemberSerializer,
    BudgetSerializer,
    TransferSerializer,
    WithdrawalSerializer,
    categorize_title,
    text_stemming,
)
from django.http import HttpRequest
from django.test import TestCase
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail


class BudgetSerializerTest(TestCase):
    def test_create_budget(self):
        user = UserFactory()
        request = HttpRequest()
        request.user = user
        context = dict(request=request)
        serializer = BudgetSerializer(data={}, context=context)

        serializer.is_valid(raise_exception=True)

        budget = serializer.save()

        self.assertEqual(budget.creator, user)
        self.assertEqual(budget.balance, decimal.Decimal(0))
        self.assertEqual(list(budget.members.all()), [user])
        self.assertEqual(budget.balance, decimal.Decimal(0))


class BudgetAddMemberSerializerTest(TestCase):
    def test_empty_data(self):
        budget = BudgetFactory()

        serializer = BudgetAddMemberSerializer(data={}, context=dict(budget=budget))

        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(serializer.errors, {'user': [ErrorDetail(string='This field is required.', code='required')]})

    def test_add_member(self):
        creator, member = UserFactory.create_batch(2)

        budget = BudgetFactory(creator=creator, members=(creator,))

        self.assertEqual(list(budget.members.all()), [creator])

        serializer = BudgetAddMemberSerializer(data={'user': member.pk}, context=dict(budget=budget))
        serializer.is_valid(raise_exception=True)
        budget = serializer.save()

        self.assertEqual(list(budget.members.all().order_by('id')), [creator, member])


class TransferSerializerTest(TestCase):
    def test_empty_data(self):
        serializer = TransferSerializer(data={})

        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(
            serializer.errors,
            {
                'amount': [ErrorDetail(string='This field is required.', code='required')],
                'title': [ErrorDetail(string='This field is required.', code='required')],
            },
        )

    def test_negative_amount(self):
        serializer = TransferSerializer(data={'title': 'Debt', 'amount': '-100'})

        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(
            serializer.errors,
            {
                'amount': [ErrorDetail(string='Amount must be positive.', code='invalid')],
            },
        )

    def test_transfer_money_to_budget(self):
        education_category = CategoryFactory(name="edukacja", tags=['książka', 'podręcznik'])
        user = UserFactory()
        request = HttpRequest()
        request.user = user
        budget = BudgetFactory(balance=decimal.Decimal('10.30'))
        data = {'title': 'Oddaje pieniądze za książki', 'amount': '10.50'}
        serializer = TransferSerializer(data=data, context=dict(request=request, budget=budget))

        serializer.is_valid(raise_exception=True)

        transaction = serializer.save()
        budget.refresh_from_db()

        self.assertEqual(budget.balance, decimal.Decimal('20.80'))

        self.assertEqual(transaction.budget, budget)
        self.assertEqual(transaction.creator, user)
        self.assertEqual(transaction.type, TransactionType.TRANSFER)
        self.assertEqual(transaction.title, data['title'])
        self.assertEqual(transaction.amount, decimal.Decimal(data['amount']))
        self.assertEqual(transaction.category, education_category)
        self.assertEqual(transaction.current_balance, decimal.Decimal('20.80'))


class WithdrawalSerializerTest(TestCase):
    def test_empty_data(self):
        serializer = WithdrawalSerializer(data={})

        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(
            serializer.errors,
            {
                'amount': [ErrorDetail(string='This field is required.', code='required')],
            },
        )

    def test_negative_amount(self):
        serializer = WithdrawalSerializer(data={'amount': '-100'})

        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(
            serializer.errors,
            {
                'amount': [ErrorDetail(string='Amount must be positive.', code='invalid')],
            },
        )

    def test_withdraw_more_than_available(self):
        user = UserFactory()
        request = HttpRequest()
        request.user = user
        budget = BudgetFactory(balance=decimal.Decimal('10.30'))
        data = {'amount': '20.50'}
        serializer = WithdrawalSerializer(data=data, context=dict(request=request, budget=budget))

        serializer.is_valid(raise_exception=True)

        with self.assertRaises(serializers.ValidationError) as cm:
            serializer.save()
        self.assertEqual(cm.exception.detail, [ErrorDetail(string='Not enough funds in budget.', code='invalid')])

        budget.refresh_from_db()

        self.assertEqual(budget.balance, decimal.Decimal('10.30'))

    def test_withdraw_money_from_budget(self):
        user = UserFactory()
        request = HttpRequest()
        request.user = user
        budget = BudgetFactory(balance=decimal.Decimal('10.30'), creator=user)
        data = {'amount': '5.50'}
        serializer = WithdrawalSerializer(data=data, context=dict(request=request, budget=budget))

        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()
        budget.refresh_from_db()

        self.assertEqual(budget.balance, decimal.Decimal('4.80'))

        self.assertEqual(transaction.budget, budget)
        self.assertEqual(transaction.creator, user)
        self.assertEqual(transaction.type, TransactionType.WITHDRAWAL)
        self.assertEqual(transaction.title, 'Withdrawal')
        self.assertEqual(transaction.amount, decimal.Decimal(data['amount']))
        self.assertEqual(transaction.category, None)
        self.assertEqual(transaction.current_balance, decimal.Decimal('4.80'))


class CategorizeTitle(TestCase):
    def test_text_stemming(self):
        self.assertEqual(
            text_stemming('oddaję pieniądze za przejazd samochodem'),
            ['oddawać', 'pieniądz', 'za', 'przejazd', 'samochód'],
        )

    def test_categorize_title(self):
        transport_category = CategoryFactory(name="transport", tags=['bilet', 'przejazd'])
        education_category = CategoryFactory(name="edukacja", tags=['książka', 'podręcznik'])

        self.assertEqual(categorize_title('Oddaje pieniądze'), None)
        self.assertEqual(categorize_title('Oddaje pieniądze za ostatnie przejazdy samochodem'), transport_category)
        self.assertEqual(categorize_title('Oddaje pieniądze za książki'), education_category)
