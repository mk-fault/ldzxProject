from rest_framework import serializers

from .models import StudentModel
from utils import funcs

class StudentModelSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=18)
    student_id = serializers.CharField(max_length=20)
    class Meta:
        model = StudentModel
        fields = '__all__'
    
    def validate_id(self,value):
        try:
            StudentModel.objects.get(id=value)
        except:
            # if not funcs.validate_id_number(value):
            #     raise serializers.ValidationError(f"身份证{value}信息有误，请检查后重新填写")
            return value 

        raise serializers.ValidationError(f"身份证[{value}]已存在")
    
    def validate_admission_date(self,value):
        if value < 1945 or value > 2099:
            raise serializers.ValidationError("请输入正确的入学年份(1945~2099)")
        return value

    def validate_student_id(self,value):
        try:
            StudentModel.objects.get(student_id=value)
        except:
            if not value.isdigit():
                raise serializers.ValidationError(f"学号[{value}]格式有误，请检查后重新填写")
            return value
        raise serializers.ValidationError(f"学号[{value}]已存在")
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    
    
    
