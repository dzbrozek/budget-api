from django_filters import rest_framework as filters


class TransactionFilter(filters.FilterSet):
    created_at = filters.IsoDateTimeFromToRangeFilter(field_name='created_at')
