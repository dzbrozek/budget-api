import datetime

import pytz
from budgets.factories import TransactionFactory
from budgets.filters import TransactionFilter
from budgets.models import Transaction
from django.test import TestCase


class TransactionFilterTest(TestCase):
    def test_filter_created_at(self):
        TransactionFactory(created_at=datetime.datetime(2021, 5, 1, 12, 13, tzinfo=pytz.UTC))
        transaction = TransactionFactory(created_at=datetime.datetime(2021, 5, 5, 6, 30, tzinfo=pytz.UTC))
        TransactionFactory(created_at=datetime.datetime(2021, 5, 15, 16, 16, tzinfo=pytz.UTC))

        qs = Transaction.objects.all()

        after = datetime.datetime(2021, 5, 5, tzinfo=pytz.UTC)
        before = datetime.datetime(2021, 5, 10, tzinfo=pytz.UTC)

        filter = TransactionFilter({'created_at_after': after.isoformat(), 'created_at_before': before.isoformat()}, qs)

        self.assertEqual(len(filter.qs), 1)
        self.assertEqual(filter.qs.get(), transaction)
