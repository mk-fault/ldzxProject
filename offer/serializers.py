from rest_framework import serializers
from .models import OfferModel
from student.models import TypeModel

class OfferSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(queryset=TypeModel.objects.all(),slug_field='name',required=True)
    school = serializers.CharField(max_length=30,required=True)
    time = serializers.CharField(max_length=20,required=True)
    class Meta:
        model = OfferModel
        fields = '__all__'