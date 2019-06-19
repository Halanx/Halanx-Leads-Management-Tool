import django_filters
from django.db.models import Q

from leads.models import TenantLead, HouseOwnerLead


class LeadFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    phone_no = django_filters.CharFilter(field_name='phone_no', lookup_expr='icontains')
    source = django_filters.CharFilter(field_name='source__category__name', lookup_expr='exact')
    permanent_address = django_filters.CharFilter(field_name='permanent_address__complete_address',
                                                  lookup_expr='icontains')
    created_at = django_filters.CharFilter(field_name='created_at', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status__name', lookup_expr='exact')

    class Meta:
        fields = ('name', 'phone_no', 'source', 'permanent_address', 'created_at', 'status')
        abstract = True


class TenantLeadFilterSet(LeadFilterSet):
    preferred_location = django_filters.CharFilter(field_name='preferred_location__complete_address',
                                                   lookup_expr='icontains')
    space_type = django_filters.CharFilter(field_name='space_type', lookup_expr='icontains')
    space_subtype = django_filters.CharFilter(field_name='space_subtype', lookup_expr='icontains')

    class Meta:
        model = TenantLead
        fields = LeadFilterSet.Meta.fields + ('preferred_location', 'space_type', 'space_subtype')


class HouseOwnerLeadFilterSet(LeadFilterSet):
    house_address = django_filters.CharFilter(field_name='house_address', lookup_expr='icontains')
    house_type = django_filters.CharFilter(method='house_type_lookup', lookup_expr='icontains')
    bhk_count = django_filters.NumberFilter(field_name='bhk_count')

    class Meta:
        model = HouseOwnerLead
        fields = LeadFilterSet.Meta.fields + ('house_address', 'house_type', 'bhk_count')

    @staticmethod
    def house_type_lookup(queryset, name, value):
        return queryset.filter(
            Q(house_type__icontains=value) | Q(furnish_type__icontains=value))
