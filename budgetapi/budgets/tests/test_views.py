from budgets.factories import BudgetFactory, TransactionFactory, UserFactory
from budgets.models import Budget, Transaction
from budgets.serializers import BudgetSerializer, TransactionSerializer, TransferSerializer
from django.urls import reverse
from djangorestframework_camel_case.util import camelize
from rest_framework.test import APITestCase


class BudgetCreateAPIViewTest(APITestCase):
    def test_cannot_create_budget_as_unauthenticated_user(self):
        response = self.client.post(reverse('budgets:create-budget'))

        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_create_budget(self):
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.post(reverse('budgets:create-budget'))
        self.assertEqual(response.status_code, 201)
        budget = Budget.objects.get()
        self.assertDictEqual(response.json(), camelize(BudgetSerializer(budget).data))


class BudgetRetrieveAPIViewTest(APITestCase):
    def test_cannot_retrieve_budget_as_unauthenticated_user(self):
        budget = BudgetFactory()

        response = self.client.get(reverse('budgets:budget-details', kwargs=dict(pk=budget.pk)))
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_cannot_retrieve_someone_else_budget(self):
        budget = BudgetFactory()
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.get(reverse('budgets:budget-details', kwargs=dict(pk=budget.pk)))
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(response.json(), {'detail': 'Not found.'})

    def test_retrieve_budget(self):
        user = UserFactory()
        budget = BudgetFactory(creator=user, members=(user,))
        self.client.force_authenticate(user)

        response = self.client.get(reverse('budgets:budget-details', kwargs=dict(pk=budget.pk)))
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), camelize(BudgetSerializer(budget).data))


class BudgetAddMemberAPIViewTest(APITestCase):
    def test_cannot_add_new_member_to_budget_as_unauthenticated_user(self):
        user = UserFactory()
        budget = BudgetFactory()

        response = self.client.post(reverse('budgets:add-member', kwargs=dict(pk=budget.pk)), data=dict(user=user.pk))
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_cannot_add_new_member_to_someone_else_budget(self):
        budget = BudgetFactory()
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.post(reverse('budgets:add-member', kwargs=dict(pk=budget.pk)), data=dict(user=user.pk))
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(response.json(), {'detail': 'Not found.'})

    def test_budget_member_cannot_add_new_members(self):
        member, user = UserFactory.create_batch(2)
        budget = BudgetFactory(members=(member,))
        self.client.force_authenticate(member)

        response = self.client.post(reverse('budgets:add-member', kwargs=dict(pk=budget.pk)), data=dict(user=user.pk))
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(response.json(), {'detail': 'Not found.'})

    def test_add_member_to_budget(self):
        creator, member = UserFactory.create_batch(2)
        budget = BudgetFactory(creator=creator, members=(creator,))
        self.client.force_authenticate(creator)

        response = self.client.post(reverse('budgets:add-member', kwargs=dict(pk=budget.pk)), data=dict(user=member.pk))
        self.assertEqual(response.status_code, 201)
        self.assertDictEqual(response.json(), {})


class TransactionListAPIViewTest(APITestCase):
    def test_cannot_get_transaction_list_as_unauthenticated_user(self):
        budget = BudgetFactory()

        response = self.client.get(reverse('budgets:transactions', kwargs=dict(pk=budget.pk)))
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_cannot_get_transaction_list_from_someone_else_budget(self):
        budget = BudgetFactory()
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.get(reverse('budgets:transactions', kwargs=dict(pk=budget.pk)))
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(response.json(), {'detail': 'Not found.'})

    def test_get_transaction_list(self):
        member = UserFactory()
        budget = BudgetFactory(members=(member,))
        transaction = TransactionFactory(budget=budget, creator=member)
        TransactionFactory()
        self.client.force_authenticate(member)

        response = self.client.get(reverse('budgets:transactions', kwargs=dict(pk=budget.pk)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), camelize(TransactionSerializer([transaction], many=True).data))


class TransferCreateAPIViewTest(APITestCase):
    def test_cannot_create_transfer_as_unauthenticated_user(self):
        budget = BudgetFactory()

        response = self.client.post(
            reverse('budgets:create-transfer', kwargs=dict(pk=budget.pk)), data=dict(title='Debt', amount='12.50')
        )
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_cannot_create_transfer_to_someone_else_budget(self):
        budget = BudgetFactory()
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.post(
            reverse('budgets:create-transfer', kwargs=dict(pk=budget.pk)), data=dict(title='Debt', amount='12.50')
        )
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(response.json(), {'detail': 'Not found.'})

    def test_create_transfer(self):
        member = UserFactory()
        budget = BudgetFactory(members=(member,))
        self.client.force_authenticate(member)

        response = self.client.post(
            reverse('budgets:create-transfer', kwargs=dict(pk=budget.pk)), data=dict(title='Debt', amount='12.50')
        )
        self.assertEqual(response.status_code, 201)
        transaction = Transaction.objects.get(budget=budget)
        self.assertEqual(response.json(), camelize(TransferSerializer(transaction).data))


class WithdrawalCreateAPIViewTest(APITestCase):
    def test_cannot_create_withdrawal_as_unauthenticated_user(self):
        budget = BudgetFactory(balance='50')

        response = self.client.post(
            reverse('budgets:create-withdrawal', kwargs=dict(pk=budget.pk)), data=dict(amount='12.50')
        )
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_cannot_create_withdrawal_from_someone_else_budget(self):
        budget = BudgetFactory(balance='50')
        user = UserFactory()
        self.client.force_authenticate(user)

        response = self.client.post(
            reverse('budgets:create-withdrawal', kwargs=dict(pk=budget.pk)), data=dict(amount='12.50')
        )
        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(response.json(), {'detail': 'Not found.'})

    def test_create_withdrawal(self):
        member = UserFactory()
        budget = BudgetFactory(members=(member,), balance='50')
        self.client.force_authenticate(member)

        response = self.client.post(
            reverse('budgets:create-withdrawal', kwargs=dict(pk=budget.pk)), data=dict(amount='12.50')
        )
        self.assertEqual(response.status_code, 201)
        transaction = Transaction.objects.get(budget=budget)
        self.assertEqual(response.json(), camelize(TransferSerializer(transaction).data))
