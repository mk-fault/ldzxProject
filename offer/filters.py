from .models import OfferModel
from django_filters import rest_framework as filters

class OfferFilter(filters.FilterSet):
    type = filters.CharFilter(field_name='type__name',lookup_expr='icontains')
    class Meta:
        model = OfferModel
        fields = ['type']