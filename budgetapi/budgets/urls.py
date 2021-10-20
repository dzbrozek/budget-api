# Routers provide an easy way of automatically determining the URL conf.
from budgets.views import (
    BudgetAddMemberAPIView,
    BudgetCreateAPIView,
    BudgetRetrieveAPIView,
    TransactionListAPIView,
    TransferCreateAPIView,
    WithdrawalCreateAPIView,
)
from django.urls import path

app_name = 'budgets'

urlpatterns = [
    path('', BudgetCreateAPIView.as_view(), name='create-budget'),
    path('<int:pk>/', BudgetRetrieveAPIView.as_view(), name='budget-details'),
    path('<int:pk>/members/', BudgetAddMemberAPIView.as_view(), name='add-member'),
    path('<int:pk>/transactions/', TransactionListAPIView.as_view(), name='transactions'),
    path('<int:pk>/transfers/', TransferCreateAPIView.as_view(), name='create-transfer'),
    path('<int:pk>/withdrawals/', WithdrawalCreateAPIView.as_view(), name='create-withdrawal'),
]
