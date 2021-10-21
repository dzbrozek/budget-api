import datetime
from typing import List

import factory.fuzzy
from budgets.models import Budget, Category, Transaction, TransactionType
from django.contrib.auth.models import User
from faker import Faker

USER_PASSWORD = 'password'  # nosec


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'user-{n}')
    email = factory.Sequence(lambda n: f'user-{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', USER_PASSWORD)
    is_active = factory.Faker('pybool')

    class Meta:
        model = User
        django_get_or_create = ('username',)


class BudgetFactory(factory.django.DjangoModelFactory):
    creator = factory.SubFactory(UserFactory)
    balance = factory.fuzzy.FuzzyDecimal(low=0, high=100)

    class Meta:
        model = Budget

    @factory.post_generation
    def members(self, create: bool, extracted: List[User], **kwargs: dict) -> None:
        if not create:
            return

        if extracted:
            for user in extracted:
                self.members.add(user)


class CategoryFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText()
    tags = factory.LazyFunction(lambda: Faker().sentence().split())

    class Meta:
        model = Category


class TransactionFactory(factory.django.DjangoModelFactory):
    creator = factory.SubFactory(UserFactory)
    budget = factory.SubFactory(BudgetFactory)
    amount = factory.fuzzy.FuzzyDecimal(low=0.01, high=100)
    title = factory.fuzzy.FuzzyText()
    category = factory.SubFactory(CategoryFactory)
    type = factory.fuzzy.FuzzyChoice(choices=TransactionType.values)

    class Meta:
        model = Transaction

    @factory.post_generation
    def created_at(self, create: bool, created_at: datetime.datetime, **kwargs: dict) -> None:
        if not create:
            return

        if created_at:
            self.created_at = created_at
            self.save()
