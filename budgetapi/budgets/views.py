from typing import cast

from budgets.filters import TransactionFilter
from budgets.models import Budget, Transaction
from budgets.serializers import (
    BudgetAddMemberSerializer,
    BudgetSerializer,
    TransactionSerializer,
    TransferSerializer,
    WithdrawalSerializer,
)
from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property
from rest_framework.generics import CreateAPIView, GenericAPIView, ListAPIView, RetrieveAPIView, get_object_or_404


class BudgetCreateAPIView(CreateAPIView):
    serializer_class = BudgetSerializer


class BudgetRetrieveAPIView(RetrieveAPIView):
    serializer_class = BudgetSerializer

    def get_queryset(self) -> models.QuerySet['Budget']:
        return Budget.objects.filter(members=cast(User, self.request.user)).select_related('creator')


class BudgetAddMemberAPIView(CreateAPIView):
    serializer_class = BudgetAddMemberSerializer

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context['budget'] = get_object_or_404(
            Budget.objects.filter(creator=cast(User, self.request.user)), pk=self.kwargs['pk']
        )
        return context


class BudgetAPIViewMixin(GenericAPIView):
    @cached_property
    def budget(self) -> Budget:
        return get_object_or_404(Budget.objects.filter(members=cast(User, self.request.user)), pk=self.kwargs['pk'])

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context['budget'] = self.budget
        return context


class TransactionListAPIView(ListAPIView, BudgetAPIViewMixin):
    serializer_class = TransactionSerializer
    filterset_class = TransactionFilter

    def get_queryset(self) -> models.QuerySet['Transaction']:
        return (
            Transaction.objects.filter(budget=self.budget).select_related('creator', 'category').order_by('-created_at')
        )


class TransferCreateAPIView(CreateAPIView, BudgetAPIViewMixin):
    serializer_class = TransferSerializer


class WithdrawalCreateAPIView(CreateAPIView, BudgetAPIViewMixin):
    serializer_class = WithdrawalSerializer
