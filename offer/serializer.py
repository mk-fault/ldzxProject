from rest_framework import serializers
from .models import OfferModel

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferModel
        fields = '__all__'